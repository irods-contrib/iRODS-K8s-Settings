# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    iRODS-K8s settings server.
"""

import json
import os
import re

from pathlib import Path
import requests

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

from src.common.logger import LoggingUtil
from src.common.pg_impl import PGImplementation
from src.common.utils import GenUtils, WorkflowTypeName, ImageRepo, RunStatus, JobTypeName, NextJobTypeName
from src.common.security import Security
from src.common.bearer import JWTBearer

# set the app version
app_version = os.getenv('APP_VERSION', 'Version number not set')

# declare the FastAPI details
APP = FastAPI(title='iRODS-K8s Settings', version=app_version)

# declare app access details
APP.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# get the log level and directory from the environment.
log_level, log_path = LoggingUtil.prep_for_logging()

# create a logger
logger = LoggingUtil.init_logging("iRODS.Settings", level=log_level, line_format='medium', log_file_path=log_path)

# specify the DB to get a connection
# note the extra comma makes this single item a singleton tuple
db_names: tuple = ('irods_k8s',)

# create a DB connection object
db_info: PGImplementation = PGImplementation(db_names, _logger=logger)

# create a DB connection object with auto-commit turned off
db_info_no_auto_commit: PGImplementation = PGImplementation(db_names, _logger=logger, _auto_commit=False)

# create a Security object
security = Security()


@APP.get('/get_sv_component_versions', dependencies=[Depends(JWTBearer(security))], status_code=200, response_model=None)
async def get_sv_component_versions() -> json:
    """
    gets the SV image versions for this namespace

    :return:
    """
    # init the returned html status code
    status_code = 200

    # init the return
    ret_val: dict = {}

    try:
        # try to make the call for records
        job_defs: dict = db_info.get_job_defs()

        # if data was retrieved
        if job_defs != -1:
            # pull out the info needed for each workflow type
            for workflow_type in job_defs:
                # get the workflow type name
                workflow_type_name = list(workflow_type.keys())[0]

                # init a list for the step dicts
                steps: list = []

                # walk through the steps and grab the docker image version details
                for step in workflow_type[workflow_type_name]:
                    # save the step image details
                    steps.append({list(step.keys())[0]: step.get(list(step.keys())[0])['IMAGE']})

                # add the steps to this workflow type dict
                ret_val.update({workflow_type_name: steps})
        else:
            ret_val = {'Warning': 'No data found.'}

    except Exception:
        # return a failure message
        ret_val = {'Error': 'Exception detected trying to get the component versions.'}

        # log the exception
        logger.exception(ret_val)

        # set the status to a server error
        status_code = 500

    # return to the caller
    return JSONResponse(content=ret_val, status_code=status_code, media_type="application/json")


@APP.get('/get_job_order/{workflow_type_name}', dependencies=[Depends(JWTBearer(security))], status_code=200, response_model=None)
async def display_job_order(workflow_type_name: WorkflowTypeName) -> json:
    """
    Displays the job order for the workflow type selected.

    """

    # init the returned html status code
    status_code = 200

    try:
        # try to make the call for records
        ret_val = db_info.get_job_order(WorkflowTypeName(workflow_type_name).value)

        # was there an error
        if ret_val == -1:
            ret_val = {'Warning': 'No data found.'}

    except Exception:
        # return a failure message
        ret_val = f'Exception detected trying to get the {WorkflowTypeName(workflow_type_name).value} job order.'

        # log the exception
        logger.exception(ret_val)

        # set the status to a server error
        status_code = 500

    # return to the caller
    return JSONResponse(content=ret_val, status_code=status_code, media_type="application/json")


@APP.get('/reset_job_order/{workflow_type_name}', dependencies=[Depends(JWTBearer(security))], status_code=200, response_model=None)
async def reset_job_order(workflow_type_name: WorkflowTypeName) -> json:
    """
    Resets the job process order to the default for the workflow selected.

    """

    # init the returned html status code
    status_code = 200
    ret_val = ''

    try:
        # is this a legit workflow type
        if workflow_type_name in WorkflowTypeName:
            # try to make the call for records
            ret_val = db_info_no_auto_commit.reset_job_order(WorkflowTypeName(workflow_type_name).value)

            # check the return value for failure, failed == true
            if ret_val:
                raise Exception(f'Failure trying to reset the {WorkflowTypeName(workflow_type_name).value} job order. Error: {ret_val}')

            # get the new job order
            job_order = db_info.get_job_order(WorkflowTypeName(workflow_type_name).value)

            # return a success message with the new job order
            ret_val = [{'message': f'The job order for the {WorkflowTypeName(workflow_type_name).value} workflow has been reset to the default.'},
                       {'job_order': job_order}]
        else:
            ret_val = {'Error': f'Workflow type {workflow_type_name} not found.'}

    except Exception:
        # return a failure message
        ret_val = {'Error': f'Exception detected trying to reset the {workflow_type_name} job order.'}

        # log the exception
        logger.exception(ret_val)

        # set the status to a server error
        status_code = 500

    # return to the caller
    return JSONResponse(content=ret_val, status_code=status_code, media_type="application/json")


@APP.get('/get_job_defs', dependencies=[Depends(JWTBearer(security))], status_code=200, response_model=None)
async def display_job_definitions() -> json:
    """
    Displays the job definitions for all workflows. Note that this list is in alphabetical order (not in job execute order).

    """
    # init the returned html status code
    status_code = 200

    # init the return
    ret_val: dict = {}

    try:
        # try to make the call for records
        job_data = db_info.get_job_defs()

        # did we get an error
        if job_data != -1:
            # make sure we got a list of config data items
            if isinstance(job_data, list):
                for workflow_item in job_data:
                    # get the workflow type name
                    workflow_type = list(workflow_item.keys())[0]

                    # get the data looking like something we are used to
                    ret_val[workflow_type] = {list(x)[0]: x.get(list(x)[0]) for x in workflow_item[workflow_type]}

                    # fix the arrays for each job def. they come in as a string
                    for item in ret_val[workflow_type].items():
                        item[1]['COMMAND_LINE'] = json.loads(item[1]['COMMAND_LINE'])
                        item[1]['COMMAND_MATRIX'] = json.loads(item[1]['COMMAND_MATRIX'])
                        item[1]['PARALLEL'] = json.loads(item[1]['PARALLEL']) if item[1]['PARALLEL'] is not None else None
            else:
                ret_val = {'Error': 'Error: Job definitions are not a list.'}
        else:
            ret_val = {'Error': 'Error: No job definitions found.'}

    except Exception:
        # return a failure message
        ret_val = {'Error': 'Exception detected trying to get the job definitions'}

        # log the exception
        logger.exception(ret_val)

        # set the status to a server error
        status_code = 500

    # return to the caller
    return JSONResponse(content=ret_val, status_code=status_code, media_type="application/json")


@APP.get("/get_log_file_list", dependencies=[Depends(JWTBearer(security))], response_model=None)
async def get_the_log_file_list(filter_param: str = ''):
    """
    Gets the log file list. An optional filter parameter (case-insensitive) can be used to search for targeted results.

    """

    # return the list to the caller in JSON format
    return JSONResponse(content={'Response': GenUtils.get_log_file_list(filter_param)}, status_code=200,
                        media_type="application/json")


@APP.get("/get_log_file/", dependencies=[Depends(JWTBearer(security))], response_model=None)
async def get_the_log_file(log_file: str):
    """
    Gets the log file specified. This method only expects a properly named file.

    """
    # make sure we got a log file
    if log_file:
        # get the log file path
        log_file_path: str = LoggingUtil.get_log_path()

        # get the full path to the file
        target_log_file_path = os.path.join(log_file_path, log_file)

        # loop through the log file directory
        for found_log_file in Path(log_file_path).rglob('*log*'):
            # if the target file is found in the log directory
            if target_log_file_path == str(found_log_file):
                # return the file to the caller
                return FileResponse(path=target_log_file_path, filename=log_file, media_type='text/plain')

        # if we get here return an error
        return JSONResponse(content={'Response': 'Error - Log file does not exist.'}, status_code=404, media_type="application/json")

    # if we get here return an error
    return JSONResponse(content={'Response': 'Error - You must select a log file.'}, status_code=404, media_type="application/json")


# sets the run.properties run status to 'new' for a job
@APP.put('/run_id/{run_id}/status/{status}', dependencies=[Depends(JWTBearer(security))], status_code=200, response_model=None)
async def set_the_run_status(run_id: int, status: RunStatus = RunStatus('new')):
    """
    Updates the run status of a selected job.

    ex: run_id: 3057, status: do not rerun

    """
    # init the returned html status code
    status_code = 200

    # is this a valid instance id
    if run_id > 0:
        try:
            # try to make the update
            db_info_no_auto_commit.update_run_status(run_id, status.value)

            # return a success message
            ret_val = f'The status of run {run_id} has been set to {status}'
        except Exception:
            # return a failure message
            ret_val = f'Exception detected trying to update run {run_id} to {status}'

            # log the exception
            logger.exception(ret_val)

            # set the status to a server error
            status_code = 500
    else:
        # return a failure message
        ret_val = f'Error: The instance id {run_id} is invalid. An instance must be a non-zero integer.'

        # log the error
        logger.error(ret_val)

        # set the status to a bad request
        status_code = 400

    # return to the caller
    return JSONResponse(content={'Response': ret_val}, status_code=status_code, media_type="application/json")


# Updates a supervisor component's next process.
@APP.put('/workflow_type_name/{workflow_type_name}/job_type_name/{job_type_name}/next_job_type/{next_job_type_name}',
         dependencies=[Depends(JWTBearer(security))], status_code=200, response_model=None)
async def set_the_supervisor_job_order(workflow_type_name: WorkflowTypeName, job_type_name: JobTypeName, next_job_type_name: NextJobTypeName):
    """
    Modifies the supervisor component's linked list of jobs. Select the workflow type, then select the job process name and the next job
    process name.

    """
    # init the returned html status code
    status_code = 200

    try:
        # check for a recursive situation
        if job_type_name == next_job_type_name:
            # set the error msg
            ret_val = f'You cannot specify a next job type equal to the target job type ({job_type_name}).'

            # declare an error for the user
            status_code = 500
        else:
            # convert the next job process name to an id
            next_job_type_id = GenUtils.job_type_name_to_id.get(NextJobTypeName(next_job_type_name).value)

            # did we get a good type id
            if next_job_type_name is not None:
                # prep the record to update key. complete does not have a hyphen
                if job_type_name != 'complete':
                    job_type_name += '-'

                # make the update
                db_info.update_next_job_for_job(job_type_name, next_job_type_id, WorkflowTypeName(workflow_type_name).value)

                # get the new job order
                job_order = db_info.get_job_order(WorkflowTypeName(workflow_type_name).value)

                # return a success message with the new job order
                ret_val = [{
                    'message': f'The {WorkflowTypeName(workflow_type_name).value} {job_type_name} next process has been set to {next_job_type_name}'},
                    {'new_order': job_order}]
            else:
                # set the error msg
                ret_val = f'The next job process ID was not found for {WorkflowTypeName(workflow_type_name).value} {next_job_type_name}'

                # declare an error for the user
                status_code = 500

    except Exception:
        # return a failure message
        ret_val = f'Exception detected trying to update the {WorkflowTypeName(workflow_type_name).value} next job name for' \
                  f' {job_type_name}, next job name: {next_job_type_name}'

        # log the exception
        logger.exception(ret_val)

        # set the status to a server error
        status_code = 500

    # return to the caller
    return JSONResponse(content={'Response': ret_val}, status_code=status_code, media_type="application/json")
