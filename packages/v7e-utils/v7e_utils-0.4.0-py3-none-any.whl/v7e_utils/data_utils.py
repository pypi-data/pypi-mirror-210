#  Copyright (c) 2023. ISTMO Center S.A.  All Rights Reserved
#

from typing import Any, Dict
import datetime
import pandas as pd

timeseries_options: Dict = {
    'index_col': 'last_activity_dt',
    'rule': 'D',
    'cols': None,
    'vals': None,
    'totals': False,
    'aggfunc': 'count'
}

def convert_value_pairs(row):
    if row['value_type'] == "datetime":
        converted_value = datetime.datetime.strptime(row['value'], '%Y-%m-%d %H:%M:%S')
    elif row['value_type'] == 'str':
        converted_value = row['value']
    else:
        converted_value = eval(f"{row['value_type']}({row['value']})")
    return converted_value


def get_timeseries_params(df_params) -> Any:
    index_col = None
    ts_params = df_params
    if ts_params.get("datetime_index", False):
        index_col = ts_params.get('index_col', None)
        pop_cols = ['datetime_index', 'index_col']
        for p in pop_cols:
            ts_params.pop(p, None)
    return index_col, ts_params


def add_df_totals(df):
    df.loc['Total'] = df.sum(numeric_only=True, axis=0)
    df.loc[:, 'Total'] = df.sum(numeric_only=True, axis=1)
    return df


def eval_duplicate_removal(df, df_options):
    duplicate_expr = df_options.get('duplicate_expr', None)
    if duplicate_expr is None:
        return df
    if df_options.get('debug', False):
        df_duplicates = df[df.duplicated(duplicate_expr)]
        print("Duplicate Rows based on columns are:", df_duplicates, sep='\n')
    sort_field = df_options.get('sort_field', None)
    keep_which = df_options.get('duplicate_keep', 'last')
    if sort_field is None:
        df = df.drop_duplicates(duplicate_expr, keep=keep_which)
    else:
        df = df.sort_values(sort_field).drop_duplicates(duplicate_expr, keep=keep_which)
    return df

def format_fields(df, format_options):
    for fld_name, fld_type in format_options.items():
        if fld_name in df.columns:
            df[fld_name] = df[fld_name].values.astype(fld_type)
    return df

def fillna_fields(df, fill_options):
    for fld_name, fill_value in fill_options.items():
        if fld_name in df.columns:
            df[fld_name].fillna(fill_value, inplace=True)
    return df


def cast_cols_as_categories(df, threshold=100):
    for col in df.columns:
        if df[col].dtype == object and len(df[col].unique()) < threshold:
            df[col] = df[col].astype(pd.CategoricalDtype())
    return df

def load_as_timeseries(df, options=timeseries_options):
    index_col = options.get("index_col", None)
    if index_col is not None and index_col in df.columns:
        df.set_index(index_col, inplace=True)
    rule = options.get("rule", "D")
    index = options.get("index", df.index)
    cols = options.get("cols", None)
    vals = options.get("vals", None)
    totals = options.get("totals", False)
    agg_func = options.get("agg_func", 'count')
    df = df.pivot_table(index=index, columns=cols, values=vals, aggfunc=agg_func).fillna(0)
    df = df.resample(rule=rule).sum()
    df.sort_index(inplace=True)
    if totals:
        df = add_df_totals(df)
    return df