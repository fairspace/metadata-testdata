import json
import logging
import time
from dataclasses import dataclass
from typing import Optional, Sequence

import requests
import sys

from rdflib import Graph
from requests import Request, Session, Response

log = logging.getLogger('fairspace_api')


def report_duration(task, start):
    duration = time.time() - start
    if duration >= 1:
        log.info(f'{task} took {duration:.0f}s.')
    else:
        log.info(f'{task} took {1000*duration:.0f}ms.')


@dataclass
class Count:
    totalElements: int


@dataclass
class Page:
    totalPages: int
    totalElements: int
    page: int
    size: int
    rows: Sequence[any]
    hasNext: bool


class FairspaceApi:
    def __init__(self,
                 url='http://localhost:8080',
                 keycloak_url='http://localhost:5100',
                 client_id='workspace-client',
                 client_secret='**********',
                 username='organisation-admin',
                 password='fairspace123'
                 ):
        self.url = url
        self.keycloak_url = keycloak_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.current_session: Optional[Session] = None
        self.token_expiry = None

    def fetch_token(self) -> str:
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
        response = requests.post(f"{self.keycloak_url}/auth/realms/fairspace/protocol/openid-connect/token",
                                 data=params,
                                 headers=headers)
        if not response.ok:
            log.error('Error fetching token!', response.json())
            sys.exit(1)
        data = response.json()
        token = data['access_token']
        self.token_expiry = time.time() + data['expires_in']
        return token

    def init_session(self):
        token = self.fetch_token()
        self.current_session = Session()
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
        response = self.current_session.get(f'{self.url}/api/v1/users/current',
                                            headers=headers)
        log.info(f"Initialised session for user {response.json()['username']}")

    def session(self) -> Session:
        if self.current_session is None or self.token_expiry is None or self.token_expiry <= time.time() + 5:
            self.init_session()
        return self.current_session

    def find_or_create_workspace(self, name):
        # Fetch existing workspaces
        response = self.session().get(f'{self.url}/api/v1/workspaces/')
        if not response.ok:
            log.error('Error fetching workspaces')
            log.error(f'{response.status_code} {response.reason}')
            sys.exit(1)
        workspaces = response.json()
        matches = [ws for ws in workspaces if ws['name'] == name]
        if len(matches) > 0:
            return matches[0]

        # Create new workspace
        log.info('Creating new workspace ...')
        headers = {
            'Content-type': 'application/json'
        }
        response: Response = self.session().put(f'{self.url}/api/v1/workspaces/',
                                                data=json.dumps({'name': name, 'comment': name}),
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
            'Depth': '0'
        }
        req = Request('PROPFIND', f'{self.url}/api/v1/webdav/{path}/', headers, cookies=self.session().cookies)
        response = self.session().send(req.prepare())
        return response.ok

    def ensure_dir(self, path, workspace=None):
        if self.exists(path):
            return
        # Create directory
        headers = {} if workspace is None else {'Owner': workspace['iri']}
        req = Request('MKCOL', f'{self.url}/api/v1/webdav/{path}/', headers, cookies=self.session().cookies)
        response: Response = self.session().send(req.prepare())
        if not response.ok:
            log.error(f"Error creating directory '{path}'!")
            log.error(f'{response.status_code} {response.reason}')
            sys.exit(1)

    def upload_files(self, path, files):
        # Upload files
        start = time.time()
        response = self.session().post(f'{self.url}/api/v1/webdav/{path}/',
                                       data={'action': 'upload_files'},
                                       files=files)
        if not response.ok:
            log.error(f"Error uploading files into '{path}'!")
            log.error(f'{response.status_code} {response.reason}')
            sys.exit(1)
        report_duration('Uploading files', start)

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
        headers = {'Content-type': content_type}
        response = self.session().put(f"{self.url}/api/v1/metadata/",
                                      data=data if fmt == 'turtle' else json.dumps(data),
                                      headers=headers)
        if not response.ok:
            log.error('Error uploading metadata!')
            log.error(f'{response.status_code} {response.reason}')
            sys.exit(1)
        report_duration('Uploading metadata', start)

    def upload_metadata_graph(self, graph: Graph):
        self.upload_metadata('turtle', graph.serialize(format='turtle').decode('utf-8'))

    def query_sparql(self, query: str):
        start = time.time()
        headers = {
            'Content-Type': 'application/sparql-query',
            'Accept': 'application/json'
        }
        response = self.session().post(f"{self.url}/api/v1/rdf/query", data=query, headers=headers)
        if not response.ok:
            log.error('Error querying metadata!')
            log.error(f'{response.status_code} {response.reason}')
            sys.exit(1)
        report_duration('Querying', start)
        return response.json()

    def retrieve_view_config(self) -> Page:
        headers = {
            'Accept': 'application/json'
        }
        response = self.session().get(f"{self.url}/api/v1/views/", headers=headers)
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
            'Accept': 'application/json'
        }
        response = self.session().post(f"{self.url}/api/v1/views/", data=json.dumps(data), headers=headers)
        if not response.ok:
            log.error(f'Error retrieving {view} view page!')
            log.error(f'{response.status_code} {response.reason}')
            sys.exit(1)
        return Page(**response.json())

    def retrieve_count(self,
                       view: str,
                       filters=None) -> Count:
        data = {
            'view': view
        }
        if filters is not None:
            data['filters'] = filters
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        response = self.session().post(f"{self.url}/api/v1/views/count", data=json.dumps(data), headers=headers)
        if not response.ok:
            log.error(f'Error retrieving count for {view} view!')
            log.error(f'{response.status_code} {response.reason}')
            sys.exit(1)
        return Count(**response.json())
