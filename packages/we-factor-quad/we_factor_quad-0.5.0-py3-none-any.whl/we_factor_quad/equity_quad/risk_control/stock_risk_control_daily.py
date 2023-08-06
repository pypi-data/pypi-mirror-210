# 核心考察的，是使用指定的因子组，来对指定对象(个股)进行风险控制，考察的内容是3个点
# 1. 能不能总体上控得住，
# 2. 能不能一直控得住，
# 3. 控制下的偏离不能太远

import numpy as np
import pandas as pd
from we_report.data_type import report_data
import matplotlib.pyplot as plt
from copy import deepcopy
from we_factor_quad.equity_quad.factor_quad_equity import FactorQuadEQ
from typing import Union, List, Dict
from we_factor_quad.factor_quad_settings import StocksOutputReport
from we_factor_quad.factor_quad_settings import settings


class RiskDecomposition:
    """基于已经分解到因子体系上的相关数据，实现风险的分解以及可视化
    这个 class 为什么有存在的必要？不能直接用 FactorQuad 吗？
    不能，因为这个类可以在保持原始数据的基础上，针对特定的股票对象进行分析，而 FactorQuad 是针对所有股票的一个简单数据结构
    所以，这个 class，是基于 FactorQuad，做的进一步的分解、分析、可视化等
    """

    def __init__(self,
                 factor_quad: FactorQuadEQ,
                 stock_ret_df: Union[pd.DataFrame] = None,
                 date_var_name: str = "date"):
        """
        :param factor_quad: 一个因子四要素对象
        :param stock_ret_df: 按照隔离设计原则，不能通过 stock_tickers 来导入数据，而是必须是完整的数据
        :param date_var_name: 日期的变量名，具体是stock_ret_df中的变量名
        """
        self.factor_quad = factor_quad
        self.stock_ret_df = stock_ret_df

        quad_tickers = list(self.factor_quad.psi_ts.columns)
        if stock_ret_df is None:  # 如果没有特别指定，就全部有的都用起来；全部对象、全部时间
            self.stock_tickers = quad_tickers
        else:  # 如果有特别指定，就选择对象的交集、时间的交集
            if date_var_name in stock_ret_df.columns:
                stock_ret_df.set_index(date_var_name, inplace=True)  # 转为index
            stock_ret_df.index = pd.to_datetime(stock_ret_df.index)  # 转为统一的时间格式
            stock_ret_df.dropna(axis=1, how="any", inplace=True)  # 去掉存在空的列，输入的股票必须是完整的
            selected_tickers = list(stock_ret_df.columns)
            self.stock_tickers = list(set(quad_tickers).intersection(set(selected_tickers)))  # 能够分析的，只是交集
            self.date_range = list(set(stock_ret_df.index).intersection(set(self.factor_quad.psi_ts.index)))  # 时间的交集
            # todo 似乎还需要判断一下，这个日期中间不应该有缺漏

    def get_decomposition_stats(self) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame):
        """
        将 quad 中的内容，进行风险分解，并进入进一步进行分解
        针对一个 factor quad 进行一次分析；
        :return: 风险分解，返回4个部分，分别是总体风险、系统风险、个股风险、因子风险
        """
        # 原始对象的3个风险特征数据拿过来
        # factor_volatility = self.factdor_quad.get_factor_vol()
        asset_sys_variance = self.factor_quad.get_systematic_var(beta_exposure=self.factor_quad.beta_ts).unstack()
        asset_idio_variance = self.factor_quad.get_ivar().unstack()  # unstack窄表转宽表
        asset_total_var = asset_sys_variance + asset_idio_variance  # 宽表，行日期，列股票
        # 将原始数据进行统计
        var_decomp = (asset_sys_variance / asset_total_var).T.median()  # 数值
        asset_sys_variance = self.factor_quad.get_systematic_var(beta_exposure=self.factor_quad.beta_ts)
        # todo: delete after seafile quad update
        if type(asset_sys_variance) == pd.Series:
            asset_sys_variance = asset_sys_variance.unstack().astype('float')
        asset_idio_variance = self.factor_quad.get_ivar().unstack()
        asset_total_var = asset_sys_variance + asset_idio_variance
        factor_vol = self.factor_quad.get_factor_vol()

        return asset_total_var, asset_idio_variance, asset_sys_variance, factor_vol

    def weighted_portfolio(self, weights: Union[Dict, pd.DataFrame]):
        """
        通过权重的方式，输入一个基于已有的个股的portfolio，然后基于这个portfolio来计算组合
        这个结果可以直接扩展用来分析一个投资组合的风险与策略问题
        :param weights: 权重，可以是一维向量，也可以是多期向量，如果是多期，则应该与quad的时间内部，并能够进行嵌入；
        :return:
        """
        if type(weights) == 'Dict':
            stock_portfolio = pd.DataFrame(weights, index=close_daily.index)
        else:
            stock_portfolio = weights.asfreq('D', method='pad')
        stock_portfolio.index.name = 'date'
        stock_portfolio.columns.name = 'code'
        stock_portfolio = stock_portfolio.loc[self.factor_quad.scale_ts.date.drop_duplicates().sort_values()]
        return stock_portfolio

    def get_portfolio_risk(self, weights: pd.DataFrame):
        """
        通过权重的方式，输入一个基于已有的个股的portfolio，然后基于这个portfolio来计算组合
        这个结果可以直接扩展用来分析一个投资组合的风险与策略问题
        :param weights: 权重，可以是一维向量，也可以是多期向量，如果是多期，则应该与quad的时间内部，并能够进行嵌入；
        :return:
        """
        portfolio_var, portfolio_sys_var, portfolio_idio_var = self.factor_quad.compute_ptfl_var(weights)
        # portfolio_var = portfolio_var.resample('BM').last()
        # portfolio_sys_var = portfolio_sys_var.resample('BM').last()
        # portfolio_idio_var = portfolio_idio_var.resample('BM').last()
        return portfolio_var, portfolio_sys_var, portfolio_idio_var

    def get_portfolio_return(self, weights: pd.DataFrame):
        """
        提取一个组合的收益率
        :param weights:
        :return:
        """
        return (weights * self.stock_ret_df).sum(axis=1).loc[weights.index].pct_change()


