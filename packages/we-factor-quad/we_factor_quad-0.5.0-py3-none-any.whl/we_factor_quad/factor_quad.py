import os.path
import pathlib as pl
import pickle
from typing import Dict, AnyStr, List
import numpy as np
import pandas as pd
from we_factor_quad.data_api import wiser_download_em_result


# CODE_COL_NAME = 'code'
# TIME_COL_NAME = 'date'


class FactorQuad(object):
    """
    一个提取因子组的数据四元组的基本模块，可以用于用户端部署，包含一些常用的数据提取展示，以及协方差矩阵计算的方法
    1. 导出数据：从数据库中导出数据，是后续分析的基础
    2. 导出并整理数据：能够将Quad 数据重组，形成指定的更加清晰的格式，方便我们整理其他的计算，也是一切的基础
    3. 导入数据：这应该是一个连接器，能够将其他数据（比如 excel 格式等）转化为对应的数据库格式，并上传到数据库
    4. 导入并整理数据：如果原始数据不满足特定的格式，可以扩展一批额外的格式，能够进行匹配导入
    5. 数据展示：展示factor vol, idio variance
    6. 在有Quad数据的基础上，输入任意 portfolio, 计算该组合的volatility，展示volatility

    # TODO: 后续提升
    # TODO: 1) 要注意提升内存管理优化：现在峰值10年monthly data峰值内存使用大概在10GB，但是绝大多数内存使用只有2GB；
    # TODO: 2) 要把数据加载的部分拆成一个四元组的data api，local cache的部分用seaDrive相关技术代替
    # TODO: 3) 使用亚楠的介绍的多核计算技术　Dask
    # TODO: 4) 后期拓展多个factor_quad联合运算（MSG)
    # TODO: 5) save .pkl好像特别慢
    # 可能需要借助多核计算。 猜测是数据库索引的问题
    """

    def __init__(self,
                 factor_system: str,
                 raw_data: Dict,
                 _code_col_name: str = "code",
                 _time_col_name: str = "date"):
        """
        不建议直接失踪，建议使用create_factor_quad
        :param factor_system:
        :param raw_data:
        """
        self._code_col_name = _code_col_name
        self._time_col_name = _time_col_name

        self.factor_system = factor_system  # 对应case数据；一个字符串说明的字符系统，这个系统会导入对应的数据
        # todo 应该先assert 一下，保证结果是一致的
        needed_dfs = ['characteristic_exposure',
                      'characteristic_covariance',
                      'characteristic_idiosyncratic_variance',
                      'characteristic_scale']
        for dfn in needed_dfs:  # 必须至少要有4个数据库； todo: 似乎  characteristic_scale 表允许是空的
            assert dfn in raw_data.keys(), f"{dfn} not found in raw data!"

        # 1.1 Store covariance as dictionary
        self.sigma_ts = self.type_date_col(raw_data['characteristic_covariance'])

        # 1.2 Store beta
        self.beta_ts = self.type_date_col(raw_data['characteristic_exposure'])

        # 1.3 Store psi
        self.psi_ts = self.type_date_col(raw_data['characteristic_idiosyncratic_variance'])

        # 1.4 Store scale

        if raw_data['characteristic_scale'].empty:
            self.scale_ts = (self.psi_ts.set_index([self._time_col_name, self._code_col_name])['var'] * 0.0 + 1.0) \
                .reset_index().rename(columns={'var': 'scale'})
        else:
            self.scale_ts = self.type_date_col(raw_data['characteristic_scale']) \
                .dropna(subset=['scale'], axis=0)

        self.scale_ts = self.scale_ts.drop_duplicates([self._time_col_name, self._code_col_name], ignore_index=True)
        self.date_list = np.unique(self.scale_ts[self._time_col_name])

        # Reindex everything to be consistent with scale
        index_time_code = self.scale_ts.set_index([self._time_col_name, self._code_col_name]).index

        # TODO Zeyu: what if psi is missing? it shouldn't. But it should be handled with shrinkage,
        #  should we fill with XS average?
        self.psi_ts = self.psi_ts.drop_duplicates([self._time_col_name, self._code_col_name], ignore_index=True)
        self.psi_ts = self.psi_ts.set_index([self._time_col_name, self._code_col_name]) \
            .reindex(index=index_time_code).reset_index()

        # Reshape sigma
        self.sigma_ts = self.sigma_ts.filter([self._time_col_name, 'source', 'target', 'cov'])
        self.sigma_ts = self.sigma_ts.drop_duplicates([self._time_col_name, 'source', 'target'], ignore_index=True)

        # Add a filler step to be robust (in case sigma is only specified via upper/lower triangle)
        sigma_ts_filler = self.sigma_ts.rename(columns={'source': 'target', 'target': 'source'})
        self.sigma_ts = self.sigma_ts.set_index([self._time_col_name, 'source', 'target'])['cov']
        self.sigma_ts = self.sigma_ts.combine_first(sigma_ts_filler
                                                    .set_index([self._time_col_name, 'source', 'target'])['cov'])
        self.sigma_ts = self.sigma_ts.unstack().reset_index()

        # self.sigma_ts = self.sigma_ts.set_index([TIME_COL_NAME]).reindex(index=self.date_list).reset_index()

        # Fill missing cov elements with 0
        self.sigma_ts = self.sigma_ts.set_index([self._time_col_name, 'source']).unstack().fillna(0.0).stack()
        cols_beta = self.sigma_ts.columns
        self.sigma_ts = self.sigma_ts.reset_index()
        # Check all the factors are there
        missing_factors = [i for i in np.unique(self.beta_ts['characteristic'])
                           if i not in ([self._time_col_name, self._code_col_name] + list(self.sigma_ts.columns))]

        for date in list(set(self.beta_ts[self._time_col_name])):
            if '2021-07-29' < str(date)[:10] < '2021-08-05':
                beta_ts = self.beta_ts[self.beta_ts[self._time_col_name] == date]
                sigma_ts = self.sigma_ts[self.sigma_ts['date'] == date]
                self.beta_ts = self.beta_ts.drop(beta_ts[~beta_ts.characteristic.isin(set(sigma_ts.source))].index)

        if len(missing_factors) > 0:
            beta_lst = []
            for date in list(set(self.beta_ts[self._time_col_name])):
                beta_t = self.beta_ts[self.beta_ts[self._time_col_name] == date]
                zero_factors = beta_t.groupby('characteristic').sum()
                missing_factors = zero_factors[zero_factors == 0].dropna().index
                beta_ts = beta_t[~beta_t['characteristic'].isin(missing_factors)]
                beta_lst.append(beta_ts)
            self.beta_ts = pd.concat(beta_lst)
            missing_factors = [i for i in np.unique(self.beta_ts['characteristic'])
                               if i not in ([self._time_col_name, self._code_col_name] + list(self.sigma_ts.columns))]
            assert len(missing_factors) == 0, "Factors %s missing from cov!" % ",".join(missing_factors)

        # Fill missing betas with 0s
        self.beta_ts = self.beta_ts.drop_duplicates([self._time_col_name, self._code_col_name, 'characteristic'],
                                                    ignore_index=True)
        self.beta_ts = self.beta_ts.set_index([self._time_col_name, self._code_col_name, 'characteristic'])['exposure'] \
            .unstack().reindex(index=index_time_code, columns=cols_beta) \
            .fillna(0.0).reset_index()

        if self.beta_ts.code[0][:2] == 'CN':  # todo 这一段请速速升级Barra之后删除
            standard_code = []
            for i in self.beta_ts.code:
                if i[2] == '6':
                    tail = '.SH'
                elif i[2] == '8':
                    tail = '.BJ'
                else:
                    tail = '.SZ'
                standard_code.append(i[2:] + tail)
            self.beta_ts.code = standard_code
        if self.psi_ts.code[0][:2] == 'CN':  # todo 这一段请速速升级Barra之后删除
            standard_code = []
            for i in self.psi_ts.code:
                if i[2] == '6':
                    tail = '.SH'
                elif i[2] == '8':
                    tail = '.BJ'
                else:
                    tail = '.SZ'
                standard_code.append(i[2:] + tail)
            self.psi_ts.code = standard_code
        if self.scale_ts.code[0][:2] == 'CN':  # todo 这一段请速速升级Barra之后删除
            standard_code = []
            for i in self.scale_ts.code:
                if i[2] == '6':
                    tail = '.SH'
                elif i[2] == '8':
                    tail = '.BJ'
                else:
                    tail = '.SZ'
                standard_code.append(i[2:] + tail)
            self.scale_ts.code = standard_code

        # 基本维度信息
        self.assets_n = self.beta_ts[self._code_col_name].drop_duplicates().shape[0]
        self.factors_m = cols_beta.shape[0]
        self.period_t = 1  # 多少天的数据
        # 填充psi中无法处理的缺失
        # self.psi_ts['var'] = self.psi_ts['var'].fillna(0)
        # After this cleanup, we expect:
        # 1) scale, beta, psi to cover same universe and time periods
        # 2) sigma has all the factors and their respective cov (filled with 0 if
        # factor only available after a certain date)
        pass

    def info(self, label: str = None):
        """
        自我表示一下自身的基本统计特征，对于factor quad而言，需要展示其主要特征包括
        :param label:
        :return:
        """
        if label is not None:
            print("=" * 8 + label + "=" * 8)
        print("assets_n, factors_m, period_t:", (self.assets_n, self.factors_m, self.period_t))

    @staticmethod
    def create_factor_quad(factor_system: str,
                           start_date: str,
                           end_date: str,
                           from_src: int = 1,
                           local_path: str = None) -> "FactorQuad":
        """
        创建一个因子四要素数据结构;
        :param factor_system: 因子系统的名称，对应于数据库中的 case 名称
        :param start_date: 8 digits格式 日期
        :param end_date:
        :param from_src: 0 表示从网络sql提取数据，1表示从sea_drive提取数据，2表示从本地提取数据（2需要对应一个pkl文件）
        :param local_path: 当from_src == 2时，需要一个pkl文件；0表示remote，1表示 seadrive，所以默认为1；
        :return:
        """
        raw_data = FactorQuad.factor_quads_download(factor_system=factor_system,
                                                    start_date=start_date,
                                                    end_date=end_date,
                                                    from_src=from_src,
                                                    local_path=local_path)
        return FactorQuad(factor_system, raw_data=raw_data)

    ##########################################
    # Getters
    ##########################################
    def get_sigma(self, t: str, drop_time: bool = True) -> pd.DataFrame:
        """
        提取指定时间的因子协方差矩阵（DF）
        :param t: 时间,8 digit 格式'20210101'
        :param drop_time: 是否去掉多余的列，只保留协方差矩阵
        :return: drop_time=True时，返回的是一个方阵，协方差矩阵
        """
        if drop_time:  # 只保留协方差矩阵格式
            sigma_t = self.sigma_ts[self.sigma_ts[self._time_col_name] == t] \
                .drop(labels=[self._time_col_name], axis=1).set_index('source')
            return sigma_t  # 方阵
        else:
            return self.sigma_ts[self.sigma_ts[self._time_col_name] == t]

    def get_sigma_and_corr(self, t: str, drop_time: bool = True) -> (pd.DataFrame, pd.DataFrame):
        """
        从接口设计的角度，宁愿写两个函数，也应该标准化，对于这种非常常用的函数，必须要明确知道输入输出
        :param t:
        :param drop_time:
        :return: 2 objs, cov_vector & corr_mat
        """
        sigma_t = self.sigma_ts[self.sigma_ts[self._time_col_name] == t] \
            .drop(labels=[self._time_col_name], axis=1).set_index('source')
        sigma_vec, corr_mat = decompose_vcv(sigma_t)  # 返回2个对象, 将协方差矩阵分解为协方差向量 + 相关性矩阵
        if drop_time:  # 只保留协方差矩阵格式
            return pd.DataFrame(sigma_vec), corr_mat
        else:
            sigma_vec = sigma_vec.reset_index()
            sigma_vec.columns = ["source", "value"]
            sigma_vec.insert(loc=0, column=self._time_col_name, value=t)
            corr_mat = corr_mat.reset_index()
            corr_mat.insert(loc=0, column=self._time_col_name, value=t)
            return sigma_vec, corr_mat

    def get_beta(self, t: str, drop_time: bool = True) -> pd.DataFrame:
        """
        提取指定时间的因子曝露
        :param t: 时间：'20210101'
        :param drop_time:
        :return: beta 矩阵
        """
        if drop_time:
            return self.beta_ts[self.beta_ts[self._time_col_name] == t].drop(labels=[self._time_col_name],
                                                                             axis=1).set_index('code')
        else:
            return self.beta_ts[self.beta_ts[self._time_col_name] == t]

    def get_scale(self, t: str, drop_time: bool = True) -> pd.DataFrame:
        """
        提取指定时间的异方差调整
        :param t: 时间：'20210101'
        :param drop_time: if True, drop time column
        :return:
        """
        if drop_time:
            return self.scale_ts[self.scale_ts[self._time_col_name] == t].drop(labels=[self._time_col_name],
                                                                               axis=1).set_index(
                'code')
        else:
            return self.scale_ts[self.scale_ts[self._time_col_name] == t]

    def get_psi(self, t: str, drop_time: bool = True) -> pd.DataFrame:
        """
        提取指定时间的特异性风险（idio variance)
        :param t: 时间：'20210101'
        :param drop_time: 是否排除掉日期
        :return:
        """
        if drop_time:
            return self.psi_ts.loc[self.psi_ts[self._time_col_name] == t, [self._time_col_name, "code", "var"]].drop(
                labels=[self._time_col_name], axis=1).set_index('code')
        else:
            return self.psi_ts.loc[self.psi_ts[self._time_col_name] == t, [self._time_col_name, "code", "var"]]

    def get_factor_vol(self) -> pd.DataFrame:
        """
        提取所有因子的波动率时序；
        M天对应M行；N个因子对应M列，形成一个 M * N的矩阵
        :return: 所有，因子的波动率的时间序列
        """
        sigma_ts_tmp = self.sigma_ts.set_index(['date', 'source']).stack().reset_index()
        idx = (sigma_ts_tmp['target'] == sigma_ts_tmp['source'])
        vol = np.sqrt(sigma_ts_tmp.loc[idx, :].pivot(index=self._time_col_name, columns='target',
                                                     values=0))
        return vol

    def get_factor_corr(self, fac1: str, fac2: str):
        """
        Compute time series of correlation for two factors
        todo ZX 为什么不用矩阵的计算方法，还要设计一个 one-to-one 的因子相关性计算方式: 主要为了方便查看time series
        :param fac1:
        :param fac2:
        :return:
        """
        sigma_ts_tmp = self.sigma_ts.set_index(['date', 'source']).stack().reset_index()
        idx_1 = (sigma_ts_tmp['target'] == fac1) & (sigma_ts_tmp['source'] == fac1)
        idx_2 = (sigma_ts_tmp['target'] == fac2) & (sigma_ts_tmp['source'] == fac2)
        idx_3 = (sigma_ts_tmp['target'] == fac1) & (sigma_ts_tmp['source'] == fac2)

        cov = sigma_ts_tmp.loc[idx_3, :].drop(labels=['target', 'source'], axis=1) \
            .set_index(self._time_col_name)

        v1 = sigma_ts_tmp.loc[idx_1, :].drop(labels=['target', 'source'], axis=1) \
            .set_index(self._time_col_name)

        v2 = sigma_ts_tmp.loc[idx_2, :].drop(labels=['target', 'source'], axis=1) \
            .set_index(self._time_col_name)
        return cov / np.sqrt(v1 * v2)

    def get_ivar(self) -> pd.Series:
        """
        提取所有资产的idiosyncratic variance时间序列，完整的时间序列
        :return: 一个二级index的Series，第一级index为时间，第二级index为 code；一般使用时需要unstack以实现窄表转宽表
        """
        ivar = self.psi_ts.set_index([self._time_col_name, self._code_col_name])['var'] \
               / (self.scale_ts.set_index([self._time_col_name, self._code_col_name])['scale']) ** 2
        return ivar

    ##########################################
    # Portfolio exposures / ivar
    ##########################################
    def get_ptfl_beta(self, ptfl_w: pd.DataFrame) -> pd.DataFrame:
        """
        Compute factor exposure of a given portfolio，portfolio对应的数据结构是 weights
        :param ptfl_w: Dataframe: T x N (panel of weights)
        :return: portfolio （weight） 的 beta 的 TS, 给所有时间都乘上去
        """

        return self.beta_ts.set_index([self._time_col_name, self._code_col_name]) \
            .mul(ptfl_w.stack(), axis=0).reset_index() \
            .drop(labels=[self._code_col_name], axis=1).groupby(by=self._time_col_name).sum()

    def get_ptfl_ivar(self, ptfl_w: pd.DataFrame) -> pd.DataFrame:
        """
        提取一个portfolio的idiosyncratic variance时序
        :param ptfl_w: Dataframe: T x N (panel of weights)
        :return: portfolio的风险，有因子解释的部分，也有因子不能解释的部分
        """
        ivar = self.get_ivar()
        return (ivar * (ptfl_w.stack() ** 2)).reset_index() \
            .groupby(by=self._time_col_name)[0].sum()

    def get_systematic_cov(self, beta_exposure: pd.DataFrame) -> pd.DataFrame:
        """
        Compute cov systematic risk
        :param beta_exposure: Dataframe: wide panel, time, asset_col, factors (e.g. self.beta_ts)
        :param asset_col: name of asset column
        :return: a time series of cov across all the assets
        """
        # TODO Yanan / Zeyu: to speed up (use Dask)??
        return beta_exposure \
            .groupby(by=self._time_col_name, axis=0, as_index=True, group_keys=True) \
            .apply(lambda x: x.set_index([self._code_col_name]).drop(self._time_col_name, axis=1)
                   .dot(self.get_sigma(x[self._time_col_name].iloc[0], drop_time=True))
                   .dot(x.set_index([self._code_col_name]).drop(self._time_col_name, axis=1).T)) \
            .reset_index()

    def get_systematic_var(self, beta_exposure: pd.DataFrame) -> pd.DataFrame:
        """
        Compute systematic variance for the assets
        :param beta_exposure: Dataframe: wide panel, time, asset_col, factors (e.g. self.beta_ts)
        :param asset_col: name of asset column
        :return: a time series of variance for all the assets; 二级index，第一级为时间，第二级为code；可以unstack窄表转宽表
        """
        return beta_exposure \
            .groupby(by=self._time_col_name, axis=0, as_index=True, group_keys=True) \
            .apply(lambda x: pd.DataFrame(np.diag(x.drop([self._time_col_name, self._code_col_name], axis=1)
                                                  .dot(self.get_sigma(x[self._time_col_name].iloc[0], drop_time=True))
                                                  .dot(x.drop([self._time_col_name, self._code_col_name], axis=1).T)),
                                          index=x[self._code_col_name])[0])

    def compute_ptfl_var(self, ptfl_w: pd.DataFrame) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
        """
        Compute the volatility time series for a given portfolio
        :param ptfl_w: Dataframe: T x N (panel of weights)
        :return: 3 objs
        """
        name = 'ptfl_tmp'
        beta_exposure = self.get_ptfl_beta(ptfl_w=ptfl_w).reset_index()
        beta_exposure[self._code_col_name] = name

        sys_var = self.get_systematic_var(beta_exposure)[name]
        idio_var = self.get_ptfl_ivar(ptfl_w)
        return sys_var + idio_var, sys_var, idio_var

    ##########################################
    # Formatting and cleanup
    ##########################################

    def type_date_col(self, df: pd.DataFrame, shift: bool = False) -> pd.DataFrame:
        """
        Convert format of date column to python datetime
        :param df:
        :param shift:
        :return:
        """
        from pandas.tseries.offsets import BDay  # 按照 Business Day 来移动
        df.columns = [i.lower() for i in df.columns]
        df.loc[:, self._time_col_name] = pd.to_datetime(df.loc[:, self._time_col_name].astype(str))
        df.loc[:, self._time_col_name] = df.loc[:, self._time_col_name] + BDay() - BDay()
        if shift:
            df.loc[:, self._time_col_name] = df.loc[:, self._time_col_name] + 5 * BDay()
        return df

    @staticmethod
    def factor_quads_upload():
        """
        能够将指定数据，按照特定格式，上传到数据库指定位置
        Returns:
        """
        # TODO: Ziping sanity check, confrom data, upload to wiserdata
        pass

    @staticmethod
    def factor_quads_download(factor_system: str, start_date: str, end_date: str,
                              universe: List = [],
                              from_src: int = 1,
                              local_path=None) -> Dict:
        """
        根据要模拟的factor的名称（类别），提取对应的因子四元组数据
        实际需要 Sigma_f, beta_t, scale用于调整beta，Psi
        params local_path: 本地临时文件
        params from_src: from which source， 0表示网络sql，1表示sea_drive, 2表示 local path
        params local_path: if from_src == 1, we need a local path
        Returns: 结果应该是4个对象组成的dict
        """
        which_objs = [
            "characteristic_exposure",
            "characteristic_covariance",
            "characteristic_idiosyncratic_variance",
            "characteristic_scale"]

        if from_src == 2:  # 从本地导入数据
            assert local_path is not None, "If select from_src = 2 use local pickle file, you must input local path!"
            assert local_path[-4:] == ".pkl", "local path is not a pkl file!"
            raw_data_dic = FactorQuad.load_obj(local_path)

        # 接收csv文件生成四元组,需要local_path参数指示日期文件夹的上层文件夹的位置，比如现在的
        elif from_src == 3:
            path_for_dates = os.path.join(local_path, factor_system)
            repo_list = sorted(os.listdir(path_for_dates))
            index_end = repo_list.index(end_date)
            index_start = repo_list.index(start_date)
            required_repo_list = repo_list[index_start: index_end + 1]
            required_path_list = [os.path.join(path_for_dates, x) for x in required_repo_list]
            raw_data_list = [pd.DataFrame([])] * len(which_objs)
            raw_data_dict = dict(zip(which_objs, raw_data_list))
            for date_path in required_path_list:
                for data_name in which_objs:
                    data_path = f"{os.path.join(date_path, data_name)}.csv"
                    data_ = pd.read_csv(data_path, index_col=0)
                    data_['case'] = factor_system
                    data_.columns = [x.lower() for x in data_.columns]
                    raw_data_dict[data_name] = pd.concat([raw_data_dict[data_name], data_])
            for key in raw_data_dict.keys():
                if key == 'characteristic_exposure':
                    raw_data_dict[key] = raw_data_dict[key][["case", "date", 'characteristic',
                                                             'exposure', 'code', "type"]]
                elif key == "characteristic_covariance":
                    raw_data_dict[key] = raw_data_dict[key][["case", "date", 'source',
                                                             'target', 'cov']]
                elif key == 'characteristic_idiosyncratic_variance':
                    raw_data_dict[key] = raw_data_dict[key][["case", "date", 'code', 'var']]
                elif key == 'characteristic_scale':
                    raw_data_dict[key] = raw_data_dict[key][["case", "date", 'code', 'scale']]
                else:
                    raise ValueError(f"{key} is not a valid raw data name..."
                                     f"it must be characteristic_idiosyncratic_variance, "
                                     f"characteristic_exposure, characteristic_covariance, or characteristic_scale")

            return raw_data_dict


        else:  # 0 remote, 1 sea_drive， 不是从本地下载数据
            # which_objs = [
            #     "characteristic_exposure",
            #     "characteristic_covariance",
            #     "characteristic_idiosyncratic_variance",
            #     "characteristic_scale"]
            raw_data_dic = {}
            if from_src == 1:  # 从sea_drive 下载数据
                assert local_path is not None, "local_path (seadrive path) should not be None!"
                for x in which_objs:
                    raw_data_dic[x] = wiser_download_em_result(case_name=factor_system,
                                                               which=x,
                                                               start_date=str(start_date),
                                                               end_date=str(end_date),
                                                               universe=universe, mode="local",
                                                               seadrive_localpath=local_path)
            elif from_src == 0:  # 从remote origin 下载数据
                for x in which_objs:
                    raw_data_dic[x] = wiser_download_em_result(case_name=factor_system,
                                                               which=x,
                                                               start_date=str(start_date),
                                                               end_date=str(end_date),
                                                               universe=universe, mode="remote")
            else:
                raise ValueError("from_src not in [0, 1, 2]")
            # FactorQuad.save_obj(raw_data_dic, path=local_path)  # 在本地保存一份pkl文件
        return raw_data_dic

    def save_obj(self, path: AnyStr):
        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, path)
        if path[-4:] != ".pkl":
            path = path + ".pkl"
        path = open(path, "wb")
        pickle.dump(self, path)

    def save_to_csv(self, dir: AnyStr = None):
        """
        将seadrive中的四元组数据保存成csv文件
        """

        if dir is None:
            dir = os.path.dirname(__file__)
        self.sigma_ts.to_csv(os.path.join(dir, "characteristic_covariance.csv"))
        self.beta_ts.to_csv(os.path.join(dir, "characteristic_exposure.csv"))
        self.psi_ts.to_csv(os.path.join(dir, "characteristic_idiosyncratic_variance.csv"))
        self.scale_ts.to_csv(os.path.join(dir, "characteristic_scale.csv"))

    @staticmethod
    def load_obj(path: AnyStr):
        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, path)
        if path[-4:] != ".pkl":
            path = path + ".pkl"
        with open(path, 'rb') as f:
            obj = pickle.load(f)
        return obj

    pass


