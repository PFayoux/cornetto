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
import logging
import errno
import os
import threading
import sh
from flask import current_app
from sqlalchemy.orm.exc import NoResultFound
from typing import Dict, Any

from cornetto.bg_services import bg_open_archive_to_visualize, bg_extract_archive_to_prod, bg_save_to_archive
from cornetto.models import StatificationHistoric
from cornetto.models.ErrorTypeMIME import ErrorTypeMIME
from cornetto.models.ExternalLink import ExternalLink
from cornetto.models.HtmlError import HtmlError
from cornetto.models.ScannedFile import ScannedFile
from cornetto.models.ScrapyError import ScrapyError
from cornetto.models.Statification import Statification
from cornetto.models.StatificationHistoric import StatificationHistoric
from cornetto.service_utils import service_do_clean_directory, validate_sha, clear_status_background

logger = logging.getLogger('cornetto')


# ========
# Services
# ========


def service_get_last_statif_infos() -> Dict[str, Any]:
    """
    Get the last statification information. The following information will be returned in a python dict :
    -   sha            :   a string that contain the sha of the last statification,
                            if the last is a new and unsaved statification it will be empty
    -   designation       :   the designation of the last statification, or empty
    -   description       :   the description of the last statification, or empty
    -   status            :   the status of the last statification :  CREATED = 0
                                                                    STATIFIED = 1
                                                                    SAVED = 2
                                                                    PRODUCTION = 3
                                                                    VISUALIZED = 4
                            Default status will be 3, if there is no statification in the database the user will still
                            be able to create a new one, if there are ongoing statification to be push to prod it still
                            give the hand to the user that have saved it.
    - i_nb_item_to_crawl  : the number of item that have been crawled during the last statification, it will be used
                            as a reference of the number of items to crawl to the next statification.

    @return a python dict containing the above information
             {
                sha,
                designation,
                description,
                status,
                i_nb_item_to_crawl
             }
    """
    # initialize the number of item to crawl to 0
    i_nb_item_to_crawl = 0
    # initialize commit to empty value
    sha = ''
    # set designation and description as empty
    designation = ''
    description = ''
    # default status will be 3 (PRODUCTION), if there is no statification in the database the user will still be able
    # to create a new one, if there are ongoing statification to be push to prod it still give the hand to
    # the user that have saved it.
    status = 3

    # get the 2 last statification that have been created, when the statification process will start the last
    # statification to be created will be the current one (unsaved)
    last_statification = Statification.get_n_list_statifications(current_app.session, 2, 0, Statification.id, 'desc')

    # check if the list of statification isn't empty
    if len(last_statification) != 0:

        if len(last_statification) > 1:
            # get the number of item crawled in the previous statification (preceding the new one created)
            i_nb_item_to_crawl = last_statification[1]['nb_item']

        # get the status and the commit sha of the last statification
        status = last_statification[0]['status']
        sha = last_statification[0]['sha']

        # if the last statification is a new one that has not been saved
        if sha == '':
            designation = last_statification[0]['designation']
            description = last_statification[0]['description']

    return {
        'sha': sha,
        'designation': designation,
        'description': description,
        'status': status,
        'i_nb_item_to_crawl': i_nb_item_to_crawl
    }


def service_get_statif_count() -> Dict[str, int]:
    """
    Get the number of statifications in the database.
    @return the number of statifications
    """
    return {
        'count': Statification.get_count(current_app.session)
    }


def service_get_satif_list(i_limit: int, i_skip: int, s_order: str) -> Dict[str, Any]:
    """
    Get the list of statifications requested with the following parameters :
    @param i_limit: number of statification to request
    @param i_skip: number of statification to skip
    @param s_order: name of the colum to sort the statification by
    @return a python dict containing the list of the statifications returned by the request
    """
    order = Statification.id

    # get the Statification attribute corresponding to the column to order by
    if s_order == 'cre_date':
        order = Statification.cre_date
    elif s_order == 'upd_date':
        order = Statification.upd_date
    elif s_order == 'designation':
        order = Statification.designation
    elif s_order == 'status':
        order = Statification.status

    # get the first 'limit' since the 'skip' statifications, if there is less return all
    a_statifications = Statification.get_n_list_statifications(current_app.session, i_limit, i_skip, order, 'desc')

    return {
        'statifications': a_statifications
    }