class RiskControlStrategy:
    """
    通过采用合理的风控策略，考察其针对个股或组合的风控的效果，调整个股权重使得每个周期都为target volatility
    :param stock_w: T x 1 pd.Series, stock weight
    :param stock_vol: T x 1 pd.Series, annualized volatility of the stock at each point
    :param target_vol: float, target annualized volatility
    :param stock_portfolio: pd.DataFrame, Dict, stock_portfolio
    :return: 满足目标波动率的个股配置权重时间序列
    """

    def __init__(self,
                 total_var_list: List = None,
                 portfolio_var_list: List = None,
                 target_vol: float = 0.1,
                 stock_code: str = '000001.SZ',
                 px_close: pd.DataFrame = None,
                 stock_portfolio: Union[pd.DataFrame, Dict] = None
                 ):
        assert not ((total_var_list is None) and (portfolio_var_list is None)), 'var_list为空'
        self.total_var_list = total_var_list
        self.target_vol = target_vol
        self.stock_code = stock_code
        self.close_daily = px_close
        self.stock_portfolio = stock_portfolio
        self.portfolio_var_list = portfolio_var_list

    def stock_risk_control(self) -> pd.DataFrame:
        """
        个股风控，将每个周期个股权重都调整到target volatility
        """
        stock_w_lst = []
        for var in self.total_var_list:
            # 设置单只个股权重为全1向量
            self.stock_w_init = pd.Series(np.ones(len(var[self.stock_code])), index=var.index)
            self.stock_w = self.stock_w_init.div(np.sqrt(var[self.stock_code]), axis=0) * self.target_vol
            stock_w_lst.append(self.stock_w)
        return stock_w_lst

    def protfolio_risk_control(self) -> pd.DataFrame:
        """
        组合风控，将每个周期组合权重都调整到target volatility
        """
        portfolio_w_lst = []
        for var in self.portfolio_var_list:
            self.stock_portfolio = self.stock_portfolio.asfreq('D', method='pad').reindex(var.index)
            self.portfolio_w = self.stock_portfolio.div(np.sqrt(var), axis=0) * self.target_vol
            portfolio_w_lst.append(self.portfolio_w)
        return portfolio_w_lst

    def get_portfolio_control_performance(self, rolling_window=21, annualize_num=252):
        """
        个股风控表现，输出风控后的波动率
        """
        if self.close_daily is not None:
            portfolio_w_lst = self.protfolio_risk_control()
            performance_lst = []
            for w in portfolio_w_lst:
                w = w.reindex(self.close_daily.index).fillna(method='pad')
                realized_vol = (w * self.close_daily.pct_change().rolling(rolling_window).std() * np.sqrt(
                    annualize_num)).sum(axis=1).loc[w.index]
                # performance_lst.append(realized_vol.asfreq('BM', method='pad'))
                performance_lst.append(realized_vol)
            return performance_lst
        else:
            return []

    def get_risk_control_performance(self, rolling_window=21, annualize_num=252):
        """
        个股风控表现，输出风控后的波动率
        """
        stock_w_lst = self.stock_risk_control()
        performance_lst = []
        for w in stock_w_lst:
            adj_close = pd.concat([self.close_daily[self.stock_code], w], axis=1)
            adj_close.columns = ['close', 'w']
            adj_close['w'] = adj_close['w'].fillna(method='pad')
            adj_close['realized_vol'] = adj_close['close'].pct_change().rolling(rolling_window).std() * np.sqrt(
                annualize_num)
            adj_close['adj_vol'] = adj_close['realized_vol'] * adj_close['w']
            # performance_lst.append(adj_close['adj_vol'].asfreq('BM', method='pad'))
            performance_lst.append(adj_close['adj_vol'])

        return performance_lst

    pass