def decompose_vcv(sigma):
    """
    Decompose a variance-covariance matrix into volaitlity and correlation
    :param sigma:
    :return:
    """
    assert isinstance(sigma, pd.DataFrame), "variance-covariance matrix has to be a DataFrame"
    sigma.sort_index(axis=0, inplace=True)
    sigma.sort_index(axis=1, inplace=True)
    vol = np.sqrt(pd.Series(np.diag(sigma), index=sigma.index))
    corr_matrix = pd.DataFrame(np.diag(1. / vol).dot(sigma).dot(np.diag(1. / vol)),
                               index=sigma.index, columns=sigma.columns)
    return vol, corr_matrix


# ------------
# 一系列测试样例
def test_quad_data_obj():
    def _test_raw_time_series(myquad: FactorQuad):
        """
        测试各种原始数据
        :param myquad:
        :return:
        """
        # 1 测试 sigma
        # print(myquad.sigma_ts.shape, myquad.sigma_ts.columns, myquad.sigma_ts.head(10))
        sigma_m, sigma_n = myquad.sigma_ts.shape

        # 2 测试 beta
        # print(myquad.beta_ts.shape, myquad.beta_ts.columns, myquad.sigma_ts.head(10))
        beta_m, beta_n = myquad.beta_ts.shape
        assert beta_n == sigma_n  # 基本上是因子个数
        objs1 = list(myquad.beta_ts.columns)[2:]  # 前两列是date, code
        objs2 = list(list(myquad.sigma_ts.columns))[2:]  # 前两列是date, source
        assert objs1 == objs2

        # 3 测试 Psi
        # print(myquad.psi_ts.shape, myquad.psi_ts.columns, myquad.psi_ts.head(10))
        psi_m, psi_n = myquad.psi_ts.shape
        assert psi_m == beta_m  # 日期+股票的总观测数
        assert list(myquad.beta_ts['code']) == list(myquad.psi_ts['code'])

        # 4 测试 Scale
        # print(myquad.scale_ts.shape, myquad.scale_ts.columns, myquad.scale_ts.head(10))
        scale_m, scale_n = myquad.scale_ts.shape
        assert scale_m == psi_m
        assert list(myquad.scale_ts['code']) == list(myquad.beta_ts['code'])

        print("test data shape finished")

    def test_download_data_from_remote():
        # 1. 测试能够从remote 下载数据， from_src = 0
        myquad = FactorQuad.create_factor_quad(factor_system='HF25_SRU',  # 这需要是一个文件夹！每一个case对应一个文件夹
                                               start_date="20210101",
                                               end_date="20210301",
                                               from_src=0)  # 应该能够从sql下载数据
        myquad.info("remote, we_factor_quad basic load info")
        _test_raw_time_series(myquad)  # 结构是正常的
        print("download over")

    def test_download_data_from_seadrive():  # 请先跑一下这个函数，然后注释掉，下面这个函数会下载数据并保存到本地
        """从数据库，下载数据"""
        # 测试能够从seadrive 下载
        myquad = FactorQuad.create_factor_quad(factor_system='HF25_SRU',  # 这需要是一个文件夹！每一个case对应一个文件夹
                                               start_date="20210101",
                                               end_date="20210301",
                                               from_src=1)  # 从sea_drive下载数据
        myquad.info("seadrive, we_factor_quad basic load info")
        _test_raw_time_series(myquad)  # 结构是正常的
        print("download over")

    # def test_download_data_from_local_pickle():
    #     # 3. 测试能够从local 下载，这个平时不用测试，平时大家电脑硬盘中也没有这个数据
    #     myquad = FactorQuad.create_factor_quad(factor_system='HF25_SRU',  # 这需要是一个文件夹！每一个case对应一个文件夹
    #                                            start_date="20210101",
    #                                            end_date="20210701",
    #                                            from_src=2, local_path="quad_data_dict.pkl")
    #     myquad.info("local pickle, we_factor_quad basic load info")
    #     _test_raw_time_series(myquad)  # 结构是正常的
    #     print("download over")

    def test_load_local_data_and_matrix_match():
        """进行数据测试，应该满足一系列的结构特征"""
        # 1. 从 seadrive 下载数据
        myquad = FactorQuad.create_factor_quad(factor_system='HF25_SRU',  # 这需要是一个文件夹！每一个case对应一个文件夹
                                               start_date="20210101",
                                               end_date="20210301",
                                               from_src=1)  # 从sea_drive下载数据
        myquad.info("seadrive, we_factor_quad basic load info")
        date_with_data = myquad.date_list[0]  # 必须要是一个存在数据的日期
        # 1. 提取对应的矩阵化对齐的数据, 下面的提取会要求提取的四元组结构的一致性
        # 1.1 测试 sigma
        sigma_t = myquad.get_sigma(date_with_data)
        sigma_m, sigma_n = sigma_t.shape
        assert sigma_m == sigma_n, f"{sigma_m, sigma_n} Not Square Matrix"  # 必须是方阵
        assert list(sigma_t.columns) == list(sigma_t.index)  # 必须行与列对象排序都完全相同

        sigma_vec, corr_mat = myquad.get_sigma_and_corr(date_with_data, drop_time=True)  # 适合直接使用
        # print(type(sigma_vec), type(corr_mat), sigma_vec.shape, corr_mat.shape)
        assert len(sigma_vec) == len(corr_mat)
        corr_m, corr_n = corr_mat.shape
        assert corr_m == corr_n
        assert list(sigma_vec.index) == list(corr_mat.columns)
        # 1.2 测试 beta
        beta = myquad.get_beta(date_with_data, drop_time=True)
        beta_m, beta_n = beta.shape  # m_stocks, n_factors
        # print(beta_m, beta_n, sigma_m, sigma_n)
        assert beta_n == sigma_n  # 因子数对齐
        assert list(beta.columns) == list(corr_mat.columns)

        # 1.3 测试 Psi
        psi = myquad.get_psi(date_with_data)
        psi_m, psi_n = psi.shape
        assert psi_m == beta_m
        assert list(psi.index) == list(beta.index)

        # 1.4 测试 Scale
        scale = myquad.get_scale(date_with_data)  # 1列 3675行
        assert len(scale) == beta_m
        assert list(scale.index) == list(beta.index)

        print("至此，单独一天的四个要素已经测试完成")

        # 2 测试完整的对象
        _test_raw_time_series(myquad)  # 测试完整的时间序列

    def test_quad_series_and_build_portfolio():
        """从本地提取数据"""
        myquad = FactorQuad.create_factor_quad(factor_system='HF25_SRU',  # 这需要是一个文件夹！每一个case对应一个文件夹
                                               start_date="20210101",
                                               end_date="20210301",
                                               from_src=1)  # 从sea_drive下载数据
        myquad.info("seadrive, we_factor_quad basic load info")
        # 2. 提取更加完整的序列； 这个序列将会是 双层 index的，第一层index是日期，第二层是前面界定的矩阵
        # idiosyncratic variance时间序列
        asset_ivar = myquad.get_ivar()
        print("ivar ts", asset_ivar.shape, asset_ivar.index, "\n", asset_ivar.head(10))
        ndays = len(set(asset_ivar.index.get_level_values(0)))
        stock_date_num = len(asset_ivar)  # 作为双重index数据对象向量的总长度

        factor_vol = myquad.get_factor_vol()  # 单一的index的对象；获得的对象是每天一行，一行中包含多个因子的波动率
        assert len(set(factor_vol.index)) == ndays

        # # 2. 构建组合，并计算组合的相关统计结果
        # ptfl_w = myquad.scale_ts.pivot(index='date', columns='code', values='scale')
        # ptfl_w = ptfl_w.div(ptfl_w.sum(1), axis=0)
        # ptfl_beta = myquad.get_ptfl_beta(ptfl_w)
        # ptfl_ivar = myquad.get_ptfl_ivar(ptfl_w)
        # ptfl_tot, ptfl_sys, ptfl_idio = myquad.compute_ptfl_var(ptfl_w)
        # # Try systematic risk function
        # asset_sys_risk = myquad.get_systematic_cov(beta_exposure=myquad.beta_ts, asset_col='code')
        # asset_sys_var = myquad.get_systematic_var(beta_exposure=myquad.beta_ts, asset_col='code')
        # # Single name total variance
        # asset_tot_var = asset_sys_var + asset_ivar
        print("多期的测试样例完成")

    # def test_upload_data():
    #     """
    #     从本地的各种数据格式，导出数据到一个数据库中去
    #     Returns:
    #     """
    #     pass

    test_download_data_from_remote()
    test_download_data_from_seadrive()  # 这里仅运行测试sea_drive
    test_load_local_data_and_matrix_match()
    test_quad_series_and_build_portfolio()
    # test_upload_data()


if __name__ == '__main__':
    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.max_rows', None)
    quad = FactorQuad.create_factor_quad(start_date="20210727",
                                         end_date="20210730",
                                         factor_system="HF25_SRAM_DAILY",
                                         from_src=1,
                                         local_path='D:\seadrive_cache_folder\zhouly\群组资料库')
    print(1)
    # test_quad_data_obj()
