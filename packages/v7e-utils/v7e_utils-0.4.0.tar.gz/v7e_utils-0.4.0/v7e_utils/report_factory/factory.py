"""Report factory to register, run reports developed as plugins"""
#  Copyright (c) 2023. ISTMO Center S.A.  All Rights Reserved
#

report_creation_funcs = {}


def register(report_type, creation_func):
    """Register a new report"""
    report_creation_funcs[report_type] = creation_func


def unregister(report_type: str):
    """Unregisters a report"""
    report_creation_funcs.pop(report_type, None)


def create(arguments):
    """Create a report of a specific type, given a dictionary of arguments."""
    args_copy = arguments.copy()
    report_type = args_copy.pop("report_callback_function", None)
    try:
        creation_func = report_creation_funcs[report_type]
        return creation_func(**args_copy)
    except KeyError:
        raise ValueError(f"Unknown report type {report_type!r}") from None
