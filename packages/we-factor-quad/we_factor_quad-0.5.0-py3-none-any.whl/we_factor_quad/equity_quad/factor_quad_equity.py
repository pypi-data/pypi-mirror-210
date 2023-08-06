# 基于 FactorQuad 基础包，导入并引入关于 Equity 的相关功能
# 为什么 HF25_SRA 为什么要这么特殊的处理？
import os

import numpy as np
import pandas as pd
from typing import Dict, Union, List
from we_factor_quad.equity_quad import solve_colinear
from we_factor_quad.factor_quad import FactorQuad
from we_factor_quad.factor_quad_settings import StocksOutputReport, settings


class FactorQuadEQ(FactorQuad):
    def __init__(self, factor_system: str, raw_data: Dict,
                 _code_col_name: str = "code",
                 _time_col_name: str = "date"):
        """
        :param factor_system:
        :param raw_data:
        :param _code_col_name: 默认变量名
        :param _time_col_name:
        """
        super().__init__(factor_system=factor_system,
                         raw_data=raw_data,
                         _code_col_name=_code_col_name,
                         _time_col_name=_time_col_name)

        # 这个shift 这样设计是不太合适的，应该外部做好，进来调整
        # self.sigma_ts = FactorQuadEQ.type_date_col(raw_data['characteristic_covariance'],
        #                                            (factor_system == 'HF25_SRA') and WE_OVERWRITE)

        # 对于股票的特别的调整
        # self.beta_ts = self.beta_cleanup(self.beta_ts)  # 为什么需要这个cleanup？

        self.sigma_withcountry_ts = None  # 一个股票体系才有的新变量；添加国家因子与否
        self.beta_withcountry_ts = None

    @staticmethod
    def create_factor_quad(factor_system: str,
                           start_date: str,
                           end_date: str,
                           from_src: int = 1,
                           local_path: str = None) -> "FactorQuadEQ":
        """
        创建一个因子四要素数据结构;
        :param factor_system: 因子系统的名称，对应于数据库中的 case 名称
        :param start_date: 8 digits格式 日期
        :param end_date:
        :param from_src: 0 表示从网络sql提取数据，1表示从sea_drive提取数据，2表示从本地提取数据（2需要对应一个pkl文件）
        :param local_path: 当from_src == 2时，需要一个pkl文件；0表示remote，1表示 seadrive，所以默认为1；
        :return:
        """
        # 结束日期处于行业调整期，自动将结束日期改为调整后
        # if '20210805' > end_date > '20210729':
        #     end_date = '20210806'
        raw_data = FactorQuadEQ.factor_quads_download(factor_system=factor_system,
                                                      start_date=start_date,
                                                      end_date=end_date,
                                                      from_src=from_src,
                                                      local_path=local_path)
        # raw_data = merge("D:/jiaochayuan_files/projects/we_factor_quad_/we_factor_quad/equity_quad/HF25_day_test")
        return FactorQuadEQ(factor_system, raw_data=raw_data)

    def rearrange_cols(self, data: pd.DataFrame, col_list: list):
        """
        根据给定的 column list 重排各列
        :param data: 数据dataframe
        :param col_list: 重排各列以后的列顺序列表
        :return: 重排各列的dataframe
        """
        return data[col_list].copy()

    def rearrange_cross_sec_sigma_rows(self, data: pd.DataFrame):
        """
        对一个时间截面上的sigma行业因子在前的顺序重排sigma中的各行
        :param data: 一个时间截面上的sigma
        :return: 一个时间截面上重排各行的sigma
        """
        df = data.copy()

        industry_set = set([i for i in df.columns if i.startswith('industry')])
        other_set = set(df.columns) - industry_set
        part1 = df.loc[df['source'].isin(industry_set)]
        part2 = df.loc[df['source'].isin(other_set)]
        df = pd.concat([part1, part2], axis=0)
        return df

    def get_cross_sec_sigma_with_country(self, data: pd.DataFrame):
        """
        将一个时间截面上且已完成行列重排的sigma转换成包含国家因子的sigma
        :param data: 一个时间截面上的sigma
        :return: 一个时间截面上包含国家因子的sigma
        """
        df = data.copy()
        date = df[self._time_col_name].iloc[0]

        columns = list(df.columns) + ['country']
        columns_ind = {v: k for k, v in enumerate(columns)}

        empty_factors = list(df.columns[(df == 0).all(axis=0)])

        df = df.drop(empty_factors, axis='columns')
        df = df[~df['source'].isin(empty_factors)]

        df_date = df[[self._time_col_name]].copy()
        df_date = df_date.reset_index(drop=True)
        df_date.loc[len(df_date)] = list(df_date.iloc[-1])

        df_factors = df.drop([self._time_col_name, 'source'], axis='columns')

        df_with_country = solve_colinear.get_sigma_with_country(df_sigma=df_factors,
                                                                k_ind=len(
                                                                    [i for i in df_factors.columns if
                                                                     i.startswith('industry')]))
        df_with_country = df_with_country.reset_index()
        df_with_country = df_with_country.rename({'index': 'source'}, axis='columns')

        df = df_date.join(df_with_country)

        for factor in empty_factors:
            df.insert(len(df), factor, 0)
            df.loc[len(df)] = [date, factor] + [0] * (len(df.columns) - 2)

        df = df[columns]
        df = df.sort_values(by=['source'], key=lambda x: x.map(columns_ind)).reset_index(drop=True)

        return df

    def add_country_factor(self):
        """
        添加国家因子，对self.sigma_withcountry_ts 与 self.beta_withcountry_ts 赋值
        :return: None
        """
        sigma = self.sigma_ts
        beta = self.beta_ts

        industry_list = [i for i in sigma.columns if i.startswith('industry')]
        style_list = [i for i in sigma.columns[2:] if i not in industry_list]
        sigma_cols = [self._time_col_name, 'source'] + industry_list + style_list
        sigma = self.rearrange_cols(sigma, sigma_cols)

        dates = list(sigma[self._time_col_name].unique())

        switch = True
        sigma_with_country = None
        for date in dates:
            sigma_slice = sigma[sigma[self._time_col_name] == date].copy().reset_index(drop=True)
            sigma_slice = self.rearrange_cross_sec_sigma_rows(sigma_slice)
            sigma_with_country_slice = self.get_cross_sec_sigma_with_country(data=sigma_slice)
            if switch:
                sigma_with_country = sigma_with_country_slice
                switch = False
            else:
                sigma_with_country = pd.concat([sigma_with_country, sigma_with_country_slice], axis=0,
                                               ignore_index=True)

        beta_cols = [self._time_col_name, self._code_col_name] + industry_list + style_list
        beta_with_country = self.rearrange_cols(beta, beta_cols)
        beta_with_country.insert(len(beta.columns), 'country', 1)

        self.sigma_withcountry_ts = sigma_with_country
        self.beta_withcountry_ts = beta_with_country

        return sigma_with_country, beta_with_country

    # def beta_cleanup(self, df: pd.DataFrame) -> pd.DataFrame:
    #     """
    #     临时解决方案，把Barra的beta变成和sigma吻合的；这个函数的出现是奇怪的，不应该有这个函数
    #     :param df:
    #     :return:
    #     """
    #     df.loc[:, 'characteristic'] = df.loc[:, 'characteristic'].str.replace(' Exp', '')
    #     df.loc[:, 'characteristic'] = df.loc[:, 'characteristic'].str.replace(' ActiveExp', '')
    #     df.drop_duplicates([self._time_col_name, self._code_col_name, 'characteristic'], inplace=True)
    #     return df

    def capped_psi_adjustment(self, cap_multiplier: int = 25):
        """
        idio risk 特异性风险，用帽子来去极值；帽子的数值是 psi 波动率数值中位数的25倍，超过帽子的认为就是帽子；
        :param cap_multiplier: 乘子倍数
        :return: 调整后的特异性风险向量
        """
        psi_pivoted = self.psi_ts.pivot(index=self._time_col_name, columns=self._code_col_name, values='var')
        psi_cap = (0.0 * psi_pivoted).add(psi_pivoted.median(1) * cap_multiplier, axis=0)
        idx = (psi_pivoted > psi_cap)
        psi_pivoted[idx] = psi_cap[idx]
        # return psi_pivoted.stack().reset_index().rename(columns={0: 'var'})
        self.psi_ts = psi_pivoted.stack().reset_index().rename(columns={0: 'var'})  # 直接内部修正掉，不需要返回了


