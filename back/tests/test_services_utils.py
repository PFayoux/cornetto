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
import shutil
import pytest
import logging
import json

from cornetto import service_utils
from cornetto import archive_utils


def test_validate_sha():
    s_archive_directory = '/tmp/archive'
    s_static_directory = '/tmp/static'
    s_test_file_path = '/tmp/static/test_file.html'

    os.makedirs(s_static_directory, exist_ok=True)
    os.makedirs(s_archive_directory, exist_ok=True)

    assert os.path.isdir(s_static_directory)
    assert os.path.isdir(s_archive_directory)

    test_file = open(s_test_file_path, 'w')
    test_file.write('test file')
    test_file.close()

    sha = archive_utils.create_archive_and_rename_to_sha(s_static_directory, s_archive_directory)

    service_utils.validate_sha(sha, s_archive_directory)

    with pytest.raises(SyntaxError, match=r"The parameter does not respect the sha ID policies, value : "):
        service_utils.validate_sha('', s_archive_directory)

    with pytest.raises(SyntaxError, match=r"The parameter does not respect the sha ID policies, value : 123"):
        service_utils.validate_sha('123', s_archive_directory)

    with pytest.raises(NotADirectoryError,
                       match=r"The given archive directory path does'nt exist : /tmp/not_a_directory"):
        service_utils.validate_sha('', '/tmp/not_a_directory')

    shutil.rmtree(s_archive_directory)
    shutil.rmtree(s_static_directory)


def test_service_do_clean_directory(caplog):
    caplog.set_level(logging.INFO, logger="cornetto")

    s_static_directory = '/tmp/static'

    os.makedirs(s_static_directory, exist_ok=True)

    assert os.path.isdir(s_static_directory)

    file = open(os.path.join(s_static_directory, 'test_file'), 'w')
    file.write('test')
    file.close()

    service_utils.service_do_clean_directory(s_static_directory)

    list_files = os.listdir(s_static_directory)

    assert len(list_files) == 0

    shutil.rmtree(s_static_directory)

    with pytest.raises(NotADirectoryError, match=r"the static repository doesn\'t exist /tmp/static"):
        service_utils.service_do_clean_directory(s_static_directory)


def test_write_status_background(caplog):
    caplog.set_level(logging.INFO, logger="cornetto")

    s_file_status_background = '/tmp/test_status_background'
    s_test_status = {
        'test': 'value',
        'test2': 2,
        'test3': False
    }

    service_utils.write_status_background(s_test_status, s_file_status_background)

    assert os.path.isfile(s_file_status_background)
    file = open(s_file_status_background, 'r')
    status_dict = json.load(file)
    file.close()

    assert status_dict['test'] == 'value'
    assert status_dict['test2'] == 2
    assert status_dict['test3'] is False

