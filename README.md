<!--
BSD 3-Clause All rights reserved.

SPDX-License-Identifier: BSD 3-Clause
-->

[![iRODS](iRODS-Logo.png)](https://irods.org)

# iRODS K8s Settings
A Web application/services to view/modify the *[iRODS-K8s Supervisor](https://github.com/irods-contrib/iRODS-K8s-Supervisor)* run-time configuration as well as to monitor operational state.

#### License.
[![BSD License](https://img.shields.io/badge/License-BSD-orange.svg)](https://github.com/irods-contrib/iRODS-K8s-Settings/blob/main/LICENSE)

#### Components and versions.
[![Python](https://img.shields.io/badge/Python-3.12.6-orange)](https://github.com/python/cpython)
[![Linting Pylint](https://img.shields.io/badge/Pylint-%203.3.0-yellow)](https://github.com/PyCQA/pylint)
[![Pytest](https://img.shields.io/badge/Pytest-%208.3.3-blue)](https://github.com/pytest-dev/pytest)

#### Build status.
[![PyLint the codebase](https://github.com/irods-contrib/iRODS-K8s-Settings/actions/workflows/pylint.yml/badge.svg)](https://github.com/irods-contrib/iRODS-K8s-Settings/actions/workflows/pylint.yml)
[![Build and push the Docker image](https://github.com/irods-contrib/iRODS-K8s-Settings/actions/workflows/image-push.yml/badge.svg)](https://github.com/irods-contrib/iRODS-K8s-Settings/actions/workflows/image-push.yml)

## Description.
This product provides a FASTAPI interface to allow access to 
the *[iRODS-K8s Supervisor](https://github.com/irods-contrib/iRODS-K8s-Supervisor)* database, configuration, and status.

There are GitHub actions to maintain code quality in this repo:
 - Pylint (minimum score of 10/10 to pass),
 - Build/publish a Docker image.

### How to build the Docker image for this product.

The Docker image must be placed in a container image registry and referenced in this component's deployment scripts.

```shell
docker build --build-arg APP_VERSION=<version> -f Dockerfile -t irods-k8s-settings:latest .
```
### K8s/Helm deployment scripts for this product are available *[here][iRODS K8s Helm](https://github.com/irods/irods_k8s/tree/main/helm/irods-supervisor-settings)*.