def load_quad_to_csv(csv_output_path=None):
    """
    将seadrive中的quad数据保存成csv文件，并用quad计算factor
    """
    myquad = FactorQuadEQ.create_factor_quad(factor_system=StocksOutputReport.msg_factor_case_name,
                                             start_date=StocksOutputReport.start,
                                             end_date=StocksOutputReport.end,
                                             from_src=StocksOutputReport.from_local,
                                             local_path=settings.seadrive_local_path)
    import datetime
    if pd.to_datetime(StocksOutputReport.end) not in sorted(myquad.date_list):
        StocksOutputReport.end = datetime.datetime.strftime(pd.to_datetime(sorted(myquad.date_list)[-1]), '%Y%m%d')
    added_myquad = FactorQuadEQ.create_factor_quad(factor_system=StocksOutputReport.msg_factor_case_name,
                                                   start_date=StocksOutputReport.end,
                                                   end_date=datetime.datetime.strftime((pd.to_datetime(
                                                       StocksOutputReport.end) + datetime.timedelta(days=20)),
                                                                                       '%Y%m%d'),
                                                   from_src=StocksOutputReport.from_local,
                                                   local_path=settings.seadrive_local_path)
    assert len(added_myquad.date_list) > 0, 'factor return数据不全'
    if len(added_myquad.date_list) > 1:
        added_date = added_myquad.date_list[1]
    else:
        added_date = added_myquad.date_list[0]
    from we_factor_quad.data_api import wiser_fetch_factor_return

    if csv_output_path is None:
        csv_output_path = os.getcwd()
    wiser_fetch_factor_return(factor_system=StocksOutputReport.msg_factor_case_name,
                              start_date=StocksOutputReport.start,
                              end_date=datetime.datetime.strftime(pd.to_datetime(added_date), '%Y%m%d'),
                              seadrive_localpath=settings.seadrive_local_path).to_csv(
        os.path.join(csv_output_path, "characteristic_return.csv"))

    # 不传入路径默认csv保存到当前文件夹下
    myquad.save_to_csv(csv_output_path)