class CompareReports:
    """
    整合一个或对比多个模型数据, 按照指定格式输出结果，输出指定形式的报告
    一个风险因子体系，应该能够帮助我们预测风险，并且基于预测做出必要的操作，从而控制风险。
    但是预测风险的函数在哪里？控制风险的策略又在哪里？
    """

    def __init__(self,
                 decomp_names: List[str],
                 risk_decomp: List[RiskDecomposition],
                 px_close: pd.DataFrame,
                 stocks: List = None,
                 stock_names: List = None,
                 stock_portfolio: Union[pd.DataFrame, Dict] = None):
        self.decomp_names = decomp_names
        self.risk_decomp = risk_decomp
        assert len(self.decomp_names) == len(self.risk_decomp), "输入的分解模型 vs 模型名称 长度不一致"
        self.total_var_list, self.idio_var_list, self.sys_var_list, self.factor_vol_list = self._get_all_decompsition()  # 内部完成分解
        # 另外还需要输入价格
        self.px_close = px_close  # todo 可能还需要一些判断，匹配性等
        # self.px_ret = np.log(px_close.asfreq('BM', method='pad')).diff()  # todo 可能要调整收益率频率，现在是月
        if self.px_close is not None:
            self.px_ret = np.log(px_close).diff()  # todo 可能要调整收益率频率，现在是月
        self.stocks = stocks
        self.stock_names = stock_names
        self.stock_portfolio = stock_portfolio

    def _get_all_decompsition(self):
        '''
        利用RiskDecomposition类获取风险分解数据
        '''
        total, idio, sys, factor_vol = [], [], [], []
        for i in range(len(self.risk_decomp)):
            total_i, idio_i, sys_i, factor_vol_i = self.risk_decomp[i].get_decomposition_stats()
            total.append(total_i)
            idio.append(idio_i)
            sys.append(sys_i)
            factor_vol.append(factor_vol_i)
        return total, idio, sys, factor_vol

    def _get_portfolio_decompsition(self):
        '''
        利用RiskDecomposition类获取组合风险分解数据
        '''
        total, idio, sys, portfolio_return_list = [], [], [], []
        for i in range(len(self.risk_decomp)):
            portfolio_w = self.risk_decomp[i].weighted_portfolio(self.stock_portfolio)
            portfolio_var, portfolio_sys_var, portfolio_idio_var = self.risk_decomp[i].get_portfolio_risk(portfolio_w)
            if self.px_close is not None:
                portfolio_return = self.risk_decomp[i].get_portfolio_return(portfolio_w)
            else:
                portfolio_return = None
            total.append(portfolio_var)
            idio.append(portfolio_idio_var)
            sys.append(portfolio_sys_var)
            portfolio_return_list.append(portfolio_return)
        return portfolio_w, total, idio, sys, portfolio_return_list

    def _get_portfolio_risk_control_result(self, target_vol=0.1):
        '''
        利用RiskControlStrategy获取组合风控策略，及组合风控表现
        :param stock_code: 要风控的组合
        :param target_vol: 目标波动率
        :return:

        '''
        portfolio_w, portfolio_total, portfolio_idio, portfolio_sys, portfolio_return_list = self._get_portfolio_decompsition()
        portfolio_risk_control_w_lst = RiskControlStrategy(portfolio_var_list=portfolio_total, px_close=self.px_close,
                                                           target_vol=target_vol,
                                                           stock_portfolio=portfolio_w).protfolio_risk_control()
        portfolio_risk_performance_lst = RiskControlStrategy(portfolio_var_list=portfolio_total, px_close=self.px_close,
                                                             target_vol=target_vol,
                                                             stock_portfolio=portfolio_w).get_portfolio_control_performance()
        return portfolio_risk_control_w_lst, portfolio_risk_performance_lst

    def _get_stock_risk_control_result(self, stock_code, target_vol=0.1):
        '''
        利用RiskControlStrategy获取个股风控策略，及个股风控表现
        :param stock_portfolio: 要风控的个股
        :param target_vol: 目标波动率
        :return:

        '''
        stock_risk_control_w_lst = RiskControlStrategy(total_var_list=self.total_var_list, px_close=self.px_close,
                                                       stock_code=stock_code,
                                                       target_vol=target_vol).stock_risk_control()
        stock_risk_performance_lst = RiskControlStrategy(total_var_list=self.total_var_list, px_close=self.px_close,
                                                         stock_code=stock_code,
                                                         target_vol=target_vol).get_risk_control_performance()
        return stock_risk_control_w_lst, stock_risk_performance_lst

    def write_sql(self, df):
        import pymysql

        # 数据库连接信息
        df = df.reset_index()
        df = df.rename(
            columns={'index': 'trade_date', '0Close': 'close', '1msg_Vol': 'msg_Vol', '2msg_iVol': 'msg_iVol',
                     '3Forward_3M_Vol': 'forward_3m', '4msg_iVol_pct': 'msg_iVol_pct'})
        from sqlalchemy import create_engine
        from urllib.parse import quote_plus as urlquote

        from sqlalchemy.orm import sessionmaker
        engine = create_engine(f"mysql+pymysql://root:{urlquote('dev-project@mysql.')}@172.16.127.213:3306/supersetdb")

        # session = sessionmaker(engine)()

        data = df
        data.to_sql('StockRisk', engine, if_exists='append', chunksize=100000, index=None)
        print('存入成功！')

        pass

    def get_reports(self, report_contents: str = "full", output_file: str = 'stock_risk_report.xlsx'):
        """
        输出报告
        :param report_contents: 报告类型，full为完整报告，除了full外，还可以选择sys_idio, factor_vol, rmv_vov, single_stock
        :param output_file: 输出文件地址
        :return:
        """
        full_contents = ["full", "sys_idio", "factor_vol", "volatility", "rmv_vov", "stock_vol",
                         "portfolio", "pure_portfolio", "all_stock_vol"]  # 能够处理的所有功能
        if isinstance(report_contents, str):
            report_contents = [report_contents]  # 先全部转为list
        assert set(report_contents).issubset(set(full_contents)), f"report_contents contains sth not in full_contents"
        if "full" in report_contents:
            is_full = True
        else:
            is_full = False
        page_dic = {}
        if "sys_idio" in report_contents or is_full:
            var_decomp, stat_table = self.get_sys_idio_stats()
            stat_table = self.adjust_table_format(stat_table)
            var_decomp = self.adjust_table_format(var_decomp)
            page_data = report_data.PageData(tables=[stat_table], appendix_tables=[var_decomp])
            page_dic["sys_idio"] = page_data
        if "factor_vol" in report_contents or is_full:
            factor_vol_ts_lst = self.get_factor_vol_ts()
            factor_vol_ts_lst = [self.adjust_table_format(i) for i in factor_vol_ts_lst]
            page_data = report_data.PageData(tables=factor_vol_ts_lst)
            page_dic["factor_vol"] = page_data
        if "volatility" in report_contents or is_full:
            factor_vol_table_lst = self.get_factor_vol_stats()
            factor_vol_table_lst = [self.adjust_table_format(i) for i in factor_vol_table_lst]
            page_data = report_data.PageData(tables=factor_vol_table_lst)
            page_dic["volatility"] = page_data
        if "rmv_vov" in report_contents or is_full:
            rmv, vov, var = self.get_var_rmv_vov()
            rmv = self.adjust_table_format(rmv)
            vov = self.adjust_table_format(vov)
            var = self.adjust_table_format(var)
            page_data = report_data.PageData(tables=[rmv, vov, var])
            page_dic["rmv_vov"] = page_data
        if "stock_vol" in report_contents or is_full:
            assert self.stocks is not None and self.stock_names is not None, "请提供股票代码和股票名称"
            st_name_dic = dict(zip(self.stocks, self.stock_names))
            df_dic = self.get_stock_report()
            for st in df_dic.keys():
                df_dic[st].index = df_dic[st].index.astype('str')
                mypage_st = report_data.PageData(text='stock_vol', tables=[
                    pd.concat([round(df_dic[st].iloc[:, 0], 2), df_dic[st].iloc[:, 1:]], axis=1).reset_index()])
                page_dic[st_name_dic[st]] = mypage_st
        if "all_stock_vol" in report_contents or is_full:
            assert self.stocks is not None and self.stock_names is not None, "请提供股票代码和股票名称"
            st_name_dic = dict(zip(self.stocks, self.stock_names))
            df_dic = self.get_all_stock_report()
            lst = []
            for k, v in df_dic.items():
                v['code'] = k
                lst.append(v)

            sql_df = pd.concat(lst)
            # self.write_sql(sql_df)
        if "portfolio" in report_contents or is_full:
            assert self.stock_portfolio is not None, "请提供投资组合及权重"
            protfolio_data = self.get_portfolio_report()
            protfolio_data.index = protfolio_data.index.astype('str')
            page_data = report_data.PageData(tables=[protfolio_data.reset_index()])
            page_dic["投资组合"] = page_data
        if "pure_portfolio" in report_contents or is_full:
            assert self.stock_portfolio is not None, "请提供投资组合及权重"
            protfolio_data = self.get_pure_portfolio_report()
            protfolio_data.index = protfolio_data.index.astype('str')
            page_data = report_data.PageData(tables=[protfolio_data.reset_index()])
            page_dic["投资组合风控"] = page_data
        # 将数据写入excel
        report = report_data.ReportData(all_pages=page_dic)  # 合并成PageData格式
        report_data.ExcelReport.output_report(report, output_file)

    @staticmethod
    def calculate_quantile_stats_ts(df) -> pd.DataFrame:
        '''
        计算25%、50%、75%分位数时间序列
        :param kwargs:
        :return:
        '''
        quantile_stats_ts = df.T.describe().T \
            .filter(['25%', '50%', '75%'])  # .asfreq('BM', method='pad')

        return quantile_stats_ts

    @staticmethod
    def calculate_quantile_stats(df) -> pd.Series:
        '''
        计算10%、25%、50%、75%、90%分位数时间统计表
        :param kwargs:
        :return:
        '''
        quantile_stats = pd.Series([df.stack().quantile(i) for i in [0.1, 0.25, 0.5, 0.75, 0.9]] + [
            df.stack().mean()], index=['10%', '25%', '50%', '75%', '90%', 'mean'])

        return quantile_stats

    def get_sys_idio_stats(self) -> (pd.DataFrame, pd.DataFrame):
        """
        输入个股风险数据，输出sheet1统计表格
        :param kwargs: total_var_list, idio_var_list, sys_var_list, name_list(待对比模型名称列表)
        :return:sheet1统计表及附录
        """
        # sheet1 附录
        decomp_lst = []
        for i in range(len(self.decomp_names)):
            decomp = CompareReports.calculate_quantile_stats_ts(self.sys_var_list[i] / self.total_var_list[i])
            decomp.columns = self.decomp_names[i] + decomp.columns
            decomp_lst.append(decomp)
        var_decomp = pd.concat(decomp_lst, axis=1)

        # sheet1 主表格
        ivar_stat = [CompareReports.calculate_quantile_stats(i) for i in self.idio_var_list]
        sys_var_stat = [CompareReports.calculate_quantile_stats(i) for i in self.sys_var_list]

        stat_table = pd.concat(ivar_stat + sys_var_stat, axis=1)
        stat_table.columns = [i + '_ivar' for i in self.decomp_names] + [i + '_sys_var' for i in self.decomp_names]

        return var_decomp, stat_table

    def get_factor_vol_ts(self) -> list:
        """
        输入factor_vol数据，返回factor_vol时间序列,输出sheet2统计表
        """
        return self.factor_vol_list

    def get_factor_vol_stats(self) -> list:
        """
        输入factor_vol数据，返回factor_vol统计表，输出sheet3统计表
        """
        factor_vol_table_lst = []
        for i in range(len(self.decomp_names)):
            # sheet2 table
            factor_vol_table = self.factor_vol_list[i].describe()
            factor_vol_table.loc['STD/mean'] = self.factor_vol_list[i].std() / self.factor_vol_list[i].mean()
            factor_vol_table = pd.concat(
                [factor_vol_table.iloc[0], factor_vol_table.iloc[1:].T],
                axis=1).T
            factor_vol_table_lst.append(factor_vol_table)

        return factor_vol_table_lst

    def get_var_rmv_vov(self) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
        """
        输入个股风险、monthly_return、收盘价，返回个股风控报告，输出sheet4统计表
        """
        # sheet4 主表
        # Single name vol targeting
        rmv_lst = []
        vov_lst = []
        var_lst = []
        annual_num = 252
        for i in range(len(self.decomp_names)):
            target_vol = 0.1
            # target_ret = self.px_ret \
            #              / np.sqrt(self.total_var_list[i].fillna(method='pad').asfreq('BM', method='pad')).shift(
            #     1) * target_vol
            target_ret = self.px_ret \
                         / np.sqrt(self.total_var_list[i].fillna(method='pad')).shift(1) * target_vol
            # 1) Tail risk: VaR (Histogram 1)
            var = (target_ret.abs().quantile(0.99) * np.sqrt(annual_num) / target_vol)

            # 2) Vol targeting (Histogram 2)
            rmv = (target_ret.std() * np.sqrt(annual_num))

            # 3) Volatility of Volatility (Histogram 3)
            vov = np.sqrt(
                ((target_ret.apply(lambda x: x.dropna().rolling(window=annual_num).std()) * np.sqrt(
                    annual_num) - target_vol) ** 2))
            rmv_lst.append(rmv)
            var_lst.append(var)
            vov_lst.append(vov)
        rmv = pd.concat(rmv_lst, axis=1)
        var = pd.concat(var_lst, axis=1)
        vov = pd.concat(vov_lst, axis=1)

        return rmv, var, vov

    def get_stock_report(self) -> Dict:
        """
        # total_var_list, idio_var_list, px_close, name_list, stocks
        输入close、return、stock_vol返回 df_dic,提供个股风控报告
        """
        rolling_vol = (np.log(self.px_close).diff(5).replace(0.0, np.nan)) \
                          .rolling(window=63, min_periods=21).std().shift(-63) * np.sqrt(52)
        df_dic = {}
        for stock in self.stocks:
            stock_risk_dic = {'0Close': self.px_close[stock],
                              '3Forward_3M_Vol': rolling_vol[stock]}
            for i in range(len(self.decomp_names)):
                stock_risk_dic[f'1{self.decomp_names[i]}_Vol'] = np.sqrt(self.total_var_list[i])[stock]
                stock_risk_dic[f'2{self.decomp_names[i]}_iVol'] = np.sqrt(self.idio_var_list[i])[stock]
                stock_w, risk_managed_performance = self._get_stock_risk_control_result(stock_code=stock,
                                                                                        target_vol=0.1)
                stock_risk_dic[f'4{self.decomp_names[i]}_iVol_pct'] = np.sqrt(self.idio_var_list[i])[stock] / \
                                                                      np.sqrt(self.total_var_list[i])[stock]
                # stock_risk_dic[f'5{self.decomp_names[i]}_Wgt'] = stock_w[i]
                #
                # stock_risk_dic[f'6{self.decomp_names[i]}_Pfm'] = risk_managed_performance[i]
                # stock_risk_dic[f'7{self.decomp_names[i]}_M_Ret'] = ((stock_w[i]*self.px_close[stock]).pct_change(5)+1).cumprod()
                # stock_risk_dic[f'8{self.decomp_names[i]}_F_Ret'] = (self.px_close[stock].pct_change()+1).cumprod()
                # stock_risk_dic[f'9{self.decomp_names[i]}_C_Ret'] = (stock_w[i].mean()*(self.px_close[stock].pct_change())+1).cumprod()

            df = pd.DataFrame(stock_risk_dic)
            df.index = pd.to_datetime(df.index.astype('str'))
            df = df[df.columns.sort_values()]
            df_dic[stock] = df
        # for stock in self.stocks:
        #     stock_risk_dic = {'0Close': self.px_close[stock].resample('BM').last(),
        #                       '3Forward 3M Vol': rolling_vol[stock].resample('BM').last(), }
        #     for i in range(len(self.decomp_names)):
        #         stock_risk_dic[f'1{self.decomp_names[i]} Vol'] = np.sqrt(self.total_var_list[i])[stock].resample(
        #             'BM').last()
        #         stock_risk_dic[f'2{self.decomp_names[i]} iVol'] = np.sqrt(self.idio_var_list[i])[stock].resample(
        #             'BM').last()
        #         stock_w, risk_managed_performance = self._get_stock_risk_control_result(stock_code=stock,
        #                                                                                 target_vol=0.1)
        #         stock_risk_dic[f'4{self.decomp_names[i]} weight'] = stock_w[i].resample('BM').last()
        #         stock_risk_dic[f'5{self.decomp_names[i]} performance'] = risk_managed_performance[i].resample(
        #             'BM').last()
        #     df = pd.DataFrame(stock_risk_dic).asfreq('BM', method='pad')  # .truncate(before=start) # 就不要截断了
        #     df.index = pd.to_datetime(df.index.astype('str'))
        #     df = df[df.columns.sort_values()]
        #     df_dic[stock] = df
        return df_dic

    def get_all_stock_report(self) -> Dict:
        """
        # total_var_list, idio_var_list, px_close, name_list, stocks
        输入close、return、stock_vol返回 df_dic,提供所有个股风控报告
        """
        rolling_vol = (np.log(self.px_close).diff(5).replace(0.0, np.nan)) \
                          .rolling(window=63, min_periods=21).std().shift(-63) * np.sqrt(52)
        stocks = set(self.risk_decomp[0].factor_quad.psi_ts['code'])
        full_df_dic = {}
        for stock in stocks:
            try:

                stock_risk_dic = {'0Close': self.px_close[stock],
                                  '3Forward_3M_Vol': rolling_vol[stock]}
                for i in range(len(self.decomp_names)):
                    stock_risk_dic[f'1{self.decomp_names[i]}_Vol'] = np.sqrt(self.total_var_list[i])[stock]
                    stock_risk_dic[f'2{self.decomp_names[i]}_iVol'] = np.sqrt(self.idio_var_list[i])[stock]
                    stock_risk_dic[f'4{self.decomp_names[i]}_iVol_pct'] = np.sqrt(self.idio_var_list[i])[stock] / \
                                                                          np.sqrt(self.total_var_list[i])[stock]
                df = pd.DataFrame(stock_risk_dic)
                df.index = pd.to_datetime(df.index.astype('str'))
                df = df[df.columns.sort_values()]
                full_df_dic[stock] = df
            except:
                print('stcok ' + stock + ' haven`t ipo')
        return full_df_dic

    def get_portfolio_report(self) -> pd.DataFrame:
        """
        # total_var_list, idio_var_list, px_close, name_list, stocks
        输入close、return、stock_vol返回 df_dic,提供个股风控报告
        """
        protfolio_w, risk_managed_performance = self._get_portfolio_risk_control_result(target_vol=0.1)
        for i in range(len(protfolio_w)):
            protfolio_w[i].columns = self.decomp_names[i] + '_' + protfolio_w[i].columns
        risk_managed_performance = pd.concat(risk_managed_performance, axis=1)
        risk_managed_performance.columns = pd.Series(self.decomp_names) + ': Pfm'
        portfolio_report = pd.concat(protfolio_w + [risk_managed_performance], axis=1)
        return portfolio_report

    def get_pure_portfolio_report(self) -> pd.DataFrame:
        """
        # total_var_list, idio_var_list, px_close, name_list, stocks
        输入close、return、stock_vol返回 df_dic,提供个股风控报告
        """
        protfolio_w, _ = self._get_portfolio_risk_control_result(target_vol=0.1)
        for i in range(len(protfolio_w)):
            protfolio_w[i].columns = self.decomp_names[i] + '_' + protfolio_w[i].columns
        portfolio_report = pd.concat(protfolio_w, axis=1)
        return portfolio_report

    def adjust_table_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        调整报告数据输出格式
        """
        df.index = df.index.astype('str')
        df = df.reset_index()
        return df


def get_risk_report(report_output_path=None):
    """
    提供给客户，风控报告输出
    """
    model_list = StocksOutputReport.compare_model  # 目前的数值为 ['we']
    start = StocksOutputReport.start
    end = StocksOutputReport.end
    risk_decomp_list = []  # 先开一个空的list，用来存储所有的结果
    for model in model_list:  # 生成 decompose 对象
        myquad = FactorQuadEQ.create_factor_quad(factor_system=eval(f'StocksOutputReport.{model}_factor_case_name'),
                                                 start_date=StocksOutputReport.start,
                                                 end_date=StocksOutputReport.end,
                                                 from_src=StocksOutputReport.from_local,
                                                 local_path=settings.seadrive_local_path)
        myquad.capped_psi_adjustment()
        from we_factor_quad.data_api import get_px_close
        # 基本测试信息的导入
        # 客户购买wiserdata数据api或使用自己数据获取px_close，通过data_api获取数据
        px_close = get_px_close(start, end)
        # 确保px_close数据格式类型正确
        assert (px_close.dtypes == float).all(), 'get_px_close获取到的数据包含非float类型的列，请检查该函数返回结果'
        mydecomp = RiskDecomposition(factor_quad=myquad, stock_ret_df=px_close)  # 在这里就应该指定和选择了
        risk_decomp_list.append(mydecomp)

    stocks = list(StocksOutputReport.report_stock_codes)
    stock_portfolio = StocksOutputReport.risk_control_portfolio
    stock_names = list(StocksOutputReport.report_stock_names)

    px_close = get_px_close(start, end)
    if report_output_path is None:
        report_output_path = StocksOutputReport.report_path
    my_compare_report = CompareReports(decomp_names=model_list, risk_decomp=risk_decomp_list, px_close=px_close,
                                       stocks=stocks, stock_names=stock_names, stock_portfolio=stock_portfolio)
    # 由这个report来负责生成仅需要因子数据的各种报告
    import os
    my_compare_report.get_reports(report_contents="stock_vol",
                                  output_file=os.path.join(report_output_path, "stock_risk_report.xlsx"))


# ----------------------
# 各种测试样例
def test_RiskControl():
    """
    测试风控报告输出
    """

    # 基本测试信息的导入
    # 客户购买wiserdata数据api或使用自己数据获取px_close，通过data_api获取数据
    start = StocksOutputReport.start
    end = StocksOutputReport.end
    local_path = settings.seadrive_local_path
    model_list = StocksOutputReport.compare_model  # 目前的数值为 ['we']

    def test_get_simple_report(model_list: List):
        # 提取所有quad by quad_name, 这是为了测试对象准备样例数据
        risk_decomp_list = []  # 先开一个空的list，用来存储所有的结果
        for model in model_list:  # 生成 decompose 对象
            myquad = FactorQuadEQ.create_factor_quad(factor_system=eval(f'StocksOutputReport.{model}_factor_case_name'),
                                                     start_date=StocksOutputReport.start,
                                                     end_date=StocksOutputReport.end,
                                                     from_src=StocksOutputReport.from_local,
                                                     local_path=settings.seadrive_local_path)
            myquad.capped_psi_adjustment()
            from we_factor_quad.data_api import get_px_close

            # 基本测试信息的导入
            # 客户购买wiserdata数据api或使用自己数据获取px_close，通过data_api获取数据
            start = StocksOutputReport.start
            end = StocksOutputReport.end
            px_close = get_px_close(start, end)

            mydecomp = RiskDecomposition(factor_quad=myquad, stock_ret_df=px_close)  # 在这里就应该指定和选择了
            risk_decomp_list.append(mydecomp)

        stocks = list(StocksOutputReport.report_stock_codes)
        stock_portfolio = StocksOutputReport.risk_control_portfolio
        stock_names = list(StocksOutputReport.report_stock_names)

        # 基本测试信息的导入
        # 客户购买wiserdata数据api或使用自己数据获取px_close，通过data_api获取数据
        start = StocksOutputReport.start
        end = StocksOutputReport.end
        px_close = get_px_close(start, end)
        report_path = StocksOutputReport.report_path
        my_compare_report = CompareReports(decomp_names=model_list, risk_decomp=risk_decomp_list, px_close=px_close,
                                           stocks=stocks, stock_names=stock_names, stock_portfolio=stock_portfolio)
        # 由这个report来负责生成仅需要因子数据的各种报告
        import os
        my_compare_report.get_reports(report_contents="stock_vol",
                                      output_file=os.path.join(report_path, "stock_risk_report.xlsx"))
        my_compare_report.get_reports(report_contents="all_stock_vol",
                                      output_file=os.path.join(report_path, "all_stock_report.xlsx"))
        my_compare_report.get_reports(report_contents="sys_idio",
                                      output_file=os.path.join(report_path, "stock_risk_report1.xlsx"))
        my_compare_report.get_reports(report_contents="factor_vol",
                                      output_file=os.path.join(report_path, "stock_risk_report2.xlsx"))
        my_compare_report.get_reports(report_contents="volatility",
                                      output_file=os.path.join(report_path, "stock_risk_report3.xlsx"))
        my_compare_report.get_reports(report_contents="rmv_vov",
                                      output_file=os.path.join(report_path, "stock_risk_report4.xlsx"))
        my_compare_report.get_reports(report_contents=["rmv_vov", "stock_vol"],
                                      output_file=os.path.join(report_path, "stock_risk_report6.xlsx"))
        my_compare_report.get_reports(report_contents="pure_portfolio",
                                      output_file=os.path.join(report_path, "portfolio_risk_report.xlsx"))
        my_compare_report.get_reports(report_contents="portfolio",
                                      output_file=os.path.join(report_path, "full_portfolio_risk_report.xlsx"))
        my_compare_report.get_reports(report_contents="full",
                                      output_file=os.path.join(report_path, "full_stock_risk_report.xlsx"))

    def test_output_on_one_quad():
        # 只有一个quad 的报告生成
        pass

    def test_on_some_stocks_multiple_quads():
        # 多个quad，多个指定的股票的报告生成
        pass

    # --------------------
    # 正常情况的测试
    test_get_simple_report(model_list=model_list)  # 多个quad，所有股票，都有数据

    # 各种异常情况的处理
    # 1. 只有1个quad，没有多个quad
    test_output_on_one_quad()
    # 2. 有多个quad，但是只生成指定的部分股票的数据
    test_on_some_stocks_multiple_quads()


# ----------------------
# 无行情数据的测试
def test_pure_RiskControl():
    """
    测试风控报告输出
    """

    # 基本测试信息的导入
    # 客户购买wiserdata数据api或使用自己数据获取px_close，通过data_api获取数据
    start = StocksOutputReport.start
    end = StocksOutputReport.end
    local_path = settings.seadrive_local_path
    model_list = StocksOutputReport.compare_model  # 目前的数值为 ['we']

    def test_get_simple_report(model_list: List):
        # 提取所有quad by quad_name, 这是为了测试对象准备样例数据
        risk_decomp_list = []  # 先开一个空的list，用来存储所有的结果
        for model in model_list:  # 生成 decompose 对象
            myquad = FactorQuadEQ.create_factor_quad(factor_system=eval(f'StocksOutputReport.{model}_factor_case_name'),
                                                     start_date=StocksOutputReport.start,
                                                     end_date=StocksOutputReport.end,
                                                     from_src=StocksOutputReport.from_local,
                                                     local_path=local_path)
            myquad.capped_psi_adjustment()

            # 基本测试信息的导入
            # 不需要px_close
            mydecomp = RiskDecomposition(factor_quad=myquad)  # 在这里就应该指定和选择了
            risk_decomp_list.append(mydecomp)

        stocks = list(StocksOutputReport.report_stock_codes)
        stock_portfolio = StocksOutputReport.risk_control_portfolio
        stock_names = list(StocksOutputReport.report_stock_names)

        # 基本测试信息的导入
        # 客户购买wiserdata数据api或使用自己数据获取px_close，通过data_api获取数据
        report_path = StocksOutputReport.report_path
        my_compare_report = CompareReports(decomp_names=model_list, risk_decomp=risk_decomp_list, px_close=None,
                                           stocks=stocks, stock_names=stock_names, stock_portfolio=stock_portfolio)
        # 由这个report来负责生成各种报告，按照定制化要求，想要什么样的报告，就生成什么样的报告
        import os
        my_compare_report.get_reports(report_contents="pure_portfolio",
                                      output_file=os.path.join(report_path, "portfolio_risk_report.xlsx"))

    def test_output_on_one_quad():
        # 只有一个quad 的报告生成
        pass

    def test_on_some_stocks_multiple_quads():
        # 多个quad，多个指定的股票的报告生成
        pass

    # --------------------
    # 正常情况的测试
    test_get_simple_report(model_list=model_list)  # 多个quad，所有股票，都有数据


if __name__ == '__main__':
    # test_RiskControl()
    get_risk_report()
    # test_pure_RiskControl()
