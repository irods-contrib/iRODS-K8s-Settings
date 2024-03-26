# BSD 3-Clause All rights reserved.
#
# SPDX-License-Identifier: BSD 3-Clause

"""
    General utilities.

    Author: Phil Owen, 10/16/2023
"""

import os

from pathlib import Path
from enum import Enum
from src.common.logger import LoggingUtil
from src.common.pg_impl import PGImplementation


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

        # if a filter param was declared, make it a wildcard
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

        # if nothing was found, return a message
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

    @staticmethod
    def validate_settings_input(workflow_type, run_status, package_dir, tests, request_group, db_info) -> str:
        """
        checks to see if the path passed exists or is using a default

        :return:
        """
        ret_val: list = []

        if not workflow_type:
            ret_val.append(['No workflow type found'])

        if not run_status:
            ret_val.append('No run status')

        if len(package_dir) != 0 and not os.path.exists(package_dir):
            ret_val.append('Invalid package directory')

        if not tests:
            ret_val.append('No tests')

        if not request_group:
            ret_val.append('No request group')
        else:
            # does the request group name already exist?
            db_ret_val = db_info.get_test_request_name_exists(request_group)

            # check the results
            if db_ret_val < 0:
                ret_val.append('DB error getting test request name.')
            elif db_ret_val:
                ret_val.append(f"Test request name '{request_group}' already exists.")

        # return to the caller
        return ', '.join(ret_val)


class WorkflowTypeName(str, Enum):
    """
    Class enums for the supervisor workflow names
    """
    CORE = 'CORE'
    FEDERATION = 'FEDERATION'
    PLUGIN = 'PLUGIN'
    TOPOLOGY = 'TOPOLOGY'
    UNIT = 'UNIT'


class DBType(str, Enum):
    """
    Enum class for the various database types
    """
    MYSQL = "mysql"
    POSTGRESQL = "postgres"


class JobTypeName(str, Enum):
    """
    Class enum for k8s job type names
    """
    CORE_STAGING_JOB = 'core-staging-job'
    CORE_DATABASE_JOB = 'core-database-job'
    CORE_PROVIDER_JOB = 'core-provider-job'
    CORE_CONSUMER_JOB = 'core-consumer-job'
    CORE_FORENSICS_JOB = 'core-forensics-job'
    CORE_FINAL_STAGING_JOB = 'core-final-staging-job'


class NextJobTypeName(str, Enum):
    """
    Class enum for k8s job type names
    """
    CORE_STAGING_JOB = 'core-staging-job'
    CORE_DATABASE_JOB = 'core-database-job'
    CORE_PROVIDER_JOB = 'core-provider-job'
    CORE_CONSUMER_JOB = 'core-consumer-job'
    CORE_FORENSICS_JOB = 'core-forensics-job'
    CORE_FINAL_STAGING_JOB = 'core-final-staging-job'


class RunStatus(str, Enum):
    """
    Class enum for job run status types
    """
    NEW = 'new'
    DEBUG = 'debug'
    DO_NOT_RUN = 'do not run'


class ImageRepo(str, Enum):
    """
    Class enum for image repo registries
    """
    CONTAINERS = 'containers.renci.org'
