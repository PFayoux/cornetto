# coding=utf-8
"""
Cornetto

Copyright (C) 2018–2019 ANSSI
Contributors:
2018–2019 Bureau Applicatif tech-sdn-app@ssi.gouv.fr
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
from os.path import isfile, join
import logging
import errno
import fcntl
from sh import rm, ls
from flask.json import dumps, loads
from flask import current_app
from typing import Dict, Any

from cornetto.verification_utilities import valid_sha

logger = logging.getLogger('cornetto')

# =================
# Service Utilities
# =================


def validate_sha(s_sha: str, s_archive_directory: str):
    """
    Verify that an archive possess the given sha
    @param s_archive_directory: the archive directory
    @param s_sha: the sha of the static version
    @raise SyntaxError if the sha doesn't exist
    """
    try:
        if not os.path.isdir(s_archive_directory):
            raise NotADirectoryError("The given archive directory path does'nt exist : " + s_archive_directory)
        a_list_sha = []
        # browse all file in the archive directory
        for filename in os.listdir(s_archive_directory):
            if isfile(join(s_archive_directory, filename)):
                # remove the .tar.gz extension in the filename and add it to the list
                a_list_sha.append(filename.strip('.tar.gz'))

        # verify that the sha id is valid
        valid_sha(s_sha, a_list_sha)
    except SyntaxError as e:
        # if the parameter that should contain a sha wasn't valid, show an error in the log
        logger.error("The sha parameter is not correct : " + str(e))
        raise e


def is_access_locked() -> bool:
    """
    Test if the lockfile is locked
    @return a boolean true if it's locked, false is not
    """
    # by default we consider that the lockfile is locked
    is_locked = True

    logger.debug('Lockfile is lock ?')
    try:
        # open the file if it exist
        f_lock_file = open(current_app.config['LOCKFILE'], "r+")
    except FileNotFoundError:
        # create it if not
        f_lock_file = open(current_app.config['LOCKFILE'], "w+")

    try:
        # create an object lock with FileLock
        fcntl.flock(f_lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if not f_lock_file.read():
            # if the lock has been acquired, then it wasn't locked
            is_locked = False
    except IOError as e:
        # raise on IOErrors not related to LOCK (if it was lock an IOError is raised, but we ignore it)
        if e.errno != errno.EAGAIN:
            f_lock_file.close()
            raise
    finally:
        # release the lock
        fcntl.flock(f_lock_file, fcntl.LOCK_UN)
        f_lock_file.close()

    logger.debug('Route is lock : ' + str(is_locked))
    return is_locked


def lock_access():
    """
    Put a lock on the lockfile. The lockfile is used to block access to a route when doing some critical treatment.
    @raise IOError
    """
    try:
        # open the file if it exist
        f_lock_file = open(current_app.config['LOCKFILE'], "r+")
    except FileNotFoundError:
        # create it if not
        f_lock_file = open(current_app.config['LOCKFILE'], "w+")

    try:
        # create an object lock with FileLock
        fcntl.flock(f_lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        f_lock_file.write('locked')
    except IOError as e:
        logger.info('Fail to lock the route')
        # raise on IOErrors not related to LOCK
        if e.errno != errno.EAGAIN:
            f_lock_file.close()
            raise
    f_lock_file.close()
    logger.info('Locked the route')


def unlock_access(s_lock_file: str):
    """
    Release the lock on the lockfile
    """
    # erase the file if it exist, create it if it doesn't exist
    f_lock_file = open(s_lock_file, "w")
    # release the lock
    fcntl.flock(f_lock_file, fcntl.LOCK_UN)
    f_lock_file.close()
    logger.info('Unlocked the route')


def write_status_background(status: dict, s_file_status_background: str):
    """
    Write a status in the status background file
    """
    # open the file if it exist, create it if it doesn't exist
    with open(s_file_status_background, "w") as fStatusBackground:
        # write the status
        fStatusBackground.write(dumps(status))


def clear_status_background():
    """
    Clear the content of the status background file
    """
    f_status_background = open(current_app.config['STATUS_BACKGROUND'], "w+")
    f_status_background.close()


def get_nb_page_crawled() -> int:
    """
    Get the number of page crawled by the statificationProcess
    @return the number of page crawled, 0 if nothing is crawled or the file crawlerProgressCount.txt doesn't exist
    """
    i_current_nb_item_crawled = 0
    try:
        # open the crawler page counter file in read mode
        count_file = open(current_app.config['CRAWLER_PROGRESS_COUNTER_FILE'])
        i_current_nb_item_crawled = int(count_file.read())
        count_file.close()

    except (FileNotFoundError, ValueError)as e:
        current_app.logger.info('The file crawlerProgressCount.txt doesn\'t exist' + str(e))

    return i_current_nb_item_crawled


def get_background_status_file_content() -> Dict[str, Any]:
    """
    Read the content of the backgound status file if it exist and return the json content as a python dict.
    If the file is empty return an empty python dict
    @return a python dict containing the information contained in the file
    """
    dict_status_background = {}
    # look at the content of the file status background
    try:
        f_file_status_background = open(current_app.config['STATUS_BACKGROUND'], 'r')
        s_status_background = f_file_status_background.read()
        # if the file isn't empty
        if s_status_background:
            dict_status_background = loads(s_status_background)
        f_file_status_background.close()

    except FileNotFoundError:
        current_app.logger.info('No status background file')

    return dict_status_background


def service_do_clean_directory(s_repository: str):
    """
    Clean the statification directory
    @param s_repository - the path to the repository to clean
    """
    logger.info('> Static repository initialization ...')
    logger.debug('repository clean : ' + s_repository)

    # Select the static directory
    empty_static_directory = rm.bake('-rf', './*', _cwd=s_repository, _tty_out=False, _iter='out')

    # if the STATIC_REPOSITORY doesn't exist
    if not os.path.isdir(s_repository):
        logger.error('the static repository doesn\'t exist ' + s_repository)

    empty_static_directory()

    logger.info('> Static repository initialization terminated')
