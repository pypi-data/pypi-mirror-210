#  Copyright (c) 2023. ISTMO Center S.A.  All Rights Reserved
#
#

import logging
import warnings
from typing import Any, Dict

import django.db
import numpy as np
import pandas as pd
from django.db import connections, connection
from tqdm import tqdm

from ..data_helper.record_batch import RecordBatch

warnings.filterwarnings('ignore')

# Initializing logging configuration in case the user did not set it up.
# logging.basicConfig()

logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=__name__ + '.log',
                    filemode='w')

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class DataHelper:
    auto_run: bool = True
    debug: bool = False
    rebuild: bool = False
    source_table: str = None
    import_fields_list: list = ['*']
    distinct: bool = False
    sql: str = None
    source_pk: str = None
    chunk_size: int = 1000
    modulus: int = 100
    model: object = Any
    target_table: str = None
    target_pk: str = None
    update_from_last_id: bool = False
    set_max_id_counter: bool = False
    show_progress: bool = False
    source: str = None
    source_connection: django.db.connections = None
    pop_keys_on_defaults: list[str] = []
    message: str = "Converting..."
    rename_cols: dict = {}
    drop_cols: list[str] = []
    verbose: bool = False
    records_fetched: int = 0
    records_written: int = 0
    error_model: object = None
    reset_errors: bool = False
    run_post_process: bool = True
    kafka_use: bool = False
    kafka_producer: object = None
    sync_options = None

    default_options = {
        'auto_run': True,
        'error_model': None,
        'reset_errors': False,
        'debug': False,
        'rebuild': False,
        'source_table': None,
        'import_fields_list': ['*'],
        'distinct': False,
        'sql': None,
        'source_pk': None,
        'chunk_size': 1000,
        'modulus': 100,
        'model': None,
        'target_table': None,
        'target_pk': None,
        'update_from_last_id': False,
        'set_max_id_counter': False,
        'show_progress': True,
        'source': None,
        'pop_keys_on_defaults': [],
        'message': 'Converting File...',
        'rename_cols': {},
        'drop_cols': [],
        'verbose': False,
        'run_post_process': True,
        'kafka_producer': None,
        'sync_options': None
    }

    def __init__(self, options: Dict) -> None:
        if options is None:
            options = {}
        options = self.__get_valid_options(options)
        self.options = {**self.default_options, **options}
        for k, v in self.options.items():
            setattr(self, k, v)

        try:
            if self.error_model is not None:
                if self.reset_errors:
                    self.error_model.objects.filter(source_table=self.source_table).delete()

            self.source_connection = connections[self.source]
            self.source_connection.ensure_connection()
            self.target_pk = self.model._meta.pk.column
            self.target_table = getattr(self.model._meta, "db_table")
            if self.debug:
                logger.setLevel(logging.DEBUG)
                logger.info("Target Table:", self.target_table, " Target PK:", self.target_pk)

            self.__build_sql()
            self.set_params()

            if self.auto_run:
                self.__run()
        except Exception as ex:
            logger.critical(ex, exc_info=True)
            if self.debug:
                print(ex)
                raise
            else:
                print(ex)
                pass

    def __get_valid_options(self, opts: dict) -> dict:
        for option in list(opts):
            if option not in self.default_options:
                opts.pop(option, None)
                logger.info(f"option: {option}, is not valid. Already popped!")
        return opts

    def __build_sql(self) -> None:
        if self.sql is not None:
            return
        if self.source_table is not None:
            fields = ", ".join(self.import_fields_list)
            if self.distinct:
                self.sql = f"SELECT DISTINCT {fields} FROM {self.source_table}"
            else:
                self.sql = f"SELECT {fields} FROM {self.source_table}"

    def set_params(self) -> None:
        pass

    def run(self) -> None:
        self.__run()

    def __run(self) -> None:
        try:
            record_batch = RecordBatch()
            record_batch.set_fetch_size(self.chunk_size)
            i, cnt = 0, 0
            p = None
            self.kafka_use = self.kafka_producer is not None
            while True:
                self.source_connection.ensure_connection()
                sql = record_batch.get_sql_statement(self.sql)
                if self.debug:
                    logger.info(sql)
                df = pd.read_sql_query(sql=sql, con=self.source_connection)
                df = df.replace({np.nan: None})
                df_row_count = df.shape[0]
                cnt += df_row_count
                if df_row_count > 0:
                    df = self.fix_data(df)
                    df = self.drop_columns(df)
                    df = self.rename_columns(df)
                    df = self.pre_process(df)
                    if self.show_progress:
                        p = tqdm(total=df.shape[0])
                        p.disable = self.show_progress is False
                        p.set_description(desc=self.message)
                    for row in df.to_dict('records'):
                        self.records_fetched += 1
                        self.__process_row(row)
                        self.post_process_row(row)
                        i = i + 1
                        if self.show_progress and p is not None:
                            if i % self.modulus == 0:
                                p.set_description(
                                    desc='{}-Fetched:{}-Written:{}'.format(self.message, self.records_fetched,
                                                                           self.records_written))
                                p.update(self.modulus)

                    if self.kafka_use:
                        self.kafka_producer.flush()
                    if self.show_progress:
                        p.update(df.shape[0])
                        p.close()
                else:
                    break
        except Exception as ex:
            logger.critical(ex, exc_info=True)
            if self.debug:
                raise
            else:
                pass
        finally:
            if self.run_post_process:
                self.post_process()
            if self.set_max_id_counter:
                self.update_id_counter()
            if self.kafka_producer is not None:
                self.kafka_producer = None
            message = f"Fetched: {self.records_fetched} Written: {self.records_written}"
            if self.debug:
                logger.info(message)
            if self.verbose:
                print(message)

    def __process_row(self, row: dict) -> None:
        try:
            defaults = self.__build_defaults(row)
            overrides = self.build_overrides(row)
            defaults = self.__merge_overrides(defaults, overrides)
            defaults = self.__remove_keys_from_defaults(defaults)
            self.update_create_row(
                row,
                defaults
            )
            self.records_written += 1
        except Exception as ex:
            logger.critical(ex, exc_info=True)
            kwargs = {
                'source_table': self.source_table,
                'target_table': self.target_table,
                'error_row': row,
                'error_message': ex
            }
            if self.error_model is not None:
                self.error_model.objects.create(**kwargs)
            if self.debug:
                logger.error(f"Error in row: {row}")
                raise
            else:
                pass

    @staticmethod
    def __build_defaults(row: dict) -> dict:
        defaults = {}
        for item, value in row.items():
            defaults[item] = value
        return defaults

    def build_overrides(self, row) -> dict:
        return {}

    @staticmethod
    def __merge_overrides(defaults: dict, overrides: dict) -> dict:
        return {**defaults, **overrides}

    def __remove_keys_from_defaults(self, dictionary: dict) -> dict:
        for key in list(self.pop_keys_on_defaults):
            dictionary.pop(key, None)
        return dictionary

    def update_conversion_errors(self, row: dict, message: str = None):
        message = message if message else row
        try:
            # target_pk = row[self.target_pk] if self.target_pk else "Compound Pk"
            # IbisErrors.objects.create(
            #    table_name=self.target_table,
            #    id_key=row[self.target_pk],
            #    error_message=message
            # )
            logger.info(message)
        except KeyError:
            pass

    def post_process_row(self, row: dict) -> None:
        pass

    def pre_process(self, df) -> pd.DataFrame:
        return df

    def post_process(self) -> None:
        pass

    def update_create_row(self, row: dict, defaults: dict) -> None:
        if self.kafka_use:
            self.kafka_producer.send(topic=self.target_table, value=defaults)
        else:
            obj, created = self.model.objects.update_or_create(
                pk=row[self.target_pk],
                defaults=defaults
            )

    def fix_data(self, df) -> pd.DataFrame:
        return df

    def rename_columns(self, df) -> pd.DataFrame:
        if self.rename_cols:
            df = df.rename(columns=self.rename_cols)
        return df

    def drop_columns(self, df) -> pd.DataFrame:
        if self.drop_cols:
            df = df.drop(self.drop_cols, axis=1)
        return df

    def update_id_counter(self) -> None:
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT max({self.target_pk}) FROM {self.target_table}")
                max_value = cursor.fetchone()[0]
                cursor.execute(f"SELECT setval('{self.target_table}_{self.target_pk}_seq', {max_value})")
        except Exception as error:
            logger.error(f"Error while connecting to PostgreSQL: {error}")

    def get_last_id(self, param=None) -> Any:
        if param is None:
            param = self.target_pk
        last_id = 0
        try:
            last_id = self.model.objects.latest(param).pk
        except Exception as ex:
            logger.critical(ex, exc_info=True)
            pass
        finally:
            return last_id
