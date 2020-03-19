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
from sh import tar, shasum, rm, scp, bash
import logging

logger = logging.getLogger('cornetto')

# =================
# Archive Utilities
# =================


def create_archive_and_rename_to_sha(s_static_repository: str,
                                     s_archive_repository: str) -> str:
    """
    Create a new .tar.gz archive from the given s_static_repository.

    The archive is renamed with the sha and is moved to the s_archive_repository
    @param s_static_repository: the path to the directory of the statification
    @param s_archive_repository: the path to the directory that contain all the archive
    @return: the sha of the created archive
    """
    logger.info('> Create the statification archive')

    for log in tar(
            '-cf',
            'archive.tar.gz',
            '-C',
            # get the parent directory of s_static_repository
            os.path.abspath(os.path.join(s_static_repository, os.pardir)),
            # get the last directory of the path s_static_repository
            os.path.basename(os.path.normpath(s_static_repository)),
            _cwd='/tmp/',
            _tty_out=False,
            _iter='err'):
        # if there are error logs
        logger.error(log)

    logger.info('> Create the statification archive sha')

    if not os.path.isfile('/tmp/archive.tar.gz'):
        raise RuntimeError('The archive.tar.gz file does\'nt exist')

    s_archive_sha = ''
    for resultShasum in shasum('archive.tar.gz', _cwd='/tmp/', _tty_out=False, _iter='out'):
        s_archive_sha = resultShasum.split(' ')[0]

    if s_archive_sha is None:
        raise RuntimeError('The sha is empty')

    logger.info('> Rename the archive and move it to the archive directory')
    os.rename('/tmp/archive.tar.gz', s_archive_repository + "/" + s_archive_sha + ".tar.gz")

    return s_archive_sha


def execute_the_push_to_prod_script(s_archive_sha, s_path_to_the_push_to_prod_script: str):
    """
    This method will execute the script that will push the wanted statification archive to the production server
    @param s_archive_sha:
    @param s_path_to_the_push_to_prod_script
    """
    for log in bash(s_path_to_the_push_to_prod_script, s_archive_sha,  _tty_out=False, _iter=True):
        logger.info(log)


def extract_archive_to_directory(s_archive_sha, s_path_to_archive_directory, s_path_to_destination_directory):
    """
    Extract an archive to the wanted directory. This is used in to visualize a previous statification.
    @param s_archive_sha: the sha of the archive
    @param s_path_to_archive_directory: the path to archive directory
    @param s_path_to_destination_directory: the path to the directory where to extract the archive
    """
    s_archive_path = os.path.join(s_path_to_archive_directory, s_archive_sha+'.tar.gz')
    for log in tar('-xf', s_archive_path, '-C', s_path_to_destination_directory, '--strip-components=1', _cwd=s_path_to_archive_directory,
                   _tty_out=False, _iter='err'):
        logger.error(log)
