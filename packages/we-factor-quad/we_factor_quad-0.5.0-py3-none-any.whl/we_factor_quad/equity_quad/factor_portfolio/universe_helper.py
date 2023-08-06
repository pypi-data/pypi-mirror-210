import pandas as pd
import numpy as np


def fill_notupdated_constituents(all_constituents: pd.DataFrame) -> pd.DataFrame:
    """
    把单个指数的成分股中，中间未更新的部分ffill了，返回一个填过的与all_constituents一样格式的窄表
    Args:
        all_constituents:
    Returns:
    """
    modified_all_constituents = pd.DataFrame([])
    all_indices = list(set(all_constituents['INDEX_ID']))
    all_dates = sorted(list(set(all_constituents['date'])))
    for index in all_indices:
        index_constituents = all_constituents[all_constituents['INDEX_ID'] == index].drop_duplicates(
            subset=['date', 'code'])
        pivoted_index_constituents = index_constituents.pivot(index='date', columns='code', values="INDEX_ID")
        pivoted_index_constituents = pivoted_index_constituents.reindex(index=all_dates)
        # 这里有一个trick，先把从来没有入选成分股的股票导致的nan，也就是全列都是nan填成一个"0"，
        pivoted_index_constituents[~(pd.isnull(pivoted_index_constituents).all(axis=1))] = \
            pivoted_index_constituents[~(pd.isnull(pivoted_index_constituents).all(axis=1))].replace(np.nan, "0")
        pivoted_index_constituents.fillna(method='ffill', inplace=True)

        pivoted_index_constituents.replace("0", np.nan, inplace=True)
        stacked_index_constituents = pivoted_index_constituents.stack(dropna=False).reset_index()
        modified_all_constituents = pd.concat([modified_all_constituents, stacked_index_constituents], axis=0)
    modified_all_constituents = modified_all_constituents.rename(mapper={0: "INDEX_ID"}, axis=1)
    modified_all_constituents = modified_all_constituents.dropna()\
        .drop_duplicates(subset=['date', 'code']).reset_index(drop=True)
    return modified_all_constituents


def apply_universe_filter(df: pd.DataFrame,
                          universe: pd.DataFrame,
                          raw_cols,
                          universe_cols=['date', 'code']):
    """

    :param df:
    :param universe:
    :param raw_cols:
    :param universe_cols:
    :return:
    """
    for col in raw_cols:
        assert col in df.columns, f"{col} has to be a column of df!"

    universe_filter = universe.stack(dropna=True)
    universe_filter = (universe_filter[universe_filter > 0]).reset_index().filter(universe_cols)
    result = universe_filter.merge(df, left_on=universe_cols, right_on=raw_cols, how='left')
    return result


if __name__ == '__main__':
    pass
