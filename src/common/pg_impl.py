# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    Class for database functionalities

    Author: Phil Owen, RENCI.org
"""
from src.common.pg_utils_multi import PGUtilsMultiConnect
from src.common.logger import LoggingUtil


class PGImplementation(PGUtilsMultiConnect):
    """
        Class that contains DB calls for the Archiver.

        Note this class inherits from the PGUtilsMultiConnect class
        which has all the connection and cursor handling.
    """

    def __init__(self, db_names: tuple, auto_commit=True):
        # get the log level and directory from the environment.
        log_level, log_path = LoggingUtil.prep_for_logging()

        # create a logger
        self.logger = LoggingUtil.init_logging("APSViz.Settings.PGImplementation", level=log_level, line_format='medium', log_file_path=log_path)

        # init the base class
        PGUtilsMultiConnect.__init__(self, 'APSViz.Settings', db_names, auto_commit)

    def __del__(self):
        """
        Calls super base class to clean up DB connections and cursors.

        :return:
        """
        # clean up connections and cursors
        PGUtilsMultiConnect.__del__(self)

    def get_job_defs(self):
        """
        gets the supervisor job definitions

        :return:
        """

        # create the sql
        sql: str = 'SELECT public.get_supervisor_job_defs_json()'

        # get the data
        ret_val = self.exec_sql('asgs', sql)

        # get the data
        return ret_val

    def get_job_order(self, workflow_type: str):
        """
        gets the supervisor job order

        :return:
        """
        # create the sql
        sql: str = f"SELECT public.get_supervisor_job_order('{workflow_type}')"

        # get the data
        ret_val = self.exec_sql('asgs', sql)

        # get the data
        return ret_val

    def reset_job_order(self, workflow_type_name: str) -> bool:
        """
        resets the supervisor job order to the default

        :return:
        """

        # declare an array of the job id and next job type id in sequence
        workflow_job_types: dict = {
            'ASGS': [
                # record id, next job type
                # -------------------------
                '1, 12',   # staging step
                '13, 25',  # hazus step
                '17, 23',  # obs-mod ast step
                '15, 26',  # adcirc to cog step
                '18, 24',  # adcirc time to cog step
                '16, 19',  # geotiff to cog step
                '11, 20',  # load geo server step
                '14, 21'   # final staging step
                ],
            'ECFLOW': [
                # job id, next job type
                # -------------------------
                '101, 25',  # staging step
                '106, 23',  # obs-mod ast step
                '104, 26',  # adcirc to cog step
                '108, 24',  # adcirc time to cog step
                '105, 19',  # geotiff to cog step
                '102, 20',  # load geo server step
                '103, 21'   # final staging step
                ],
            'HECRAS': [
                '201, 21',  # load geo server step
                ]
         }

        # init the failed flag
        failed: bool = False

        # for each job entry
        for item in workflow_job_types[workflow_type_name]:
            # build the update sql
            sql = f"SELECT public.update_next_job_for_job({item}, '{workflow_type_name}')"

            # and execute it
            ret_val = self.exec_sql('asgs', sql)

            # anything other than a list returned is an error
            if ret_val != 0:
                failed = True
                break

        # if there were no errors, commit the updates
        if not failed:
            self.commit('asgs')

        # return to the caller
        return failed

    def get_terria_map_catalog_data(self, **kwargs):
        """
        gets the catalog data for the terria map UI

        :return:
        """
        # init the return
        catalog_list: dict = {}

        # create the sql
        sql: str = f"SELECT public.get_terria_data_json(_grid_type:={kwargs['grid_type']}, _event_type:={kwargs['event_type']}, " \
                   f"_instance_name:={kwargs['instance_name']}, _run_date:={kwargs['run_date']}, _end_date:={kwargs['end_date']}, " \
                   f"_limit:={kwargs['limit']}, _met_class:={kwargs['met_class']}, _storm_name:={kwargs['storm_name']}, " \
                   f"_cycle:={kwargs['cycle']}, _advisory_number:={kwargs['advisory_number']})"

        # get the layer list
        catalog_list = self.exec_sql('apsviz', sql)

        # get the pull-down data using the above filtering mechanisms
        pulldown_data: dict = self.get_pull_down_data(**kwargs)

        # merge the pulldown data to the catalog list
        catalog_list.update({'pulldown_data': pulldown_data})

        # return the data
        return catalog_list

    def get_run_list(self):
        """
        gets the last 100 job runs

        :return:
        """

        # create the sql
        sql: str = 'SELECT public.get_supervisor_run_list()'

        # return the data
        return self.exec_sql('asgs', sql)

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
        self.exec_sql('asgs', sql)

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
        self.exec_sql('asgs', sql)

    def update_run_status(self, instance_id: int, uid: str, status: str):
        """
        Updates the run properties run status to 'new'.

        :param instance_id:
        :param uid:

        :param status
        :return:
        """

        # create the sql
        sql = f"SELECT public.set_config_item({instance_id}, '{uid}', 'supervisor_job_status', '{status}')"

        # run the SQL
        self.exec_sql('asgs', sql)

    def get_pull_down_data(self, **kwargs) -> dict:
        """
        gets the pulldown data given the list of filtering mechanisms passed.

        :param kwargs:
        :return:
        """
        # init the return value
        pulldown_data: dict = {}

        # get the pull-down data
        sql = f"SELECT public.get_terria_pulldown_data(_grid_type:={kwargs['grid_type']}, _event_type:={kwargs['event_type']}, " \
              f"_instance_name:={kwargs['instance_name']}, _met_class:={kwargs['met_class']}, _storm_name:={kwargs['storm_name']}, " \
              f"_cycle:={kwargs['cycle']}, _advisory_number:={kwargs['advisory_number']});"

        # get the pulldown data
        pulldown_data = self.exec_sql('apsviz', sql)

        # return the full dataset to the caller
        return pulldown_data