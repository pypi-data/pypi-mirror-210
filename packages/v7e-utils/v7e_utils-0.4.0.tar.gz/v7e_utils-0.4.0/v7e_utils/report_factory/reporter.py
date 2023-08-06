#  Copyright (c) 2023. ISTMO Center S.A.  All Rights Reserved
#
import importlib
class ReportFactory:

    def __init__(self):
        self.reports = []
    def register(self, args):
        self.reports.append(args)

    def initialize(self):
        for report in self.reports:
            callback_lib = importlib.import_module(report['report_callback_module'])
            report_prefix = report['report_prefix']
            method = getattr(callback_lib, "initialise")
            method(report_prefix)
