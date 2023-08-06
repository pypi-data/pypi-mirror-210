#  Copyright (c) 2023. ISTMO Center S.A.  All Rights Reserved
#

import configparser
import os
import zipfile

import openpyxl


class IniFile(configparser.ConfigParser):
    def __init__(self, config_file, defaults=None, overwrite_defaults=False):
        super().__init__()
        self.config_file = config_file
        self.defaults = defaults
        self.overwrite_defaults = overwrite_defaults
        self.go()

    def go(self):
        if not os.path.exists(self.config_file):
            self.save_config()
            self.overwrite_defaults = True

        if self.defaults is not None and self.overwrite_defaults:
            for section, content in self.defaults.items():
                self.add_section(section)
                for key in content.keys():
                    self.set(section, key, str(content[key]))
            self.save_config()
        self.read(self.config_file)
        return self

    def get_config(self, section: str, option: str) -> str:
        return self.get(section, option)

    def write_config(self, section: str, option: str, value: str) -> None:
        self.set(section, option, str(value))
        self.save_config()

    def save_config(self) -> None:
        with open(self.config_file, 'w') as configfile:
            self.write(configfile)


## Alternative Version
# class IniFile:
#     def __init__(self, config_file, defaults=None, overwrite_defaults=False):
#         self.config_file = config_file
#         self.defaults = defaults
#         self.overwrite_defaults = overwrite_defaults
#         self.config = configparser.ConfigParser()
#         self.create_file()
#         self.add_defaults()
#         self.read_file()
#
#     def create_file(self):
#         if not os.path.exists(self.config_file):
#             with open(self.config_file, 'w') as f:
#                 pass
#
#     def add_defaults(self):
#         if self.defaults is not None and self.overwrite_defaults:
#             for section, content in self.defaults.items():
#                 self.config.add_section(section)
#                 for key in content.keys():
#                     self.config.set(section, key, str(content[key]))
#             self.save_config()
#
#     def read_file(self):
#         self.config.read(self.config_file)
#
#     def get_config(self, section: str, option: str) -> str:
#         return self.config.get(section, option)
#
#     def write_config(self, section: str, option: str, value: str) -> None:
#         self.config.set(section, option, str(value))
#
#     def save_config(self) -> None:
#         with open(self.config_file, 'w') as configfile:
#             self.config.write(configfile)

def check_make_dir(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath, exist_ok=True)
    return os.path.join(dirpath, '')


def ensure_directory_exists(dir_path):
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


def compress_files_to_zip(file_list, zip_file_name):
    with zipfile.ZipFile(zip_file_name, 'w') as zip_file:
        for file in file_list:
            zip_file.write(file)
    return zip_file_name


def adjust_worksheet_columns(worksheet, df):
    for col_idx, col in enumerate(df):
        series = df[col]
        # Find the maximum length of the column name and the values in the column
        max_len = max(
            series.astype(str).map(len).max(),
            len(str(series.name))
        ) + 1  # Adding a little extra space
        # Set the width of the column in the worksheet
        worksheet.column_dimensions[openpyxl.utils.get_column_letter(col_idx + 1)].width = max_len
        #worksheet.set_column(col_idx, col_idx, max_len)
