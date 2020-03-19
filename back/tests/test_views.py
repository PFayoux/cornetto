# coding=utf-8
"""
Cornetto

Copyright (C) 2018–2020 ANSSI
Contributors:
2018–2020 Bureau Applicatif tech-sdn-app@ssi.gouv.fr
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
"""
import os

import pytest
from flask import json
from werkzeug.datastructures import Headers

from cornetto.models import open_session_db
from cornetto import create_app

config = {
    'DEBUG': True,
    'LOGLEVEL': 'INFO',
    'STATIC_REPOSITORY': '/tmp/',
    'ARCHIVE_REPOSITORY': '/tmp/',
    'VISUALIZE_REPOSITORY': '/tmp/',
    'PUSH_TO_PROD_SCRIPT': '/tmp/test.sh',
    'PYTHONPATH': '../venv/lib/python3.6/site-packages/', 
    'URL_GIT': '',
    'URLS': '',
    'DOMAINS': '',
    'API_LOGFILE': '/tmp/api.log',
    'LOGDIR': '/tmp/',
    'LOGFILE': '/tmp/statif.log',
    'PROJECT_DIRECTORY': './cornetto',
    'PIDFILE': '/tmp/.pid.data',
    'LOCKFILE': '/tmp/.lock_access',
    'STATUS_BACKGROUND': '/tmp/.status_background.json',
    'CRAWLER_PROGRESS_COUNTER_FILE': '/tmp/.crawlerProgressCounterFile.txt',
    'DELETE_FILES': '',
    'DELETE_DIRECTORIES': '',
    'URL_REGEX': '(https?://)?web(.your-private-domain.com/?)?',
    'URL_REPLACEMENT': '',
    'DATABASE_URI': 'sqlite:///:memory:',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False
}


@pytest.yield_fixture()
def setup_module():
    os.makedirs(os.path.dirname(config['LOCKFILE']), exist_ok=True)
    session = open_session_db('sqlite:///:memory:')


@pytest.yield_fixture()
def setup_fonction(): 
    test_file = open('/tmp/test.sh', 'w')
    test_file.write('echo "test"')
    test_file.close()
    app = create_app(None, config)
    yield {
        'client': app.test_client(),
        'designation': 'Statification Test',
        'description': 'A test statification for unit test',
        'x_forwarded_user': 'Username',
        'content_type': 'application/json'
    }


def test_statification_status(setup_module, setup_fonction):
    r = setup_fonction['client'].get(
        '/api/statification/status'
    )

    assert r.status_code == 200

    data = json.loads(r.get_data())
    assert data['sha'] == ''
    assert data['description'] == ''
    assert data['designation'] == ''
    assert not data['isLocked']
    assert not data['isRunning']
    assert data['nbItemToCrawl'] == 100
    assert data['status'] == 3
    assert data['statusBackground'] == {}
    assert data['status_code'] == 200


def test_do_start_statif(setup_module, setup_fonction):
    """
    TODO write a full test for do_start_statif
    """
    r = setup_fonction['client'].post(
        '/api/statification/start',
        data=json.dumps({
            'designation': setup_fonction['designation'],
            'description': setup_fonction['description']
        }),
        headers=Headers([
            ('X-Forwarded-User', setup_fonction['x_forwarded_user']),
            ('Content-Type', setup_fonction['content_type'])
        ])
    )

    assert r.status_code == 200

    data = json.loads(r.get_data())
    assert data['status_code'] == 200
