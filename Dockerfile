# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

# This Dockerfile is used to build THE APSVIZ-Settings python image
# starts with the python image
# creates a directory for the repo
# gets the APSVIZ-Settings repo
# and runs main which starts the web server

# leverage the renci python base image
FROM python:3.9-slim

# get some credit
LABEL maintainer="powen@renci.org"

# Copy in just the requirements first for caching purposes
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# create a new non-root user and switch to it
RUN useradd --create-home -u 1000 nru
USER nru

# Create the directory for the code and cd to it
WORKDIR /repo/APSVIZ-Settings

# Copy in the rest of the code
COPY . .

# start the service entry point
ENTRYPOINT ["python", "main.py"]