def service_get_statif_info(s_archive_sha: str) -> Dict[str, Any]:
    """
    Get the statification information for the given commit sha, with all the data included in associated objects.
    For the current statification, it will return a python dict containing :
      -  statification : the data of object statification
      -  errors_type_mime : the list of errors type mime
      -  external_links : the list of external links
      -  html_errors : the list of html errors
      -  scanned_files : the list of scanned files
      -  scrapy_errors : the list of scrapy errors
      -  statification_historics : the list of statification historics.

    @return a python dict containing all the information of the current statification
    """
    # initialize empty variable
    s_statification = None
    a_errors_type_mime = None
    a_external_links = None
    a_html_errors = None
    a_scanned_files = None
    a_scrapy_errors = None
    a_statification_historic = None

    try:
        # verify that the commit is valid if not , if it is empty then
        if s_archive_sha != '':
            validate_sha(s_archive_sha)

        try:
            # get the statification corresponding to the commit and the associated objects
            statification = Statification.get_statification(current_app.session, s_archive_sha)
            # get the JSON from this statification
            s_statification = statification.get_dict()

            # get other objects associated to the statification and their JSON
            try:
                a_errors_type_mime = statification.get_list_from_class(ErrorTypeMIME, current_app.session)
            except NoResultFound as e:
                current_app.logger.info(e)
            try:
                a_external_links = statification.get_list_from_class(ExternalLink, current_app.session)
            except NoResultFound as e:
                current_app.logger.info(e)
            try:
                a_html_errors = statification.get_list_from_class(HtmlError, current_app.session)
            except NoResultFound as e:
                current_app.logger.info(e)
            try:
                a_scanned_files = statification.get_list_from_class(ScannedFile, current_app.session)
            except NoResultFound as e:
                current_app.logger.info(e)
            try:
                a_scrapy_errors = statification.get_list_from_class(ScrapyError, current_app.session)
            except NoResultFound as e:
                current_app.logger.info(e)
            try:
                a_statification_historic = statification.get_list_from_class(StatificationHistoric, current_app.session)
            except NoResultFound as e:
                current_app.logger.info(e)
        except NoResultFound as e:
            current_app.logger.info(e)

        # Return a python dict with all information
        return {
            'statification': s_statification,
            'errors_type_mime': a_errors_type_mime,
            'external_links': a_external_links,
            'html_errors': a_html_errors,
            'scanned_files': a_scanned_files,
            'scrapy_errors': a_scrapy_errors,
            'statification_historics': a_statification_historic
        }
    except SyntaxError as e:
        current_app.logger.error(e)
        # return an error code if the commit is not valid
        return {
            'success': False,
            'error': 'commit_unvalid'
        }
    except sh.ErrorReturnCode:
        # if an error has occurred during a subprocess
        return {
            'success': False,
            'error': 'system_fail'
        }


def service_do_start_statif(s_user: str, s_designation: str, s_description: str) -> Dict[str, Any]:
    """
    This method will initialize and start a statification process, this will do the following :
        - Delete the statusBackground file to create a new one containing the information of the statification process
        - Initialize the statification repository
        - Clear all source file in the repository to start in a clean repo
        - Verify that the log directory is accessible to write log
        - Delete the old statif.log file if it exist
        - Start the statification process, it will launch the crawler and begin to create the statification

    If an error happen during the process it will be caught and transferred as a RuntimeError to the parent method with
    a specific error code.
    @return  if everything goes smoothly the following python dict will be returned :
                {
                    'success': True,
                }
    :raise RuntimeError
    """

    clear_status_background()

    # if the field are set and if the process is stopped
    if s_user and s_designation and not current_app.statifProcess.is_running():
        try:
            # reinitialize the repository
            service_do_clean_directory(current_app.config['STATIC_REPOSITORY'])

            try:
                # try to create the folder LOGDIR
                os.makedirs(current_app.config['LOGDIR'])
            except OSError as e:
                # if the folder does not exist raise an error
                if not (e.errno == errno.EEXIST and os.path.isdir(current_app.config['LOGDIR'])):
                    # log the error
                    current_app.logger.error("Error while creating folder \n" + str(e))
                    # return an error code
                    raise RuntimeError('system_fail')

            try:
                # if the static.log exist we delete it
                os.remove(current_app.config['LOGFILE'])
            except FileNotFoundError:
                # if the log file is not found
                current_app.logger.info("The log does not exist yet")

            # create an object statification and start a process of statification
            current_app.statifProcess.start(current_app.session, s_designation, s_description, s_user)

            # on success return a success code
            return {
                'success': True
            }
        except sh.ErrorReturnCode as e:
            current_app.logger.error(str(e))
            # if an error has happened when executing a subprocess command
            raise RuntimeError('subprocess')

    # send a specific error code depending on the cause of error
    if not s_user:
        current_app.logger.error("Parameter X-Forwarded-User empty")
        raise RuntimeError('forwarded_user_empty')
    if not s_designation:
        current_app.logger.error("Parameter designation empty")
        raise RuntimeError('field_empty')
    else:
        current_app.logger.error("Process is running")
        raise RuntimeError('process_running')


