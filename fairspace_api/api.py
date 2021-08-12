import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Optional, Sequence, Dict

import requests
import sys

from rdflib import Graph
from requests import Response

log = logging.getLogger('fairspace_api')

def use_or_read_value(value: str, variable: str) -> str:
    if value is not None and len(value) > 0:
        return value
    value = os.environ.get(variable)
    log.info(f'Reading variable {variable} from environment.')
    if value is None or len(value) == 0:
        raise Exception(f'Please configure the {variable} environment variable.')
    return value


@dataclass
class Count:
    totalElements: int
    timeout: bool


@dataclass
class Page:
    totalPages: int
    totalElements: int
    rows: Sequence[any]
    hasNext: bool
    timeout: bool
    page: Optional[int] = None
    size: Optional[int] = None


class FairspaceApi:
    def __init__(self,
                 url=None,
                 keycloak_url=None,
                 realm=None,
                 client_id=None,
                 client_secret=None,
                 username=None,
                 password=None
                 ):
        self.url = use_or_read_value(url, 'FAIRSPACE_URL')
        self.keycloak_url = use_or_read_value(keycloak_url, 'KEYCLOAK_URL')
        self.realm = use_or_read_value(realm, 'KEYCLOAK_REALM')
        self.client_id = use_or_read_value(client_id, 'KEYCLOAK_CLIENT_ID')
        self.client_secret = use_or_read_value(client_secret, 'KEYCLOAK_CLIENT_SECRET')
        self.username = use_or_read_value(username, 'KEYCLOAK_USERNAME')
        self.password = use_or_read_value(password, 'KEYCLOAK_PASSWORD')
        self.current_token: Optional[str] = None
        self.token_expiry = None

    def fetch_token(self) -> str:
        """

        :return:
        """
        # Fetch access token
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'username': self.username,
            'password': self.password,
            'grant_type': 'password'
        }
        headers = {
            'Content-type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        response = requests.post(f"{self.keycloak_url}/auth/realms/{self.realm}/protocol/openid-connect/token",
                                 data=params,
                                 headers=headers)
        if not response.ok:
            log.error('Error fetching token!')
            log.error(f'{response.status_code} {response.reason}')
            sys.exit(1)
        data = response.json()
        token = data['access_token']
        self.current_token = token
        self.token_expiry = time.time() + data['expires_in']
        return token

    def get_token(self) -> str:
        token_expiration_buffer = 5
        if self.token_expiry is None or self.token_expiry <= time.time() + token_expiration_buffer:
            return self.fetch_token()
        return self.current_token

    def find_or_create_workspace(self, code):
        # Fetch existing workspaces
        headers = {'Authorization': 'Bearer ' + self.get_token()}
        response = requests.get(f'{self.url}/api/workspaces/', headers=headers)
        if not response.ok:
            log.error('Error fetching workspaces')
            log.error(f'{response.status_code} {response.reason}')
            sys.exit(1)
        workspaces = response.json()
        matches = [ws for ws in workspaces if ws['code'] == code]
        if len(matches) > 0:
            return matches[0]

        # Create new workspace
        log.info('Creating new workspace ...')
        headers['Content-type'] = 'application/json'
        response: Response = requests.put(f'{self.url}/api/workspaces/',
                                          data=json.dumps({'code': code, 'title': code}),
                                          headers=headers)
        if not response.ok:
            log.error('Error creating workspace!')
            log.error(f'{response.status_code} {response.reason}')
            sys.exit(1)
        log.info('Workspace created.')
        return response.json()

    def exists(self, path):
        """ Check if a path exists
        """
        headers = {
            'Depth': '0',
            'Authorization': 'Bearer ' + self.get_token()
        }
        response = requests.request('PROPFIND', f'{self.url}/api/webdav/{path}/', headers=headers)
        return response.ok

    def ensure_dir(self, path, workspace=None):
        if self.exists(path):
            return
        # Create directory
        headers = {'Authorization': 'Bearer ' + self.get_token()}
        if workspace is not None:
            headers['Owner'] = workspace['iri']
        response: Response = requests.request('MKCOL', f'{self.url}/api/webdav/{path}/', headers=headers)
        if not response.ok:
            log.error(f"Error creating directory '{path}'!")
            log.error(f'{response.status_code} {response.reason}')
            sys.exit(1)

    def upload_files(self, path, files: Dict[str, any]):
        # Upload files
        start = time.time()
        headers = {
            'Authorization': 'Bearer ' + self.get_token()
        }
        response = requests.post(f'{self.url}/api/webdav/{path}/',
                                 data={'action': 'upload_files'},
                                 files=files,
                                 headers=headers)
        if not response.ok:
            log.error(f"Error uploading files into '{path}'!")
            log.error(f'{response.status_code} {response.reason}')
            sys.exit(1)

    def upload_files_by_path(self, path, files):
        self.upload_files(path, {filename: open(file, 'rb') for (filename, file) in files.items()})

    def upload_empty_files(self, path, filenames):
        self.upload_files(path, {filename: '' for filename in filenames})

    def upload_metadata(self, fmt, data):
        start = time.time()
        if fmt == 'turtle':
            content_type = 'text/turtle'
        elif fmt == 'ld+json':
            content_type = 'application/ld+json'
        else:
            log.error(f'Unsupported format: {fmt}')
            sys.exit(1)
        headers = {
            'Content-type': content_type,
            'Authorization': 'Bearer ' + self.get_token()
        }
        response = requests.put(f"{self.url}/api/metadata/",
                                data=data if fmt == 'turtle' else json.dumps(data),
                                headers=headers)
        if not response.ok:
            log.error('Error uploading metadata!')
            log.error(f'{response.status_code} {response.reason}')
            sys.exit(1)

    def upload_metadata_graph(self, graph: Graph):
        self.upload_metadata('turtle', graph.serialize(format='turtle').decode('utf-8'))

    def query_sparql(self, query: str):
        start = time.time()
        headers = {
            'Content-Type': 'application/sparql-query',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.get_token()
        }
        response = requests.post(f"{self.url}/api/rdf/query", data=query, headers=headers)
        if not response.ok:
            log.error('Error querying metadata!')
            log.error(f'{response.status_code} {response.reason}')
            sys.exit(1)
        return response.json()

    def retrieve_view_config(self) -> Page:
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.get_token()
        }
        response = requests.get(f"{self.url}/api/views/", headers=headers)
        if not response.ok:
            log.error(f'Error retrieving view config!')
            log.error(f'{response.status_code} {response.reason}')
            sys.exit(1)
        return response.json()

    def retrieve_view_page(self,
                           view: str,
                           page=1,
                           size=20,
                           include_counts=False,
                           include_joined_views=False,
                           filters=None) -> Page:
        data = {
            'view': view,
            'page': page,
            'size': size,
            'includeCounts': include_counts,
            'includeJoinedViews': include_joined_views
        }
        if filters is not None:
            data['filters'] = filters
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.get_token()
        }
        response = requests.post(f"{self.url}/api/views/", data=json.dumps(data), headers=headers)
        if not response.ok:
            log.error(f'Error retrieving {view} view page!')
            log.error(f'{response.status_code} {response.reason}')
            sys.exit(1)
        print(response.json())
        return Page(**response.json())

    def count(self,
              view: str,
              filters=None) -> Count:
        data = {
            'view': view
        }
        if filters is not None:
            data['filters'] = filters
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.get_token()
        }
        response = requests.post(f"{self.url}/api/views/count", data=json.dumps(data), headers=headers)
        if not response.ok:
            log.error(f'Error retrieving count for {view} view!')
            log.error(f'{response.status_code} {response.reason}')
            sys.exit(1)
        return Count(**response.json())

    def reindex(self):
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.get_token()
        }
        response = requests.post(f"{self.url}/api/maintenance/reindex", None, headers=headers)
        if not response.ok:
            log.error(f'Error reindexing!')
            log.error(f'{response.status_code} {response.reason}')
            sys.exit(1)

