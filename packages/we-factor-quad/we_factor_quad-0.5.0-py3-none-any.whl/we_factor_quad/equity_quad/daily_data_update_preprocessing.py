import os
from copy import copy, deepcopy
import pandas as pd
import numpy as np
from we_factor_quad.equity_quad.factor_quad_equity import FactorQuadEQ
from we_factor_quad.equity_quad.factor_portfolio.full_factor_mimicking_portfolio import FmpAnalyzer
import we_factor_quad.data_api as dapi
from we_factor_quad.factor_quad_settings import FmpUniverseConfig, settings


def get_filled_psi(start_date,
                   end_date,
                   daily_return: pd.DataFrame = None,
                   factor_system: str = "HF25_SRAM_DAILY",
                   from_src: int = 3,
                   local_path: str = "D:/jiaochayuan_files/projects/we_factor_quad_/we_factor_quad/equity_quad/",
                   seadrive_localpath='D:\seadrive_cache_folder\zhouly\群组资料库'):
    """
    应该是输入一个要更新日期+前5个工作日(共6天)的asset return和用要更新日期+前一天的factorquad，然后输出一个填过的psi
    Args:
        local_path: 用来存放csv新增四元组数据的根文件夹地址，比如HF25_SRAM_DAILY这个文件夹的所在文件夹
        from_src: 3指用csv版本四元组数据生成factorquad
        factor_system: 用来存放csv新增四元组数据的根文件夹名字，比如“HF25_SRAM_DAILY”
        end_date: 生成factorquad的结束日期
        start_date:生成factorquad的起始日期
        daily_return: 当日和前6日的日股票收益率，必须是宽表，行为日期，列为股票。如果这个参数是None，那么将会自动从数据库里取return数据
        seadrive_localpath:

    Returns:
    """
    delta_time = (pd.Timestamp(end_date) - pd.Timestamp(start_date)).days
    # ====================================这里日后要改成通过csv生成factorquad================================================
    quad = FactorQuadEQ.create_factor_quad(start_date=start_date,
                                           end_date=end_date,
                                           factor_system=factor_system,
                                           from_src=from_src,
                                           local_path=local_path)
    # ==================================================================================================================
    beta_ts, psi_ts = deepcopy(quad.beta_ts), deepcopy(quad.psi_ts)
    beta_ts["code"] = ["CN" + x.split(".")[0] for x in beta_ts["code"]]
    psi_ts["code"] = ["CN" + x.split(".")[0] for x in psi_ts["code"]]
    beta = beta_ts.sort_values(by=["date", "code"])[["date", "code"] +
                                                    settings.msg_factors_name].set_index(["date", "code"])
    psi = psi_ts[["date", "code", 'var']].sort_values(by=["date", "code"]).set_index(["date", "code"])

    status = ((beta != 0.0).sum(axis=1)) == 0.0
    # 已上市股票的beta和psi
    valid_index = list(status[status == 0.0].index)
    valid_psi = psi[psi.index.isin(valid_index)]
    valid_beta = beta[beta.index.isin(valid_index)]

    # 看风格因子是否三个以上为0
    condition = (valid_beta == 0).sum(axis=1) >= 3
    condition_index = condition[condition == True].index
    nan_psi = valid_psi[valid_psi.index.isin(condition_index)]
    need_fill_index = nan_psi[nan_psi['var'].isna()]

    # 如果没有psi需要被填，那么直接返回一个空Dataframe
    if len(list(need_fill_index.index)) == 0:
        print("No missing psi to be filled!")
        return pd.DataFrame([])
    # =================================================================================================================
    ret_start = (quad.date_list[0] - pd.offsets.BDay(5)).strftime('%Y%m%d')
    ret_end = pd.Timestamp(quad.date_list[-1]).strftime('%Y%m%d')
    if not daily_return:
        _return = dapi.wiser_get_stock_return(start=ret_start,
                                              end=ret_end,
                                              sample_stk=[],
                                              factor_system="HF25_SRAM_DAILY",
                                              seadrive_localpath=seadrive_localpath,
                                              freq='B')
        _return2 = pd.read_csv("D:\jiaochayuan_files\projects\we_factor_quad_\we_factor_quad\equity_quad/return.csv",
                              index_col=0, parse_dates=True)
        _return2 = _return2.reindex(columns=sorted(list(set(_return.columns))), index=_return.index)
        _return = _return2
        # _return = _return.fillna(0.0)
        print(1)
    else:
        _return = deepcopy(daily_return)
    latest_date_return = _return.iloc[(-delta_time-1):, :]
    latest_date_return.index.name = "date"
    loc_noreturn = latest_date_return == 0.0
    fmp_obj = FmpAnalyzer(quad=quad)
    weights = fmp_obj.get_portfolio_weights(start_date=start_date,
                                            end_date=end_date,
                                            freq='B',
                                            universe_conf=FmpUniverseConfig.universe_config['default_universe'])

    _return = _return.rolling(5).sum().fillna(0.0)
    _return = _return.reindex(index=quad.date_list)
    total_return_filter = ((_return == 0.0) + loc_noreturn) >= 1
    factor_return = fmp_obj.construct_factor_return(weights_df=weights, ret=_return)

    revive_beta_with_scale(quad=quad, hetero_adj=True)
    _return = revive_stock_ret_with_scale(quad=quad, ret=_return)
    total_return_filter = total_return_filter.replace(True, np.nan).replace(False, 1.0)
    sys_return, res_return = fmp_obj.factor_decompose_asset_return(factor_return=factor_return,
                                                                   stock_ret=_return)
    total_return_filter = total_return_filter.reindex(columns=res_return.columns, index=res_return.index)
    res_return = res_return * total_return_filter
    all_psi = ((res_return ** 2 * 52).ewm(com=0.003).mean()).stack(dropna=False)

    filled_nan_psi = all_psi[all_psi.index.isin(need_fill_index.index)]
    filled_nan_psi = filled_nan_psi.replace(0.0, np.nan).dropna()
    filled_nan_psi.index.names = ['date', 'code']

    if filled_nan_psi.shape[0] == 0:
        return pd.DataFrame([])
    else:
        return filled_nan_psi.unstack()


