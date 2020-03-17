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
import logging
import shutil

from cornetto import archive_utils


def test_create_archive_and_rename_to_sha():
    """
    Test the creation of a tar.gz archive and the creation of it's sha
    """
    s_static_repository = '/tmp/static'
    s_archive_repository = '/tmp/archive'

    if not os.path.exists(s_static_repository):
        os.makedirs(s_static_repository, exist_ok=True)

    if not os.path.exists(s_archive_repository):
        os.makedirs(s_archive_repository, exist_ok=True)

    file = open(os.path.join(s_static_repository, 'test_file.html'), 'w')
    file.write('<html><body>test content<body></html>')
    file.close()

    if not os.path.isfile(os.path.join(s_static_repository, 'test_file.html')):
        raise FileNotFoundError('test file not found')

    sha = archive_utils.create_archive_and_rename_to_sha(s_static_repository, s_archive_repository)

    assert sha != ''
    assert os.path.isfile(os.path.join(s_archive_repository, sha+'.tar.gz'))

    # remove created directories
    shutil.rmtree(s_static_repository)
    shutil.rmtree(s_archive_repository)


def test_execute_the_push_to_prod_script(caplog):
    """
    Test the creation of a tar.gz archive and the creation of it's sha
    """
    s_script_file_path = '/tmp/script_test.sh'
    script_file = open(s_script_file_path, 'w')
    script_file.write('''
    #!/bin/bash
    echo 'script test executed'
    echo $1
    ''')
    script_file.close()

    if not os.path.isfile(s_script_file_path):
        raise FileNotFoundError('test file not found')

    # get the logger
    caplog.set_level(logging.INFO, logger="cornetto")

    # execute the method to test the execution
    archive_utils.execute_the_push_to_prod_script('sha', s_script_file_path)

    # verify that the method has correctly executed the script and the correct log has been recorded
    assert caplog.record_tuples == [
        ("cornetto", logging.INFO, "script test executed\n"),
        ("cornetto", logging.INFO, "sha\n")
    ]

    # remove created file
    os.remove(s_script_file_path)


def test_extract_archive_to_directory():
    s_static_repository = '/tmp/static'
    s_archive_repository = '/tmp/archive'
    s_destination_repository = '/tmp/destination'

    if not os.path.exists(s_static_repository):
        os.makedirs(s_static_repository, exist_ok=True)

    if not os.path.exists(s_archive_repository):
        os.makedirs(s_archive_repository, exist_ok=True)

    if not os.path.exists(s_destination_repository):
        os.makedirs(s_destination_repository, exist_ok=True)

    file = open(os.path.join(s_static_repository, 'test_file.html'), 'w')
    file.write('<html><body>test content<body></html>')
    file.close()

    if not os.path.isfile(os.path.join(s_static_repository, 'test_file.html')):
        raise FileNotFoundError('test file not found')

    sha = archive_utils.create_archive_and_rename_to_sha(s_static_repository, s_archive_repository)

    archive_utils.extract_archive_to_directory(sha, s_archive_repository, s_destination_repository)

    assert os.path.isfile(os.path.join(s_destination_repository, 'test_file.html'))

    file = open(os.path.join(s_destination_repository, 'test_file.html'), 'r')
    file_content = file.read()
    file.close()

    assert file_content == '<html><body>test content<body></html>'

    # remove created directories
    shutil.rmtree(s_static_repository)
    shutil.rmtree(s_destination_repository)
    shutil.rmtree(s_archive_repository)
