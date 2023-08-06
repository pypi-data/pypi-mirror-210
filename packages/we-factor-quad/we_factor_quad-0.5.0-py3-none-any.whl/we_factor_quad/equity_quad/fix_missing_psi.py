import os
from copy import copy, deepcopy
import pandas as pd
import numpy as np
from we_factor_quad.equity_quad.factor_quad_equity import FactorQuadEQ
from we_factor_quad.equity_quad.factor_portfolio.full_factor_mimicking_portfolio import FmpAnalyzer
import we_factor_quad.data_api as dapi
from we_factor_quad.factor_quad_settings import FmpUniverseConfig, settings
date = 'date'
code = 'code'

def get_fixed_psi(quad: FactorQuadEQ,
                  seadrive_localpath='D:\seadrive_cache_folder\zhouly\群组资料库'):
    """
    补上psi中的缺失位，并返回修复后的psi
    Args:
        quad:

    Returns:
    """
    start_date = pd.to_datetime(quad.date_list[0]).replace(day=1).strftime('%Y%m%d')
    end_date = pd.to_datetime(quad.date_list.max()).to_period('M').to_timestamp('D', how='E').strftime('%Y%m%d')
    tmp_start = (quad.date_list[0] - pd.offsets.BDay(5)).strftime('%Y%m%d')
    tmp_end = (quad.date_list[0] - pd.offsets.BDay(1)).strftime('%Y%m%d')
    _, beta_ts = deepcopy(quad.add_country_factor())
    psi_ts = deepcopy(quad.psi_ts)

    beta_ts[code] = ["CN" + x.split(".")[0] for x in beta_ts[code]]
    psi_ts[code] = ["CN" + x.split(".")[0] for x in psi_ts[code]]
    beta = beta_ts.sort_values(by=[date, code])[[date, code] + settings.we_factors_name].set_index([date, code])
    psi = psi_ts[[date, code, 'var']].sort_values(by=[date, code]).set_index([date, code])

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

    _return = dapi.wiser_get_stock_return(start=start_date,
                                          end=end_date,
                                          sample_stk=[],
                                          seadrive_localpath=seadrive_localpath,
                                          freq='B')
    _return = _return.reindex(index=quad.date_list)

    return_supplement = dapi.wiser_get_stock_return(start=tmp_start,
                                                    end=tmp_end,
                                                    sample_stk=[],
                                                    seadrive_localpath=seadrive_localpath,
                                                    freq='B')
    loc_noreturn = _return == 0.0

    fmp_obj = FmpAnalyzer(quad=quad)
    weights = fmp_obj.get_portfolio_weights(start_date=start_date,
                                            end_date=end_date,
                                            freq='B',
                                            universe_conf=FmpUniverseConfig.universe_config['default_universe'])

    _return = pd.concat([return_supplement, _return], axis=0)
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

    final_psi = filled_nan_psi.reset_index()
    final_psi.columns = ['date', 'code', 'var']
    final_psi['date'] = [x.strftime('%Y%m%d') for x in final_psi['date']]
    final_psi['code'] = [map_code(x) for x in final_psi['code']]
    final_psi.to_csv("final_psi.csv", index=True)
    return final_psi


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
    # ave_scale_inverse = scale_inverse['scale']
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


def save_new_psi(save_dir: str):
    """

    Args:
        save_dir:

    Returns:
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    psi = pd.read_csv("final_psi.csv", index_col=0)
    psi['date'] = psi['date'].astype(str)
    os.chdir(os.getcwd() + "/" + save_dir)
    for date in sorted(list(set(psi['date']))):
        print(f"saving tweaked psi for date {date}...")
        dir_name = date
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        date_psi = psi[psi['date'] == date].reset_index(drop=True)
        file_path = os.path.join(os.getcwd(), dir_name, "characteristic_idiosyncratic_variance.csv")
        date_psi.to_csv(path_or_buf=file_path)


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
    start_date = "20230329"
    end_date = "20230330"
    sram_quad = FactorQuadEQ.create_factor_quad(local_path='D:\seadrive_cache_folder\zhouly\群组资料库',
                                                factor_system='HF25_SRAM_DAILY',
                                                start_date=start_date,
                                                end_date=end_date)
    new_psi = get_fixed_psi(quad=sram_quad)
    save_new_psi("HF25_day_test_newpsi3")

