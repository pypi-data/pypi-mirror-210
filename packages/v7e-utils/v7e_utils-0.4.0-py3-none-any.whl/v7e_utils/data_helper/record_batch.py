#  Copyright (c) 2023. ISTMO Center S.A.  All Rights Reserved
#
#

class RecordBatch:
    def __init__(self):
        self.limit_cnt = 0
        self.last_limit = 0
        self.last_sql = None
        self.fetch_size = 1000
        self.l_text = None
        self.num_rows:int = 0
        self.total_rows = 0

    def set_fetch_size(self, fetch_size):
        self.fetch_size = fetch_size

    def set_limit_text(self):
        if self.l_text is None:
            self.l_text = f"LIMIT {self.fetch_size}"
            self.limit_cnt = self.fetch_size
            self.last_limit = self.limit_cnt
        else:
            self.limit_cnt = self.last_limit
            self.last_limit = self.limit_cnt + self.fetch_size
            self.l_text = f"LIMIT {self.fetch_size} OFFSET {self.limit_cnt}"

    def set_sql_statement(self, sql):
        self.set_limit_text()
        self.last_sql = f"{sql} {self.l_text}"

    def get_sql_statement(self, sql):
        self.set_sql_statement(sql)
        return self.last_sql
