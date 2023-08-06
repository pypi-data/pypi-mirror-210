import pandas as pd
import os


class settings:
    # 这部分参数，用于生成报告
    # 因子四元组时间区间
    start_date = '20200701'
    end_date = '20210710'
    # 四元组数据来源，local是读本地pkl文件，remote为从wiserdata下载数据
    quad_from_local = 1
    # seadrive_local_path = r"D:\seadrive_cache_folder\zhouly\群组资料库"
    seadrive_local_path = r'C:\Users\Administrator\seadrive_root\gorilla\共享资料库'
    # seadrive_local_path = r'C:\Users\Administrator\Seafile'
    # seadrive_local_path = "D:/seadrive_files/xiazeyu/Shared with groups/"
    # we因子模型与要对比的barra模型 case名
    # msg_factor_case_name = 'HF25_SRAM_DAILY'
    msg_factor_case_name = 'HF25_SRAM_DAILY_Tsinghua_Internal_Usage'
    cufm_factor_case_name = '202211_PRE_BARRA'
    # we模型与barra模型风格因子名
    msg_factors_name = ['beta', 'ceg', 'dtop', 'etop', 'gpm', 'log_bp', 'log_markcap', 'log_st_mean', 'log_std', 'mbs',
                        'reversal_short', 'roe', 'rstr', 'tagr']
    cufm_factors_name = ['Beta', 'Book-to-Price', 'Dividend Yield', 'Earnings Quality', 'Earnings Variability',
                         'Earnings Yield', 'Growth', 'Investment Quality', 'Leverage', 'Liquidity',
                         'Long-Term Reversal',
                         'Mid Capitalization',
                         'Momentum', 'Profitability', 'Residual Volatility', 'Size']
    index_weight_file = ['', 'Baijiu_w.csv']
    index_ticker_list = ['000300.SH', '399997.CSI']
    index_truncate_before = ['2010-1', '2015-1']
    # report_stock_codes = ['605020.SH', '300834.SZ', '301068.SZ', '000002.SZ', '601398.SH', '002069.SZ', '600196.SH',
    #                       '002460.SZ', '600519.SH',
    #                       '600518.SH']
    # report_stock_names = ['605020.SH', '300834.SZ', '301068.SZ', '万科', '工商银行', '獐子岛', '复星医药', '赣锋锂业', '茅台', '康美药业',
    #                       '乐视']
    report_stock_codes = ['000002.SZ','601398.SH', '002069.SZ','600196.SH','002460.SZ', '600519.SH']
    report_stock_names = ['万科','工商银行', '獐子岛','复星医药','赣锋锂业', '茅台']
    # 传入dataframe表示投资组合权重随时间变化
    risk_control_portfolio = pd.DataFrame({'000001.SZ': [0.2, 0.3], '000002.SZ': [0.8, 0.7]},
                                          index=pd.to_datetime(['2012-01-01', '2023-02-01']))
    report_path = os.getcwd()

    # Factor Summary report
    factor_summary_start_date = '20210701'
    factor_summary_end_date = '20230101'
    factor_model = 'model_202209'
    factor_group = 'volatility'

    factor_group_start_date = '20220601'
    factor_group_end_date = '20221031'

    compare_model = ['msg']
    # 指数测试需要
    index_code_map = {
        # 同花顺内部代码 -> 常见形式代码
        'ind422': '000300.SH',
        'ind427': '000905.SH',
        'ind377': '000016.SH',
        'I06011': '000852.SH'
    }


class StocksOutputReport:
    start = settings.start_date
    end = settings.end_date
    from_local = settings.quad_from_local
    msg_factor_case_name = settings.msg_factor_case_name
    cufm_factor_case_name = settings.cufm_factor_case_name
    msg_factors_name = settings.msg_factors_name
    cufm_factors_name = settings.cufm_factors_name
    report_stock_codes = list(settings.report_stock_codes)
    report_stock_names = list(settings.report_stock_names)
    compare_model = settings.compare_model
    risk_control_portfolio = settings.risk_control_portfolio
    report_path = settings.report_path


class IndexOutputReport:
    ticker_list = settings.index_ticker_list
    truncate_before = settings.index_truncate_before
    weight_file = settings.index_weight_file


class IndexOutputReport:
    ticker_list = settings.index_ticker_list
    truncate_before = settings.index_truncate_before
    weight_file = settings.index_weight_file


class FmpUniverseConfig:
    """
    设定所有可用的universe，由多个指数叠加
    """
    universe_config = {'default_universe': ("ind422", "I06011", "I00275"),  # 沪深300，中证500 + 中证 1000
                       'alternative_universe': ("ind422",),
                       'all_universe': ("ind249", "I02551", "55000008", "I00127",)
                       }
