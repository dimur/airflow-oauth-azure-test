#
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

import os
import jwt
from flask_appbuilder import expose
from flask_appbuilder.security.manager import AUTH_OAUTH
from flask_appbuilder.security.views import AuthOAuthView
from airflow.www.security import AirflowSecurityManager

basedir = os.path.abspath(os.path.dirname(__file__))

# Flask-WTF flag for CSRF
WTF_CSRF_ENABLED = True

# ----------------------------------------------------
# AUTHENTICATION CONFIG
# ----------------------------------------------------
# For details on how to set up each of the following authentication, see
# http://flask-appbuilder.readthedocs.io/en/latest/security.html# authentication-methods
# for details.

# The authentication type
AUTH_TYPE = AUTH_OAUTH

# Will allow user self registration
AUTH_USER_REGISTRATION = True

# The default user self registration role
AUTH_USER_REGISTRATION_ROLE = "Public"

# If we should replace ALL the user's roles each login, or only on registration
AUTH_ROLES_SYNC_AT_LOGIN = True

# Force users to re-auth after 30min of inactivity (to keep roles in sync)
PERMANENT_SESSION_LIFETIME = 1800

# A mapping from Azure AD to a list of FAB (Airflow) roles
AUTH_ROLES_MAPPING = {
  "airflow_admin":  ["Admin"],
  "airflow_op":     ["Op"],
  "airflow_user":   ["User"],
  "airflow_viewer": ["Viewer"],
  "airflow_public": ["Public"],
}

AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
AZURE_APPLICATION_ID = os.getenv("AZURE_APPLICATION_ID")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
API_BASE_URL = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2"

# The list of providers which the user can choose from
OAUTH_PROVIDERS = [{
        "name": "azure",
        "icon": "fa-windows",
        "token_key": "access_token",
        "remote_app": {
            "client_id": AZURE_APPLICATION_ID,
            "client_secret": AZURE_CLIENT_SECRET,
            "api_base_url": API_BASE_URL,
            "client_kwargs": {
                "scope": "User.Read",
                "resource": AZURE_APPLICATION_ID,
            },
            "request_token_url": None,
            "access_token_url": f"{API_BASE_URL}/token",
            "authorize_url": f"{API_BASE_URL}/authorize",
        },
}]

# Custom security manager, which introduces a permission model adapted to Airflow
class AzureCustomSecurity(AirflowSecurityManager):
  def oauth_user_info(self, provider, response=None):
    if provider == "azure":
        id_token = response["id_token"]
        me = jwt.decode(id_token, algorithms="RS256", verify=False)
        return {
            "username": me["upn"],
            "email": me["upn"],
            "first_name": me["given_name"],
            "last_name": me["family_name"],
            "role_keys": me["roles"],
          }
    else:
        return {}

SECURITY_MANAGER_CLASS = AzureCustomSecurity