def service_do_save(s_user: str) -> Dict[str, Any]:
    """
    Save the satification to a tag.gz archive

    @param s_user is needed and should correspond to a username
    @return  if everything goes smoothly the following python dict will be returned :
                {
                    'success': True,
                }

    :raise RuntimeError if an error happen during the process it will be caught and transferred as a RuntimeError to the
                        parent method with a specific error code.
    """
    clear_status_background()

    try:
        if not s_user:
            current_app.logger.error("Parameter X-Forwarded-User empty")
            raise RuntimeError('forwarded_user_empty')

        # Select the git repository
        git = sh.git.bake(_cwd=current_app.config['STATIC_REPOSITORY'], _tty_out=False)

        current_app.logger.info('> Add all modifications')

        current_app.logger.info('> Create a new archive')

        args = (
            s_user,
            current_app.config['ARCHIVE_REPOSITORY'],
            current_app.config['STATIC_REPOSITORY'],
            current_app.config['LOGFILE'],
            current_app.config['LOGDIR'],
            current_app.config['LOCKFILE'],
            current_app.config['STATUS_BACKGROUND'],
            current_app.config['DATABASE_URI']
        )

        # execute code asynchronously
        thread = threading.Thread(target=bg_save_to_archive, args=args)
        thread.daemon = True
        thread.start()

        # on success return a success code ,
        # user (front) will need to wait for background process to finish
        return {
            'success': True
        }

    except FileNotFoundError as e:
        # if the log file is not found
        current_app.logger.error("The log file " + current_app.config['LOGFILE'] + " wasn't found \n" + str(e))
        # if an error has happened when executing a subprocess command
        raise RuntimeError('system_fail')
    except threading.ThreadError as e:
        current_app.logger.error(str(e))
        # if an error has happened when executing the background thread
        raise RuntimeError('subprocess')


def service_do_apply_prod(s_user: str, s_archive_sha: str) -> Dict[str, Any]:
    """
    Push the desired statification (commit) in production.

    This method will call a background process to treat asynchronously the push operation which can take a long time,
    it will return before the background process is finished.

    @param s_user is needed and should correspond to a username
    @param s_archive_sha is needed and should correspond to a valid commit
    @return  if everything goes smoothly the following python dict will be returned :
                {
                    'success': True,
                }
    @raise RuntimeError if an error happen during the process it will be caught and transferred as a RuntimeError to the
                        parent method with a specific error code.
    """
    # this try except is there to check if commit or user are valid
    try:
        if not s_user:
            current_app.logger.error("Parameter X-Forwarded-User empty")
            raise RuntimeError('forwarded_user_empty')

        validate_sha(s_archive_sha)

        clear_status_background()

        # reinitialise the STATIC repository before checking out the last commit
        # ensure sources are up to date
        service_do_clean_directory(current_app.config['STATIC_REPOSITORY'])

        current_app.logger.info('> Load the statification sha')

        args = (
            s_archive_sha,
            s_user,
            current_app.config['PUSH_TO_PROD_SCRIPT'],
            current_app.config['STATUS_BACKGROUND'],
            current_app.config['LOCKFILE'],
            current_app.config['DATABASE_URI']
        )

        # execute code asynchronously
        thread = threading.Thread(target=bg_extract_archive_to_prod, args=args)
        thread.daemon = True
        thread.start()

        # on success return a success code
        return {
            'success': True
        }

    except SyntaxError as e:
        current_app.logger.error(e)
        # on fail write an error
        raise RuntimeError('commit_unvalid')
    except threading.ThreadError as e:
        current_app.logger.error(str(e))
        # if an error has happened when executing the background thread
        raise RuntimeError('subprocess')


def service_do_visualize(s_user: str, s_archive_sha: str) -> Dict[str, Any]:
    """
    Checkout a specified commit into the 'Visualize' repository to visualize a precedent statification.

    This method will call a background process to treat asynchronously the push operation which can take a long time,
    it will return before the background process is finished.

    @param s_user is needed and should correspond to a username
    @param s_archive_sha is needed and should correspond to a valid commit
    @return  if everything goes smoothly the following python dict will be returned :
                {
                    'success': True,
                }
    :raise RuntimeError if an error happen during the process it will be caught and transferred as a RuntimeError to the
                        parent method with a specific error code.
    """
    try:
        if not s_user:
            current_app.logger.error("Parameter X-Forwarded-User empty")
            raise RuntimeError('forwarded_user_empty')

        validate_sha(s_archive_sha)

        clear_status_background()

        current_app.logger.info('> Doing visualization operations')

        args = (
            s_archive_sha,
            s_user,
            current_app.config['ARCHIVE_REPOSITORY'],
            current_app.config['VISUALIZE_REPOSITORY'],
            current_app.config['STATUS_BACKGROUND'],
            current_app.config['LOCKFILE'],
            current_app.config['DATABASE_URI']
        )

        # execute code asynchronously
        thread = threading.Thread(target=bg_open_archive_to_visualize, args=args)
        thread.daemon = True
        thread.start()

        # on success a success code
        return {
            'success': True
        }
    except SyntaxError as e:
        current_app.logger.error(str(e))
        # on fail write an error
        raise RuntimeError('commit_unvalid')
    except threading.ThreadError as e:
        current_app.logger.error(str(e))
        # if an error has happened when executing the background thread
        raise RuntimeError('subprocess')

