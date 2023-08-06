import pandas as pd
import numpy as np

def summary_stats(ret, compounding=0, sampling_freq='BM', annual_fac=12.0):
    """
    return summary stats
    :param ret: DataFrame or Series of Returns
    :param compounding:
    :param sampling_freq:
    :param annual_fac: annualization factor for the corresponding frequency
    :return:
    """
    if isinstance(ret, pd.Series):
        ret = pd.DataFrame({'ret': ret})
    if compounding:
        ret_m = ret.cumprod().asfreq(sampling_freq, method='pad').pct_change()
    else:
        ret_m = ret.cumsum().asfreq(sampling_freq, method='pad').diff()

    summary = {'count': ((ret_m != 0.0) & (~pd.isnull(ret_m))).sum(),
               '0Mean': ret_m.mean() * annual_fac,
               '1Vol': ret_m.std() * np.sqrt(annual_fac),
               '2Sharpe': ret_m.mean() / ret_m.std() * np.sqrt(annual_fac),
               '3Skewness': (100.0 * ret_m).skew(),
               '4Kurt': (100.0 * ret_m).kurt(),
               '5AR(1)': ret_m.corrwith(ret_m.shift(1))}
    return pd.DataFrame(summary).T