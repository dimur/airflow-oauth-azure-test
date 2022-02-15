# Azure AD OAuth2 authentication in Airflow 2
    useful links:
        https://github.com/dpgaspar/Flask-AppBuilder/blob/master/examples/oauth/config.py
        https://github.com/apache/airflow/blob/main/airflow/www/security.py
        https://awslife.medium.com/airflow-authentication-with-rbac-and-keycloak-2c34d2012059

## 1. ON AZURE PORTAL
### 1.1. Create an app registration
        Azure Active Directory -> App registrations
        -> New registration
            1. set Name
            2. set Account type (Single tenant is default)
            3. set Redirect URI
                example (local test):
                    Web (platform type) http://localhost:8080/oauth-authorized/azure
### 1.2. Create a client secret
        Azure Active Directory -> App registrations -> [App name] -> Certificates & secrets
        -> New client secret
### 1.3. Collect new app registration's settings:
        Azure Active Directory -> App registrations -> [App name] -> Overview
        Save:
            **Application (client) ID**
            **Directory (tenant) ID**
        ... -> Endpoints
        Save:
            client secret **Value**
### 1.4. Add app roles
        Azure Active Directory -> App registrations -> [App name] -> App roles
        -> Create app role
            Display name:           airflow_viewer
            Allowed member types:   Users/Groups
            Value:                  airflow_viewer
            Description:            Viewer

            Repeat for roles:
                airflow_user
                airflow_public
                airflow_op
                airflow_admin
### 1.5. Add assignments "users/groups <---> roles"
        Azure Active Directory -> Enterprise applications -> [App name] -> Users and groups
        -> Add user/group
### 1.6. Grant admin consent
        Azure Active Directory -> App registrations -> [App name] -> API permissions
        -> Grant admin consent
            Should be:
                Permission name: User.Read (Sign in and read user profile)

## 2. CONFIGURE and RUN (local test) AIRFLOW
    webserver_config.py is used to configure authentication method.
    Clone this repo:
        git clone <url>
### 2.1. Fill env.list.template with values from 1.3 and rename it to env.list
### 2.2. Execute a list of commands to run Airflow webserver as a docker container
sudo useradd airflow -u 50000 -s /usr/sbin/nologin && \
sudo chown -R airflow $(pwd)/airflow-oauth-azure-test/airflow && \
docker run -d -p 8080:8080 \
  --name airflow-webserver \
  -v $(pwd)/airflow-oauth-azure-test/airflow:/opt/airflow \
  --env-file $(pwd)/airflow-oauth-azure-test/env.list \
   apache/airflow webserver && \
sleep 60 && \
docker exec airflow-webserver airflow db init
### 2.3. Check Azure AD OAuth2 authentication in Airflow 2
Open http://localhost:8080 in your browser and try to authorize as an Azure user (assignment to some Airflow role should be done in 1.5).
