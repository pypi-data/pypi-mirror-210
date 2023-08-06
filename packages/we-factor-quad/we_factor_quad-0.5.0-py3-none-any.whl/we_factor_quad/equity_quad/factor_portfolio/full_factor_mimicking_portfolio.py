# 给定一个由任意个市场指数混合的股票universe，和股票的factor quad，计算所有因子的factor return, 计算任意多个股票的residual return
# 生成一个报告，包括
# 1. 单因子accumulated factor return的时间序列及图
# 2. summary stats
import copy
import warnings
from typing import Dict, AnyStr, List
from matplotlib import pyplot as plt, ticker
from we_report.interface.excel_reporter import ExcelReport as Ereporter
from we_report.data_type.report_data import PageData, ReportData
import we_factor_quad.data_api as dapi
from we_factor_quad.utils import summary_stats
import we_factor_quad.equity_quad.factor_portfolio.universe_helper as uhelper
from we_factor_quad.equity_quad.factor_quad_equity import FactorQuadEQ
from we_factor_quad.factor_quad_settings import FmpUniverseConfig, settings
import pandas as pd
import numpy as np
warnings.filterwarnings('ignore')


class FmpAnalyzer:
    """
    这个类里面集成了以下功能
    1. 计算所有因子的factor return
    2. 计算任意多个股票的residual return
    # 生成一个报告，包括
    # 1. 单因子accumulated factor return的时间序列及图
    # 2. summary stats
    """
    def __init__(self,
                 quad: FactorQuadEQ,
                 _code_col_name='code',
                 _time_col_name='date'):

        self.start_date = pd.to_datetime(quad.date_list[0]).replace(day=1).strftime('%Y%m%d')
        self.end_date = pd.to_datetime(quad.date_list.max()).to_period('M').to_timestamp('D', how='E').strftime('%Y%m%d')
        self.quad = quad
        self.code_col_name = _code_col_name
        self.time_col_name = _time_col_name
        self.factor_names = list(quad.sigma_ts.columns[2:])

    def construct_factor_return(self,
                                weights_df: pd.DataFrame,
                                ret: pd.DataFrame) -> pd.DataFrame:
        """
        weights中包含universe的信息，不必再传进来universe了
        Args:
            ret: 可以是monthly的或daily的
            weights_df: factor mimicking portfolio weights

        Returns:
        """

        weights_df = weights_df.set_index([self.time_col_name, "factors"]).loc[:, (weights_df != 0).any(axis=0)].reset_index(
            drop=False)
        renamed_universe_cols = ["CN" + x.split('.')[0] for x in list(weights_df.columns) if len(x.split('.')) > 1]
        monthly_return = ret[renamed_universe_cols]
        monthly_return = monthly_return.reindex(index=sorted(list(set(weights_df[self.time_col_name]))), method='pad')
        rename_map = list(weights_df.columns)[:2] + renamed_universe_cols
        weights_renamed = weights_df.rename(columns=dict(zip(weights_df.columns, rename_map)))
        factor_num = len(set(weights_df['factors']))
        factor_names_preserved = list(weights_df['factors'])[:factor_num]
        monthly_return.index.name = self.time_col_name
        _monthly_return = monthly_return.reset_index(drop=False)
        repeated_monthly_return = pd.DataFrame(data=np.repeat(_monthly_return.values,
                                                              repeats=factor_num, axis=0),
                                               columns=_monthly_return.columns)
        repeated_monthly_return['factors'] = weights_renamed['factors']
        monthly_return_to_use = repeated_monthly_return.set_index([self.time_col_name, 'factors']).dropna(how='all')
        # 下面等于是shift了weights
        weights_to_use = weights_renamed.set_index([self.time_col_name, 'factors']).shift(factor_num).dropna(how='all')
        if len(factor_names_preserved) == weights_to_use.shape[0]:
            unstacked_factor_return = (weights_to_use * monthly_return_to_use.loc[weights_to_use.index]).sum(axis=1) \
                .unstack()
        else:
            unstacked_factor_return = weights_to_use.groupby(level=[0]) \
                .apply(lambda x: (x * monthly_return_to_use.loc[x.index]).sum(axis=1)).unstack() \
                .reset_index(level=1, drop=True)[factor_names_preserved]

        return unstacked_factor_return

    def factor_decompose_asset_return(self,
                                      factor_return: pd.DataFrame,
                                      stock_ret: pd.DataFrame,
                                      stock_universe: list = []) -> (pd.DataFrame, pd.DataFrame):
        """

        Args:
            stock_ret: 可以是任意频率的return
            factor_return:
            stock_universe: 表示需要计算sys和residual的股票代码， 格式是"CNXXXXXX"

        Returns:
        """
        sigma_ts_wc, original_beta_withcountry = self.quad.add_country_factor()
        original_beta_withcountry_copy = copy.deepcopy(original_beta_withcountry)
        original_beta_withcountry_copy[self.code_col_name] = ['CN' + x.split(".")[0] for x in
                                                              original_beta_withcountry_copy[self.code_col_name]
                                                              if len(x.split(".")) > 1]

        if len(stock_universe) > 0:
            monthly_return = stock_ret[stock_universe]
            universe_filtered_beta_ts = original_beta_withcountry_copy[
                original_beta_withcountry_copy[self.code_col_name].isin(stock_universe)].reset_index(drop=True)
        else:
            monthly_return = stock_ret
            universe_filtered_beta_ts = original_beta_withcountry_copy
        universe_filtered_beta_ts = universe_filtered_beta_ts.sort_values(
            by=[self.time_col_name, self.code_col_name]).reset_index(drop=True)
        all_stocks = sorted(list(set(universe_filtered_beta_ts[self.code_col_name])))
        all_dates = sorted(list(set(universe_filtered_beta_ts[self.time_col_name])))
        allstock_monthly_return = monthly_return.reindex(index=all_dates, method='pad')
        allstock_monthly_return = allstock_monthly_return.reindex(columns=all_stocks)
        stock_num = len(allstock_monthly_return.columns)
        first_date_length = universe_filtered_beta_ts[universe_filtered_beta_ts[self.time_col_name] == all_dates[0]].shape[0]
        repeated_factor_return = pd.DataFrame(data=np.repeat(factor_return.reset_index(drop=False).values,
                                                             repeats=stock_num, axis=0),
                                              columns=[factor_return.index.name] + list(factor_return.columns))
        # 下面等于是shift了beta
        beta_to_use = universe_filtered_beta_ts.set_index([self.time_col_name, self.code_col_name]).shift(
            first_date_length).dropna(how='all')
        if beta_to_use.shape[0] != repeated_factor_return.shape[0]:
            multiindex = allstock_monthly_return.dropna(how='all').stack(dropna=False).index
            beta_to_use = beta_to_use.reindex(index=multiindex)
            beta_to_use.index.names = (self.time_col_name, self.code_col_name)
        repeated_factor_return[self.code_col_name] = beta_to_use.reset_index()[self.code_col_name]
        factor_return_to_use = repeated_factor_return.set_index([self.time_col_name, self.code_col_name])
        beta_to_use = beta_to_use.reindex(columns=factor_return_to_use.columns)
        if factor_return.shape[0] == 1:
            sys_return = (beta_to_use * factor_return_to_use).sum(axis=1).unstack()
        else:
            sys_return = beta_to_use.groupby(level=[0]) \
                .apply(lambda x: (x * factor_return_to_use.loc[x.index]).sum(axis=1)).unstack() \
                .reset_index(level=1, drop=True)
        residual_return = allstock_monthly_return.iloc[1:, :] - sys_return
        return sys_return, residual_return

    def construct_all_factor_performances(self,
                                          factor_return: pd.DataFrame) -> dict:
        """
        储存并生成一个excel sheet里面含有单因子的accumulated factor return 的 time series和相应的线图
        Args:
            factor_return:


        Returns:
        """
        import seaborn as sns
        sns.set_style("darkgrid")
        page_names = []
        pages = []
        for factor_name in self.factor_names:
            factor_return_ts = (factor_return[[factor_name]].cumsum()).reset_index()
            factor_return_ts[self.time_col_name] = pd.to_datetime(factor_return_ts[self.time_col_name], unit='s')
            ax1 = sns.lineplot(data=factor_return_ts, x="date", y=factor_name)
            ax1.set_title(f"{factor_name} accumulated factor return")
            ax1.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1, decimals=1))
            line_figure = ax1.get_figure()
            line_figure.savefig(f"{factor_name}_accumulated_factor_return.png", dpi=500)
            plt.clf()
            page = PageData(tables=[factor_return_ts],
                            fig_paths=[f"{factor_name}_accumulated_factor_return.png"],
                            fig_size=[600, 700])
            pages.append(page)
            page_names.append(factor_name)
        # excel sheet name长度不能超过30
        page_names = [x[0: 30] if len(x) > 30 else x for x in page_names]
        report_dict = dict(zip(page_names, pages))
        return report_dict

    def construct_universe(self,
                           universe_identifier: tuple[str],
                           start_date: str,
                           end_date: str,
                           original_psi_ts: pd.DataFrame,
                           rename_mapping=None,
                           freq='BM'):
        universe = dapi.load_universe(universe_identifier=universe_identifier,
                                      start_date=start_date,
                                      end_date=end_date,
                                      rename_mapping=rename_mapping,
                                      freq=freq)
        pivoted_psi = original_psi_ts.pivot(index=self.time_col_name, columns=self.code_col_name, values="var")

        pivoted_psi = pivoted_psi.reindex(columns=universe.columns)
        pivoted_psi = pivoted_psi * 0 + 1
        universe = universe.reindex(index=pivoted_psi.index, method='nearest')
        updated_universe = universe * pivoted_psi
        return updated_universe


    def get_portfolio_weights(self,
                              start_date: str,
                              end_date: str,
                              universe_conf=FmpUniverseConfig.universe_config['default_universe'],
                              manual_universe=pd.DataFrame([]),
                              freq='BM'):
        """
        用来在本地直接计算factor mimicking portfolio weights， 比较慢，但是可以输入任意在universe_config里定义的universe
        Args:
            manual_universe: 直接由客户输入的一个行名是每月最后一个交易日，列名是形为CNxxxxxx股票名的Dataframe，时间数量(行数)必须和quad相等，
            股票数量(列数)必须是所有时间
            start_date:
            end_date:
            universe_conf: 在universe_config里定义的由多个指数叠加生成的universe

        Returns:

        """

        # add country factor to sigma and beta
        sigma_ts_wc, beta_ts_wc = self.quad.add_country_factor()
        preserved_cols = sorted(list(set(beta_ts_wc[self.code_col_name])))
        if manual_universe.shape[0] == 0:
            universe = self.construct_universe(universe_identifier=universe_conf,
                                               start_date=start_date,
                                               end_date=end_date,
                                               rename_mapping={i.split('.')[0]: i for i in
                                                               np.unique(beta_ts_wc.loc[:, self.code_col_name])},
                                               original_psi_ts=self.quad.psi_ts,
                                               freq=freq)
        else:
            universe = copy.copy(manual_universe)
        universe_quad = universe.reindex(index=self.quad.date_list, method='pad')
        beta_ts_wc_filtered = uhelper.apply_universe_filter(beta_ts_wc,
                                                            universe=universe_quad,
                                                            raw_cols=[self.time_col_name, self.code_col_name])

        psi_ts_filtered = uhelper.apply_universe_filter(self.quad.psi_ts,
                                                        universe=universe_quad,
                                                        raw_cols=[self.time_col_name, self.code_col_name])

        dates_toloopover = sorted(list(set(beta_ts_wc_filtered[self.time_col_name])))
        factors = list(beta_ts_wc_filtered.columns)[2:]
        multiindex = pd.MultiIndex.from_product([dates_toloopover, factors], names=[self.time_col_name, 'factors'])
        weights_df = pd.DataFrame([])

        # to be accelerated
        date_num = 1
        for date in dates_toloopover:
            codes = list(beta_ts_wc_filtered[beta_ts_wc_filtered[self.time_col_name] == date][self.code_col_name])
            time_group_beta = beta_ts_wc_filtered[beta_ts_wc_filtered[self.time_col_name] == date].values[:, 2:].astype(
                float)
            time_group_sigma = sigma_ts_wc[sigma_ts_wc[self.time_col_name] == date].values[:, 2:].astype(float)
            time_group_psi = np.diag(
                np.squeeze(psi_ts_filtered[psi_ts_filtered[self.time_col_name] == date].values[:, -1])).astype(float)
            weights_part1 = time_group_sigma @ time_group_beta.T
            weights_part2 = np.linalg.inv((time_group_beta @ time_group_sigma @ time_group_beta.T) + time_group_psi)
            weights = weights_part1 @ weights_part2
            df_to_concat = pd.DataFrame(data=weights,
                                        index=multiindex[(date_num - 1) * len(factors): date_num * len(factors)],
                                        columns=codes)
            weights_df = pd.concat([weights_df, df_to_concat], axis=0)
            date_num += 1
        sorted_cols = sorted(list(weights_df.columns))
        weights_df = weights_df[sorted_cols].reindex(columns=preserved_cols).fillna(0.0).reset_index(drop=False)
        return weights_df


    def construct_summary_stats(self,
                                factor_return: pd.DataFrame):
        """

        Args:
            factor_return:

        Returns:

        """
        stats = summary_stats(ret=factor_return).round(3)
        page = PageData(tables=[stats])
        report_dict = dict(zip(["summary_stats"], [page]))
        return report_dict

    def output_report(self,
                      weights_df: pd.DataFrame,
                      monthly_ret: pd.DataFrame,
                      output_workbook_name: str = "factor_return_report.xlsx"):
        """

        Args:
            monthly_ret: 
            weights_df: 
            output_workbook_name:

        Returns:

        """
        factor_returns = self.construct_factor_return(weights_df=weights_df, ret=monthly_ret)
        performance_dict = self.construct_all_factor_performances(factor_return=factor_returns)
        stats_dict = self.construct_summary_stats(factor_return=factor_returns)
        performance_dict.update(stats_dict)
        report = ReportData(performance_dict)
        Ereporter.output_report(report, output_workbook_name)

    def save_to_csv(self, seadrive_localpath: AnyStr, dir: AnyStr=None):
        """
        用quad计算factor return, systematic return, residual return，保存为csv文件
        """

        monthly_ret = dapi.wiser_get_stock_return(start=self.start_date, end=self.end_date,
                                                    seadrive_localpath=seadrive_localpath)
        weights_df = dapi.wiser_fetch_fmp_weights(start_date=self.start_date, end_date=self.end_date,
                                                  seadrive_localpath=seadrive_localpath)
        factor_return = self.construct_factor_return(ret=monthly_ret, weights_df=weights_df)
        sys, residual = self.factor_decompose_asset_return(stock_ret=monthly_ret, factor_return=factor_return)
        import os
        if dir is None:
            dir = os.path.dirname(__file__)
        factor_return.to_csv(os.path.join(dir, "factor_return.csv"))
        sys.to_csv(os.path.join(dir, "sys_return.csv"))
        residual.to_csv(os.path.join(dir, "residual_return.csv"))

