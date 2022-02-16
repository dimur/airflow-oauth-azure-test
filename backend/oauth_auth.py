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
   User authentication backend
   Referencies
     - https://flask-appbuilder.readthedocs.io/en/latest/_modules/flask_appbuilder/security/manager.html
     - https://github.com/apache/airflow/blob/main/airflow/api/auth/backend/basic_auth.py
"""
from functools import wraps
from typing import Any, Callable, Optional, Tuple, TypeVar, Union, cast

from flask import Response, current_app, request
from flask_appbuilder.const import AUTH_OAUTH, AUTH_LDAP, AUTH_DB
from flask_login import login_user

from flask_appbuilder.security.sqla.models import User

import logging
import jwt

CLIENT_AUTH: Optional[Union[Tuple[str, str], Any]] = None

log = logging.getLogger(__name__)

def init_app(_):
    """Initializes authentication backend"""


T = TypeVar("T", bound=Callable)


def auth_current_user() -> Optional[User]:
    """Authenticate and set current user if Authorization header exists"""
    ab_security_manager = current_app.appbuilder.sm
    user = None

    if ab_security_manager.auth_type == AUTH_OAUTH:
        token = request.headers['Authorization'].strip()
        if token is not None:
            me = jwt.decode(token, algorithms="RS256", verify=False)
            groups = me["roles"]
            if len(groups) >= 1:
                groups = [group for group in groups if "airflow" in group]
                userinfo = {
                    "username": me.get("upn"),
                    "email": me.get("upn"),
                    "first_name": me.get("given_name"),
                    "last_name": me.get("family_name"),
                    "role_keys": groups,
                }
                user = ab_security_manager.auth_user_oauth(userinfo)
                log.info(f"User: {str(user)}")
                if user is not None:
                    login_user(user, remember=False)
    return user

def requires_authentication(function: T):
    """Decorator for functions that require authentication"""

    @wraps(function)
    def decorated(*args, **kwargs):
        if auth_current_user() is not None:
            return function(*args, **kwargs)
        else:
            return Response("Unauthorized", 401, {"WWW-Authenticate": "Basic"})

    return cast(T, decorated)