def revive_beta_with_scale(quad: FactorQuadEQ,
                           hetero_adj=False):
    """
    将beta除以1/scale的平均值，以还原beta
    Args:
        hetero_adj:
        quad:

    Returns:
    """
    scale_inverse = deepcopy(quad.scale_ts)
    scale_inverse['scale'] = 1 / scale_inverse['scale']
    ave_scale_inverse = scale_inverse.groupby(by='date').transform("mean")
    reviving_beta = quad.beta_ts.set_index(['date', 'code'])
    ave_scale_inverse.index = reviving_beta.index
    # ==========================
    if not hetero_adj:
        np_operation = reviving_beta.values / ave_scale_inverse.values.reshape(-1, 1)
    else:
        np_operation = reviving_beta.values / scale_inverse['scale'].values.reshape(-1, 1)
    # =========================
    quad.beta_ts = pd.DataFrame(data=np_operation,
                                index=reviving_beta.index,
                                columns=reviving_beta.columns).reset_index(drop=False)


def revive_stock_ret_with_scale(quad: FactorQuadEQ,
                                ret: pd.DataFrame):
    """
    将stock return除以1/scale的平均值
    Args:
     quad:
     ret:

    Returns:
    """
    scale_inverse = (1 / deepcopy(quad.scale_ts)[['date', 'code', 'scale']].pivot(index='date',
                                                                                  columns='code',
                                                                                  values='scale'))
    scale_inverse.sort_index(inplace=True)
    scale_inverse.columns = ["CN" + x.split(".")[0] for x in scale_inverse.columns]
    scale_inverse = scale_inverse.reindex(columns=ret.columns)
    np_operation = ret.values / scale_inverse.values
    new_ret = pd.DataFrame(data=np_operation,
                           index=ret.index,
                           columns=ret.columns)
    return new_ret


def map_code(code_cn: str):
    """
    将CNxxxxxx形式的股票代码转成xxxxxx.xx形式
    Args:
        code_cn:

    Returns:
    """
    if code_cn[2] == "6":
        new_code = f"{code_cn[2:]}.SH"
    elif code_cn[2] == "0" or "3":
        new_code = f"{code_cn[2:]}.SZ"
    elif code_cn[2] == "8":
        new_code = f"{code_cn[2:]}.BJ"
    else:
        raise ValueError("stock code does not exist!")
    return new_code


if __name__ == "__main__":

    get_filled_psi(start_date="20210629",
                   end_date="20210630",
                   daily_return=None,
                   seadrive_localpath='D:\zhouly\群组资料库')