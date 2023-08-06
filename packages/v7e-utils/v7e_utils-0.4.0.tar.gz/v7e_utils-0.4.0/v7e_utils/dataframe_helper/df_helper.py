#  Copyright (c) 2022-2023. ISTMO Center S.A.  All Rights Reserved
#
#
import datetime
import logging
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

import pandas as pd
from django.db import models
from django.db import transaction, connection

from ..data_utils import eval_duplicate_removal
from ..dataframe_helper.io import read_frame


class DfHelper(ABC):
    """Helper class to load data from a Django model or view and perform basic data manipulation using pandas."""
    view_name: Optional[str] = None
    model: Optional[models.Model] = None
    model_is_view: bool = False
    use_exclude: bool = False
    char_fields = None
    int_fields = None
    datetime_fields = None
    float_fields = None
    view_config: Dict = {
        'refresh_view': False,
        'concurrently': True,
    }
    dataframe_options: Dict = {
        "debug": False,
        "duplicate_expr": None,
        "duplicate_keep": 'last',
        "sort_field": None,
        "group_by_expr": None,
        "group_expr": None
    }
    dataframe_params: Dict = {
        "fieldnames": (),
        "index_col": None,
        "coerce_float": False,
        "verbose": True,
        "datetime_index": False,
        "column_names": None
    }
    filters: Dict = {}

    def __init__(self, *kwargs):
        """
        Initialize the class with the parameters passed in the `kwargs` dictionary.

        Args:
            kwargs: A dictionary of parameters for loading and manipulating data.
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.__parse_params(kwargs)
        self.set_params()
        assert self.model is not None or self.view_name is not None, "Model or View must be specified"
        assert self.filters is not None, "Must must specify at least one filter condition"

    def refresh(self):
        if self.view_config.get('refresh_view', True) and self.model_is_view:
            print("Este proceso puede durar mucho tiempo...\n")
            refresh_view(self.view_name, concurrently=self.view_config.get('concurrently', True))

    def __parse_params(self, kwargs: tuple[Any]) -> None:
        """Parse the dictionary items from the args tuple and update the class attributes."""
        df_params, df_options, view_options, filters = {}, {}, {}, {}
        try:
            for dict_item in kwargs:
                for key, value in dict_item.items():
                    if key in self.dataframe_params:
                        df_params.update({key: value})
                    elif key in self.dataframe_options:
                        df_options.update({key: value})
                    elif key in self.view_config:
                        view_options.update({key: value})
                    else:
                        filters.update({key: value})
        except Exception as ex:
            self.logger.debug(ex.with_traceback())
            pass
        finally:
            self.filters = filters
            self.view_config = {**self.view_config, **view_options}
            self.dataframe_params = {**self.dataframe_params, **df_params}
            self.dataframe_options = {**self.dataframe_options, **df_options}
            self.view_config = {**self.view_config, **view_options}

    @abstractmethod
    def set_params(self) -> None:
        # set model or view name here
        # self.model = model_name
        # self.model_is_view = False
        # This method should be overloaded in the implemented instance of this class
        pass

    def load(self) -> pd.DataFrame:
        return self.__load_filtered_qs()

    def __load_filtered_qs(self) -> pd.DataFrame:
        if self.use_exclude:
            qs = self.model.objects.exclude(**self.filters)
        else:
            qs = self.model.objects.filter(**self.filters)
        df = read_frame(qs, **self.dataframe_params)
        df = self.convert_columns(df)
        return df

    def convert_columns(self,df):
        model_fields = self.model._meta.get_fields()
        for field in model_fields:
            field_name = field.name
            field_type = type(field).__name__
            if field_name in df.columns:
                if field_type == 'CharField':
                    df[field_name] = df[field_name].values.astype(str)
                elif field_type == 'IntegerField' or field_type == 'AutoField':
                    df[field_name] = df[field_name].values.astype(int)
                elif field_type == 'DateTimeField':
                    df[field_name] = pd.to_datetime(df[field_name], errors='coerce')
                elif field_type == 'BooleanField':
                    df[field_name] = df[field_name].astype(bool)
                elif field_type == 'FloatField' or field_type == 'DecimalField':
                    df[field_name] = pd.to_numeric(df[field_name], errors='coerce')
                elif field_type == 'DateField':
                    df[field_name] = pd.to_datetime(df[field_name], errors='coerce').dt.date
                elif field_type == 'TimeField':
                    df[field_name] = pd.to_datetime(df[field_name], errors='coerce').dt.time
                elif field_type == 'DurationField':
                    df[field_name] = pd.to_timedelta(df[field_name], errors='coerce')
        return df

    def load_latest(self) -> pd.DataFrame:
        # loading the latest works using the df_options settings
        # override on a one to one basis
        return self.__load_set('last')

    def load_earliest(self) -> pd.DataFrame:
        # loading the latest works using the df_options settings
        # override on a one to one basis
        return self.__load_set('first')

    def __load_set(self, keep_duplicate='last') -> pd.DataFrame:
        saved_options = self.dataframe_options
        self.dataframe_options['duplicate_keep'] = keep_duplicate
        df = self.load()
        df = eval_duplicate_removal(df, self.dataframe_options)
        self.dataframe_options = saved_options
        return df

    def load_grouped_activity(self) -> pd.DataFrame:
        df = self.load()
        group_by_expr = self.dataframe_options.get('group_by_expr', None)
        group_expr = self.dataframe_options.get('group_expr', None)
        if group_by_expr is not None:
            df = df.groupby(group_by_expr).size().reset_index(name=group_expr)
        return df

@transaction.atomic()
def refresh_view(view_name, concurrently=False):
    start_time = time.monotonic()
    cursor_command = "REFRESH MATERIALIZED VIEW {}".format(
        view_name) if concurrently == False else "REFRESH MATERIALIZED VIEW CONCURRENTLY {}".format(view_name)
    with connection.cursor() as cursor:
        cursor.execute(cursor_command)
    end_time = time.monotonic()
    duration = datetime.timedelta(seconds=end_time - start_time)
    return duration