def test_FactorQuadEQ():
    def load_data():
        myquad = FactorQuadEQ.create_factor_quad(factor_system=StocksOutputReport.msg_factor_case_name,
                                                 start_date=StocksOutputReport.start,
                                                 end_date=StocksOutputReport.end,
                                                 from_src=StocksOutputReport.from_local,
                                                 local_path=settings.seadrive_local_path)
        myquad.info("check info")
        print("finish")

    load_data()


# def merge(file_path):
#     files =  [
#         "characteristic_covariance.csv",
#         "characteristic_exposure.csv",
#         "characteristic_idiosyncratic_variance.csv",
#         "characteristic_scale.csv"
#     ]
#     characteristic_covariance = pd.DataFrame()
#     characteristic_exposure = pd.DataFrame()
#     characteristic_idiosyncratic_variance = pd.DataFrame()
#     characteristic_scale  = pd.DataFrame()
#     for dirpath, dirnames, filenames in os.walk(file_path):
#         for dirname in dirnames:
#             date_path = os.path.join(dirpath, dirname)
#             for file in files:
#                 path = os.path.join(date_path, file)
#                 data = pd.read_csv(path,index_col=0)
#                 if file == 'characteristic_covariance.csv':
#                     characteristic_covariance = pd.concat([characteristic_covariance,data])
#                 elif file == 'characteristic_exposure.csv':
#                     characteristic_exposure = pd.concat([characteristic_exposure, data])
#                 elif file == 'characteristic_idiosyncratic_variance.csv':
#                     characteristic_idiosyncratic_variance = pd.concat([characteristic_idiosyncratic_variance, data])
#                 elif file == 'characteristic_scale.csv':
#                     characteristic_scale = pd.concat([characteristic_scale, data])
#                 else:
#                     print('no such file !'+ str(file))
#
#     return {"characteristic_covariance": characteristic_covariance[characteristic_covariance['DATE']>=20221101],\
#            "characteristic_exposure": characteristic_exposure[characteristic_exposure['DATE']>=20221101],\
#            "characteristic_idiosyncratic_variance": characteristic_idiosyncratic_variance[characteristic_idiosyncratic_variance['DATE']>=20221101],\
#            "characteristic_scale": characteristic_scale[characteristic_scale['DATE']>=20221101]}

if __name__ == '__main__':
    # test_FactorQuadEQ()
    load_quad_to_csv()
