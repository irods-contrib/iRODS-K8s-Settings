# BSD 3-Clause All rights reserved.
#
# SPDX-License-Identifier: BSD 3-Clause

"""
    JWT bearer utilities.

    Author: Phil Owen, 6/27/2023
"""
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.common.security import Security


class JWTBearer(HTTPBearer):
    """
    class to handle JWT operations

    """
    def __init__(self, sec: Security, auto_error: bool = True):
        # save the security object
        self.sec = sec

        # call the superclass to init
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        """
        called by fastapi to authenticate the request

        :param request:
        :return:
        """
        # get the JWT Bearer token from the request
        auth: HTTPAuthorizationCredentials = await super().__call__(request)

        # if we got the bearer creds
        if auth:
            # make sure that the request has an auth bearer
            if not auth.scheme == "Bearer":
                # raise error if no bearer specified
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")

            # decode and validate the JWT auth token
            if not self.sec.decode_jwt(auth.credentials):
                raise HTTPException(status_code=403, detail="Invalid authentication token.")

            # return the JWT creds
            return auth.credentials
