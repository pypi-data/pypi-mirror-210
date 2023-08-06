#  Copyright (c) 2023. ISTMO Center S.A.  All Rights Reserved
#

import datetime
import os
from ..file_utils import check_make_dir


class ReportHelper:
    directory_path: str = None
    today = datetime.datetime.today()
    period: str = "{}/{}".format(today.year, '%02d' % today.month)
    report_directory: str = None
    report_headings: dict = None
    stub: str = None

    def __init__(self):
        self.set_params()
        if self.directory_path:
            check_make_dir(self.directory_path)

    def set_params(self):
        pass

    def create_adhoc_folder(self, stub):
        return check_make_dir(
            os.path.join(self.directory_path, stub)
        )

    def create_folder_current_month(self, stub):
        return check_make_dir(
            os.path.join(self.directory_path, stub, self.period)
        )

    def create_folder_today(self, stub):
        return check_make_dir(
            os.path.join(self.directory_path, stub, str(self.today.year), '%02d' % self.today.month,
                         '%02d' % self.today.day)
        )

    def create_folder_trimester(self, year, q, stub):
        return check_make_dir(
            os.path.join(self.directory_path, stub, "{}-{}".format(year, q))
        )