def test_fmp_process():

    def test_fmp1():
        start_date = "20200101"
        end_date = "20230131"
        seadrive_localpath = settings.seadrive_local_path
        quad = FactorQuadEQ.create_factor_quad(start_date=start_date, end_date=end_date, factor_system="HF25_SRAM", local_path=seadrive_localpath)
        analyzer = FmpAnalyzer(quad)
        monthly_ret = dapi.wiser_get_stock_return(start=start_date, end=end_date, seadrive_localpath=seadrive_localpath)
        weights_df = dapi.wiser_fetch_fmp_weights(start_date=start_date, end_date=end_date,
                                                  seadrive_localpath=seadrive_localpath)
        factor_return = analyzer.construct_factor_return(ret=monthly_ret, weights_df=weights_df)
        sys, residual = analyzer.factor_decompose_asset_return(stock_ret=monthly_ret, factor_return=factor_return)

    def test_fmp2():
        start_date = "20130101"
        end_date = "20221031"
        seadrive_localpath = settings.seadrive_local_path
        quad = FactorQuadEQ.create_factor_quad(start_date=start_date, end_date=end_date, factor_system="HF25_SRAM",
                                               local_path=seadrive_localpath)
        analyzer = FmpAnalyzer(quad)
        monthly_ret = dapi.wiser_get_stock_return(start=start_date, end=end_date,
                                                    seadrive_localpath=seadrive_localpath)
        weights_df = dapi.wiser_fetch_fmp_weights(start_date=start_date, end_date=end_date,
                                                  seadrive_localpath=seadrive_localpath)
        factor_return = analyzer.construct_factor_return(ret=monthly_ret, weights_df=weights_df)
        sys, residual = analyzer.factor_decompose_asset_return(stock_ret=monthly_ret, factor_return=factor_return)
        # analyzer.output_report(weights_df=weights_df, monthly_ret=monthly_ret)

    def test_fmp3_alternative_universe():
        """
        不用seadrive，用数仓取下来的指数混合生成新的universe。不过由于不能提供给客户数仓，这个test只是用来检验是否可以手工输入一个universe来
        生成fmp weights，进而计算factor return, systematic return, residual return
        """
        start_date = "20130101"
        end_date = "20221031"
        seadrive_localpath = settings.seadrive_local_path
        quad = FactorQuadEQ.create_factor_quad(start_date=start_date, end_date=end_date, factor_system="HF25_SRAM",
                                               local_path=seadrive_localpath)
        analyzer = FmpAnalyzer(quad)
        monthly_ret = dapi.wiser_get_stock_return(start=start_date,
                                                  end=end_date,
                                                  seadrive_localpath=seadrive_localpath)
        weights_df = analyzer.get_portfolio_weights(start_date=start_date,
                                                    end_date=end_date,
                                                    universe_conf=FmpUniverseConfig.universe_config['alternative_universe'])
        factor_return = analyzer.construct_factor_return(ret=monthly_ret, weights_df=weights_df)
        sys, residual = analyzer.factor_decompose_asset_return(stock_ret=monthly_ret, factor_return=factor_return)
        # analyzer.output_report(weights_df=weights_df,
        #                        monthly_ret=monthly_ret,
        #                        output_workbook_name="factor_return_alter_universe")

    def test_fmp_to_csv():
        """
        将seadrive中的quad数据保存成csv文件，并用quad计算factor return, systematic return, residual return，保存为csv文件
        """
        quad = FactorQuadEQ.create_factor_quad(start_date="200000101", end_date="20221031", factor_system="HF25_SRAM",
                                               local_path=r'C:\Users\Administrator\seadrive_root\trial\case_HF25_SRAM')
        #若dir=None 默认保存到factor_quad_equity所在文件夹下
        quad.save_to_csv(dir=None)
        #若dir=None 默认保存到full_factor_mimicking_portfolio所在文件夹下
        FmpAnalyzer(quad).save_to_csv(r'C:\Users\Administrator\seadrive_root\trial\case_HF25_SRAM',dir=None)

    test_fmp1()
    test_fmp2()
    test_fmp3_alternative_universe()
    test_fmp_to_csv()

if __name__ == '__main__':
    test_fmp_process()
    # start_date = "20130101"
    # end_date = "20221031"
    # seadrive_localpath = settings.seadrive_local_path
    # quad = FactorQuadEQ.create_factor_quad(start_date=start_date, end_date=end_date, factor_system="HF25_SRAM",
    #                                        local_path=seadrive_localpath)
    # date_seq = pd.date_range(start=start_date, end=end_date, freq='B')
    # beta_ts = quad.beta_ts.reindex(index=date_seq).fillna(method='ffill')
    # psi_ts = quad.psi_ts.reindex(index=date_seq).fillna(method='ffill')
    # analyzer = FmpAnalyzer(quad)
    # weights_df = analyzer.get_portfolio_weights(start_date=start_date, end_date=end_date,freq='B',)
    # ret = dapi.wiser_get_stock_return(start=start_date,end=end_date,freq='B')
    # factor_return = analyzer.construct_factor_return(weights_df=weights_df, ret=ret)
