# 核心考察的，是使用指定的因子组，来对指定对象(指定的指数)进行风险控制，考察的内容是3个点
# 1. 能不能总体上控得住，
# 2. 能不能一直控得住，
# 3. 控制下的偏离不能太远
import pandas as pd
from we_factor_quad.equity_quad.factor_quad_equity import FactorQuadEQ
from typing import Union, List, Dict
from we_factor_quad.factor_quad_settings import StocksOutputReport
from we_factor_quad.factor_quad_settings import settings
import we_factor_quad.data_api as data_api
from we_factor_quad.equity_quad.risk_control.stock_risk_control import RiskDecomposition, CompareReports


class CompareReportsPortfolio(CompareReports):
    """
    基于 portfolio 的风险控制报告的生成，继续参照 CompareReports 的报告控制方法
    """

    def __init__(self, decomp_names: List[str], risk_decomp: List[RiskDecomposition],
                 px_close: pd.DataFrame, stock_portfolio: Union[pd.DataFrame, Dict] = None):
        super().__init__(decomp_names=decomp_names, risk_decomp=risk_decomp, px_close=px_close,
                         stock_portfolio=stock_portfolio)


# ---------------
# 测试样例


def test_risk_decomposition_index():
    start_dt = '2020-01-01'
    end_dt = '2022-11-01'
    index_code_map = settings.index_code_map
    target_vol = 0.1  # 期望的波动率
    local_path = settings.seadrive_local_path
    model_list = StocksOutputReport.compare_model  # 目前的数值为 ['we', 'barra']

    def test_get_index_report(model_list: List):
        px_close = data_api.get_px_close((pd.to_datetime(start_dt) - pd.DateOffset(months=1)).strftime('%Y%m%d'),
                                         end_dt)
        ret = px_close.asfreq('BM', method='pad').pct_change(periods=1).dropna(axis=0, how='all')
        risk_decomp_list = []
        for model in model_list:
            myquad = FactorQuadEQ.create_factor_quad(factor_system=eval(f'StocksOutputReport.{model}_factor_case_name'),
                                                     start_date=StocksOutputReport.start,
                                                     end_date=StocksOutputReport.end,
                                                     from_src=StocksOutputReport.from_local,
                                                     local_path=local_path)
            myquad.capped_psi_adjustment()  # todo 确定是要计算 capped_psi() 的吧
            ret.index = ret.index.to_period('M').start_time
            mydecomp = RiskDecomposition(
                factor_quad=myquad, stock_ret_df=ret.reindex(myquad.date_list, method='pad').fillna(0.))  # 在这里就应该指定和选择了
            risk_decomp_list.append(mydecomp)

        # 提取portfolio 中的stock的价格与权重
        # portfolio_data load
        ptfl_w = data_api.load_stock_index_weight(index_code_map, data_api.ths_a_share_code_map(),
                                                  start_dt, end_dt, freq='BM')

        # 生成报告
        myreport = CompareReportsPortfolio(decomp_names=model_list, risk_decomp=risk_decomp_list, px_close=px_close,
                                           stock_portfolio=ptfl_w['000852.SH'])
        myreport.get_reports(report_contents=['sys_idio', 'factor_vol', 'volatility', 'rmv_vov'],
                             output_file="D:/index_risk_report.xlsx")

    test_get_index_report(model_list)


if __name__ == '__main__':
    test_risk_decomposition_index()
