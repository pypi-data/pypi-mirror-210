# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
DB-API implementation based on pyhive
"""

import base64
import ssl

from pyhive import hive
from thrift.transport import THttpClient

# PEP 249 module globals
apilevel = hive.apilevel
threadsafety = hive.threadsafety
paramstyle = hive.paramstyle


def connect(
    database: str,
    http_path: str,
    username: str,
    password: str,
    host: str,
    port: int = 443,
    ssl_cert: str = "none",
    **kwargs
) -> hive.Connection:
    """
    Constructor for creating a pyhive DB-API connection to the SeqsLab cluster.
    :param database:
    :param http_path: a seqslab job run ID
    :param username:
    :param password:
    :param ssl_cert: "none", "optional", or "required"
    :param host:
    :param port:
    :returns: a pyhive :py:class:`Connection` object.
    """
    if ssl_cert:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = hive.ssl_cert_parameter_map[ssl_cert]
    else:
        raise ValueError("Missing SSL certificate argument.")

    if username is not None and password is not None:
        auth = base64.standard_b64encode(f"{username}:{password}".encode()).decode("UTF-8")
    else:
        raise ValueError("Missing either username or password argument.")

    if http_path is not None:
        uri = f"https://{host}:{port}/{http_path}"
    else:
        raise ValueError("Missing http_path argument.")

    thrift_transport = THttpClient.THttpClient(
        uri_or_host=uri,
        ssl_context=ssl_context,
    )
    thrift_transport.setCustomHeaders({"Authorization": f"Basic {auth}"})

    return hive.Connection(database=database, thrift_transport=thrift_transport, **kwargs)
