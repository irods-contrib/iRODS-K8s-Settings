# BSD 3-Clause All rights reserved.
#
# SPDX-License-Identifier: BSD 3-Clause

"""
    iRODS-K8s settings server.
"""

import json
import os
import typing

from itertools import batched

from pathlib import Path
from typing import Union

from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

from src.common.logger import LoggingUtil
from src.common.pg_impl import PGImplementation
from src.common.utils import GenUtils, WorkflowTypeName, RunStatus, JobTypeName, NextJobTypeName, DBType
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
db_names: tuple = ('irods-sv',)

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
    status_code: int = 200
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
        msg: str = 'Exception detected trying to get the component versions.'

        # log the exception
        logger.exception(msg)

        # set the status to a server error
        status_code = 500

        # set the error message in the return
        ret_val = {'Error': msg}

    # return to the caller
    return JSONResponse(content=ret_val, status_code=status_code, media_type="application/json")


@APP.get('/get_environment_type_names', dependencies=[Depends(JWTBearer(security))], status_code=200, response_model=None)
async def get_environment_type_names() -> json:
    """
    Returns the distinct test types.

    """

    # init the returned html status code
    status_code: int = 200
    ret_val: dict = {}

    try:
        # try to make the call for records
        ret_val = db_info.get_environment_type_names()

        # was there an error?
        if ret_val == -1:
            ret_val = {'Warning': 'No data found.'}

    except Exception:
        # return a failure message
        msg: str = 'Exception detected trying to get the environment types.'

        # log the exception
        logger.exception(msg)

        # set the status to a server error
        status_code = 500

        # set the error message in the return
        ret_val = {'Error': msg}

    # return to the caller
    return JSONResponse(content=ret_val, status_code=status_code, media_type="application/json")


@APP.get('/get_test_names', dependencies=[Depends(JWTBearer(security))], status_code=200, response_model=None)
async def get_test_names() -> json:
    """
    Returns the distinct test types.

    """

    # init the returned html status code
    status_code: int = 200
    ret_val: dict = {}

    try:
        # try to make the call for records
        ret_val = db_info.get_test_names()

        # was there an error?
        if ret_val == -1:
            ret_val = {'Warning': 'No data found.'}

    except Exception:
        # return a failure message
        msg: str = 'Exception detected trying to get the test names.'

        # log the exception
        logger.exception(msg)

        # set the status to a server error
        status_code = 500

        # set the error message in the return
        ret_val = {'Error': msg}

    # return to the caller
    return JSONResponse(content=ret_val, status_code=status_code, media_type="application/json")


@APP.get('/get_dbms_image_names', dependencies=[Depends(JWTBearer(security))], status_code=200, response_model=None)
async def get_dbms_image_names() -> json:
    """
    Returns the distinct test types.

    """

    # init the returned html status code
    status_code: int = 200
    ret_val: dict = {}

    try:
        # try to make the call for records
        ret_val = db_info.get_dbms_image_names()

        # was there an error?
        if ret_val == -1:
            ret_val = {'Warning': 'No data found.'}

    except Exception:
        # return a failure message
        msg: str = 'Exception detected trying to get the test suite types.'

        # log the exception
        logger.exception(msg)

        # set the status to a server error
        status_code = 500

        # set the error message in the return
        ret_val = {'Error': msg}

    # return to the caller
    return JSONResponse(content=ret_val, status_code=status_code, media_type="application/json")


@APP.get('/get_os_image_names', dependencies=[Depends(JWTBearer(security))], status_code=200, response_model=None)
async def get_os_image_names() -> json:
    """
    Returns the distinct test types.

    """

    # init the returned html status code
    status_code: int = 200
    ret_val: dict = {}

    try:
        # try to make the call for records
        ret_val = db_info.get_os_image_names()

        # was there an error?
        if ret_val == -1:
            ret_val = {'Warning': 'No data found.'}

    except Exception:
        # return a failure message
        msg: str = 'Exception detected trying to get the test suite types.'

        # log the exception
        logger.exception(msg)

        # set the status to a server error
        status_code = 500

        # set the error message in the return
        ret_val = {'Error': msg}

    # return to the caller
    return JSONResponse(content=ret_val, status_code=status_code, media_type="application/json")


@APP.get('/get_test_request_names', dependencies=[Depends(JWTBearer(security))], status_code=200, response_model=None)
async def get_os_request_names() -> json:
    """
    Returns the distinct test request names.

    """

    # init the returned html status code
    status_code: int = 200
    ret_val: dict = {}

    try:
        # try to make the call for records
        ret_val = db_info.get_test_request_names()

        # was there an error?
        if ret_val == -1:
            ret_val = {'Warning': 'No data found.'}

    except Exception:
        # return a failure message
        msg: str = 'Exception detected trying to get the test suite types.'

        # log the exception
        logger.exception(msg)

        # set the status to a server error
        status_code = 500

        # set the error message in the return
        ret_val = {'Error': msg}

    # return to the caller
    return JSONResponse(content=ret_val, status_code=status_code, media_type="application/json")


