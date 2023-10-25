# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    General utilities.

    Author: Phil Owen, 6/27/2023
"""

import os

from pathlib import Path
from enum import Enum
from src.common.logger import LoggingUtil


class GenUtils:
    """
    General utilities

    """
    # declare the two potential image repos
    image_repo_to_repo_name: dict = {'renciorg': 'renciorg', 'containers.renci.org': 'containers.renci.org/eds'}

    # declare the component job type image name
    job_type_to_image_name: dict = {}

    # declare job name to id
    job_type_name_to_id: dict = {}

    @staticmethod
    def get_log_file_list(filter_param: str = ''):
        """
        Gets all the log file path/names

        :return:
        """
        # init the return
        ret_val = {}

        # init a file counter
        counter = 0

        # get the log file path
        log_file_path: str = LoggingUtil.get_log_path()

        # if a filter param was declared make it a wildcard
        if filter_param:
            filter_param += '*'

        # go through all the directories
        for file_path in Path(log_file_path).rglob(f"*{filter_param}log*"):
            # increment the counter
            counter += 1

            # clean up the file path. this is only relevant to windows paths
            final_path = str(file_path).replace(log_file_path, "")

            # save the absolute file path, endpoint URL, and file size in a dict
            ret_val.update({f"{file_path.name}_{counter}": {'file_path': final_path[1:], 'file_size': f'{file_path.stat().st_size} bytes'}})

        # if nothing was found return a message
        if len(ret_val) == 0 and filter_param:
            ret_val = {'Warning': f'Nothing found using your filter parameter ({filter_param[:-1]})'}

        # return the list to the caller
        return ret_val

    @staticmethod
    def check_freeze_status() -> bool:
        """
        checks to see if we are in image freeze mode.

        """
        # get the flag that indicates we are freezing the updating of image versions
        freeze_mode: bool = os.path.exists(os.path.join(os.path.dirname(__file__), '../', str('freeze')))

        # return to the caller
        return freeze_mode


class WorkflowTypeName(str, Enum):
    """
    Class enums for the supervisor workflow names
    """
    CORE = 'CORE'
    FEDERATION = 'FEDERATION'
    PLUGIN = 'PLUGIN'
    TOPOLOGY = 'TOPOLOGY'
    UNIT = 'UNIT'


class JobTypeName(str, Enum):
    """
    Class enum for k8s job type names
    """
    CORE_JOB = 'core-job'
    FEDERATION_JOB = 'federation-job'
    PLUGIN_JOB = 'plugin-job'
    TOPOLOGY_JOB = 'topology-job'
    UNIT_JOB = 'unit-job'


class NextJobTypeName(str, Enum):
    """
    Class enum for k8s job type names
    """
    CORE_JOB = 'core-job'
    FEDERATION_JOB = 'federation-job'
    PLUGIN_JOB = 'plugin-job'
    TOPOLOGY_JOB = 'topology-job'
    UNIT_JOB = 'unit-job'


class RunStatus(str, Enum):
    """
    Class enum for job run status types
    """
    NEW = 'new'
    DEBUG = 'debug'
    DO_NOT_RERUN = 'do not rerun'


class ImageRepo(str, Enum):
    """
    Class enum for image repo registries
    """
    CONTAINERS = 'containers.renci.org'
    RENCIORG = 'renciorg'
