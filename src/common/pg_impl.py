# BSD 3-Clause All rights reserved.
#
# SPDX-License-Identifier: BSD 3-Clause

"""
    Class for database functionalities

    Author: Phil Owen, RENCI.org
"""
import json

from src.common.pg_utils_multi import PGUtilsMultiConnect
from src.common.logger import LoggingUtil


class PGImplementation(PGUtilsMultiConnect):
    """
        Class that contains DB calls for the Settings app.

        Note this class inherited from the PGUtilsMultiConnect class
        which has all the connection and cursor handling.
    """

    def __init__(self, db_names: tuple, _logger=None, _auto_commit=True):
        # if this is a reference to a logger passed in use it
        if _logger is not None:
            # get a handle to a logger
            self.logger = _logger
        else:
            # get the log level and directory from the environment.
            log_level, log_path = LoggingUtil.prep_for_logging()

            # create a logger
            self.logger = LoggingUtil.init_logging("iRODS.Settings.PGImplementation", level=log_level, line_format='medium', log_file_path=log_path)

        # init the base class
        PGUtilsMultiConnect.__init__(self, 'iRODS.Settings', db_names, _logger=self.logger, _auto_commit=_auto_commit)

    def __del__(self):
        """
        Calls super base class to clean up DB connections and cursors.

        :return:
        """
        # clean up connections and cursors
        PGUtilsMultiConnect.__del__(self)

    def get_environment_type_names(self):
        """
        gets the test environment types

        :return:
        """

        # create the sql
        sql: str = "SELECT public.get_environment_type_names_json();"

        # get the data
        ret_val = self.exec_sql('irods-sv', sql)

        # return the data
        return ret_val

    def get_test_names(self):
        """
        gets the test names

        :return:
        """

        # create the sql
        sql: str = "SELECT public.get_test_names_json();"

        # get the data
        ret_val = self.exec_sql('irods-sv', sql)

        # return the data
        return ret_val

    def get_dbms_image_names(self):
        """
        gets the DBMS image names

        :return:
        """

        # create the sql
        sql: str = "SELECT public.get_dbms_image_names_json();"

        # get the data
        ret_val = self.exec_sql('irods-sv', sql)

        # return the data
        return ret_val

    def get_os_image_names(self):
        """
        gets the os image names

        :return:
        """

        # create the sql
        sql: str = "SELECT public.get_os_image_names_json();"

        # get the data
        ret_val = self.exec_sql('irods-sv', sql)

        # return the data
        return ret_val

    def get_test_request_names(self):
        """
        gets the irods test request names

        :return:
        """

        # create the sql
        sql: str = "SELECT public.get_test_request_names_json();"

        # get the data
        ret_val = self.exec_sql('irods-sv', sql)

        # return the data
        return ret_val

    def get_test_request_name_exists(self, request_name):
        """
        gets true/false if the request name already exists

        :return:
        """

        # create the sql
        sql: str = f"SELECT public.get_test_request_name_exists('{request_name}');"

        # get the data
        ret_val = self.exec_sql('irods-sv', sql)

        # return the data
        return ret_val

    def get_run_status(self, request_group):
        """
        gets the run status

        :return:
        """

        # create the sql
        sql: str = f"SELECT public.get_run_status_json('{request_group}');"

        # get the data
        ret_val = self.exec_sql('irods-sv', sql)

        # return the data
        return ret_val

    def insert_superv_request(self, status: str, request_data: dict, request_group: str):
        """
        inserts a request record into the database

        :param status:
        :param request_data:
        :param request_group:

        :return:
        """

        # create the sql
        sql: str = (f"SELECT public.insert_request_item(_status:='{status}', _request_data:='{json.dumps(request_data)}', "
                    f"_request_group:='{request_group}');")

        # get the data
        ret_val = self.exec_sql('irods-sv', sql)

        # return the data
        return ret_val

    def get_job_defs(self):
        """
        gets the supervisor job definitions

        :return:
        """

        # create the sql
        sql: str = 'SELECT public.get_supervisor_job_defs_json()'

        # get the data
        ret_val = self.exec_sql('irods-sv', sql)

        # return the data
        return ret_val

    def get_job_order(self, workflow_type: str):
        """
        gets the supervisor job order

        :return:
        """
        # create the sql
        sql: str = f"SELECT public.get_supervisor_job_order('{workflow_type}')"

        # get the data
        ret_val = self.exec_sql('irods-sv', sql)

        # return the data
        return ret_val

    def reset_job_order(self, workflow_type_name: str) -> bool:
        """
        resets the supervisor job order to the default

        :return:
        """

        # declare an array of the job id and next job type id in sequence
        workflow_job_types: dict = {'CORE': ['1, 2', '2, 3'], 'FEDERATION': ['1, 2', '2, 3'], 'PLUGIN': ['1, 2', '2, 3'],
                                    'TOPOLOGY': ['1, 2', '2, 3'], 'UNIT': ['1, 2', '2, 3']}

        # init the failed flag
        failed: bool = False

        # for each job entry
        for item in workflow_job_types[workflow_type_name]:
            # build the update sql
            sql = f"SELECT public.update_next_job_for_job({item}, '{workflow_type_name}')"

            # and execute it
            ret_val = self.exec_sql('irods-sv', sql)

            # anything other than a list returned is an error
            if ret_val != 0:
                failed = True
                break

        # if there were no errors, commit the updates
        if not failed:
            self.commit('irods-sv')

        # return to the caller
        return failed

    def get_run_list(self):
        """
        gets the last 100 job runs

        :return:
        """

        # create the sql
        sql: str = 'SELECT public.get_supervisor_run_list()'

        # return the data
        return self.exec_sql('irods-sv', sql)

    def update_next_job_for_job(self, job_name: str, next_process_id: int, workflow_type_name: str):
        """
        Updates the next job process id for a job

        :param job_name:
        :param next_process_id:
        :param workflow_type_name:
        :return: nothing
        """

        # create the sql
        sql = f"SELECT public.update_next_job_for_job('{job_name}', {next_process_id}, '{workflow_type_name}')"

        # run the SQL
        ret_val = self.exec_sql('irods-sv', sql)

        # if there were no errors, commit the updates
        if ret_val > -1:
            self.commit('irods-sv')

    def update_job_image_version(self, job_name: str, image: str):
        """
        Updates the image version

        :param job_name:
        :param image:
        :return: nothing
        """

        # create the sql
        sql = f"SELECT public.update_job_image('{job_name}', '{image}')"

        # run the SQL
        ret_val = self.exec_sql('irods-sv', sql)

        # if there were no errors, commit the updates
        if ret_val > -1:
            self.commit('irods-sv')

    def update_run_status(self, run_id: int, status: str):
        """
        Updates the run properties run status to 'new'.

        :param run_id:

        :param status
        :return:
        """

        # create the sql
        sql = f"SELECT public.set_config_item({run_id}, 'supervisor_job_status', '{status}')"

        # run the SQL
        ret_val = self.exec_sql('irods-sv', sql)

        # if there were no errors, commit the updates
        if ret_val > -1:
            self.commit('irods-sv')

    def get_run_props(self, run_id: int):
        """
        gets the run properties for a run

        :return:
        """
        # create the sql
        sql: str = f"SELECT * FROM public.get_run_prop_items_json({run_id})"

        # get the data
        ret_val = self.exec_sql('irods-sv', sql)

        # check the result
        if ret_val == -1:
            ret_val = ['Run not found']
        else:
            # replace with the data sorted by keys
            ret_val[0]['run_data'] = {x: ret_val[0]['run_data'][x] for x in sorted(ret_val[0]['run_data'])}

        # return the data
        return ret_val[0]