@APP.get('/get_run_status/', dependencies=[Depends(JWTBearer(security))], status_code=200, response_model=None)
async def get_run_status(request_group: Union[str, None] = Query(default='')) -> json:
    """
    Returns the distinct test types.

    """

    # init the returned html status code
    status_code: int = 200
    ret_val: list = []

    try:
        # try to make the call for records
        ret_val = db_info.get_run_status(request_group)

        # was there an error?
        if ret_val == -1:
            ret_val = ['Warning: No data found.']

    except Exception:
        # return a failure message
        msg: str = 'Exception detected trying to get the run status.'

        # log the exception
        logger.exception(msg)

        # set the status to a server error
        status_code = 500

        # set the error message in the return
        ret_val = [f'Error: {msg}']

    # return to the caller
    return JSONResponse(content=ret_val, status_code=status_code, media_type="application/json")


@APP.get('/get_job_order/{workflow_type_name}', dependencies=[Depends(JWTBearer(security))], status_code=200, response_model=None)
async def display_job_order(workflow_type_name: WorkflowTypeName = WorkflowTypeName('CORE')) -> json:
    """
    Displays the job order for the workflow type selected.

    """

    # init the returned html status code
    status_code: int = 200
    ret_val: dict = {}

    try:
        # try to make the call for records
        ret_val = db_info.get_job_order(WorkflowTypeName(workflow_type_name).value)

        # was there an error?
        if ret_val == -1:
            ret_val = {'Warning': 'No data found.'}

    except Exception:
        # return a failure message
        msg: str = f'Exception detected trying to get the {WorkflowTypeName(workflow_type_name).value} job order.'

        # log the exception
        logger.exception(msg)

        # set the status to a server error
        status_code = 500

        # set the error message in the return
        ret_val = {'Error': msg}

    # return to the caller
    return JSONResponse(content=ret_val, status_code=status_code, media_type="application/json")


@APP.get('/reset_job_order/{workflow_type_name}', dependencies=[Depends(JWTBearer(security))], status_code=200, response_model=None)
async def reset_job_order(workflow_type_name: WorkflowTypeName = WorkflowTypeName('CORE')) -> json:
    """
    Resets the job process order to the default for the workflow selected.

    """

    # init the returned html status code
    status_code: int = 200
    ret_val: typing.Any = None

    try:
        # is this a legit workflow type?
        if workflow_type_name in WorkflowTypeName:
            # try to make the call for records
            ret_val: bool = db_info_no_auto_commit.reset_job_order(WorkflowTypeName(workflow_type_name).value)

            # check the return value for failure, failed == true
            if not ret_val:
                # get the new job order
                job_order = db_info.get_job_order(WorkflowTypeName(workflow_type_name).value)

                # return a success message with the new job order
                ret_val: list = [{'message': f'The job order for the {WorkflowTypeName(workflow_type_name).value} workflow has been reset to the '
                                             f'default.'}, {'job_order': job_order}]
            else:
                ret_val: dict = {'Error': 'Error resetting job order.'}
        else:
            ret_val: dict = {'Error': f'Workflow type {workflow_type_name} not found.'}

    except Exception:
        # return a failure message
        msg: str = f'Exception detected trying to reset the {workflow_type_name} job order.'

        # log the exception
        logger.exception(msg)

        # set the status to a server error
        status_code = 500

        # set the error message in the return
        ret_val = {'Error': msg}

    # return to the caller
    return JSONResponse(content=ret_val, status_code=status_code, media_type="application/json")


@APP.get('/get_job_defs', dependencies=[Depends(JWTBearer(security))], status_code=200, response_model=None)
async def display_job_definitions() -> json:
    """
    Displays the job definitions for all workflows. Note that this list is in alphabetical order (not in job execute order).

    """
    # init the returned html status code and return value
    status_code: int = 200
    ret_val: dict = {}

    try:
        # try to make the call for records
        job_data = db_info.get_job_defs()

        # did we get an error?
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
        msg: str = 'Exception detected trying to get the job definitions'

        # log the exception
        logger.exception(msg)

        # set the status to a server error
        status_code = 500

        # set the error message in the return
        ret_val = {'Error': msg}

    # return to the caller
    return JSONResponse(content=ret_val, status_code=status_code, media_type="application/json")


