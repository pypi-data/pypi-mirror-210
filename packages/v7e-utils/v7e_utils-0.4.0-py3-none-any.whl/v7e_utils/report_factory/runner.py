#  Copyright (c) 2023. ISTMO Center S.A.  All Rights Reserved
#

from ..report_factory import factory, loader


class ReportRunner(object):
    def __init__(self, modules_list):
        for constructor, library in modules_list.items():
            loader.load_plugins([library])
            factory.create(constructor)
            print("Constructor:", constructor, "Library:", library)