@APP.get("/get_log_file_list", dependencies=[Depends(JWTBearer(security))], response_model=None)
async def get_the_log_file_list(filter_param: str = ''):
    """
    Gets the log file list. An optional filter parameter (case-insensitive) can be used to search for targeted results.

    """

    # return the list to the caller in JSON format
    return JSONResponse(content={'Response': GenUtils.get_log_file_list(filter_param)}, status_code=200, media_type="application/json")


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


@APP.put('/superv_workflow_request/{workflow_type}/run_status/{run_status}', dependencies=[Depends(JWTBearer(security))], status_code=200,
         response_model=None)
async def superv_workflow_request(workflow_type: WorkflowTypeName,
                                  run_status: RunStatus,
                                  db_type: Union[DBType, None] = Query(default=DBType.POSTGRESQL),
                                  package_dir: Union[str, None] = Query(default=''),
                                  os_image: Union[str, None] = Query(default='ubuntu-20.04:latest'),
                                  db_image: Union[str, None] = Query(default='postgres:14.11'),
                                  tests: Union[str, None] = Query(default=''),
                                  request_group: Union[str, None] = Query(default='')) -> json:
    """
    Adds a superv workflow request to the DB.

    """
    # init the returned html status code
    status_code: int = 200
    ret_val: dict = {'status': 'success'}
    db_ret_val: int = 0

    try:
        # made sure all the params are valid
        if workflow_type and run_status and os_image:  # and db_image and test_image and tests
            # convert the string to a dict
            test_request = json.loads(tests)

            # if there are tests declared
            if len(test_request) > 0:
                # create base request db object
                base_request_data: dict = {'workflow-type': workflow_type, 'db-image': db_image, 'db-type': db_type, "os-image": os_image,
                                           'package-dir': package_dir, 'tests': None}

                # get the run location
                run_location = next(iter(test_request))

                # was there a valid run location?
                if run_location in ['CONSUMER', 'PROVIDER']:

                    # init a storage list for the tests
                    tests: list = []

                    # define the max number of tests in a short-running group
                    short_batch_size: int = int(os.getenv('SHORT_BATCH_SIZE', '10'))

                    # define the max number of tests in a long-running group
                    long_batch_size: int = int(os.getenv('LONG_BATCH_SIZE', '2'))

                    # get a list of all the tests
                    test_list: list = db_info.get_test_names()

                    # get a lst of the tests that are long-running
                    long_running_tests: list = [el['label'] for el in test_list if el['description'] == 'L']

                    # get a list of the long-running tests requested
                    long_runners: list = [test for test in test_request[run_location] if test in long_running_tests]

                    # the long runners go off in batches of LONG_BATCH_SIZE
                    for batch in batched(long_runners, long_batch_size):
                        # append the test group
                        tests.append({run_location: batch})

                    # get the list of shorter running tests
                    short_runners: list = [test for test in test_request[run_location] if test not in long_running_tests]

                    # the rest go off in batches of SHORT_BATCH_SIZE for short-running tests
                    for batch in batched(short_runners, short_batch_size):
                        # append the test group
                        tests.append({run_location: batch})
                else:
                    logger.warning('Unrecognized test type for request group: %s.', request_group)

                # if there were tests found
                if len(tests) > 0:
                    # insert each test group into the DB
                    for item in tests:
                        # build up the json for the DB
                        base_request_data['tests'] = item

                        # insert the record
                        db_ret_val = db_info.insert_superv_request(run_status.value, base_request_data, request_group)
                # else there were no valid tests requested
                else:
                    ret_val = {'Error': 'No valid tests found.'}
            # else there were no tests requested
            else:
                ret_val = {'Error': 'No tests requested.'}

            # check the result
            if db_ret_val != 0:
                ret_val = {'Error': 'Error inserting database record.'}
            else:
                ret_val = {'Success': 'Request successfully submitted.'}
        else:
            ret_val = {'Error': 'Invalid or missing input parameters.'}

    except Exception:
        # return a failure message
        msg: str = 'Exception detected trying to generate a Superv workflow request.'

        # log the exception
        logger.exception(msg)

        # set the status to a server error
        status_code = 500

        # set the error message in the return
        ret_val = {'Error': msg}

    # return to the caller
    return JSONResponse(content=ret_val, status_code=status_code, media_type="application/json")


# sets the run.properties run status to 'new' for a job
@APP.put('/run_id/{run_id}/status/{status}', dependencies=[Depends(JWTBearer(security))], status_code=200, response_model=None)
async def set_the_run_status(run_id: int, status: RunStatus = RunStatus('new')):
    """
    Updates the run status of a selected job.

    ex: run_id: 3057, status: do not rerun

    """
    # init the returned html status code and return value
    status_code: int = 200
    ret_val: str = ''

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
    status_code: int = 200

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
