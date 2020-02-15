import logging
import os

from datetime import datetime

from sqlalchemy.orm.exc import NoResultFound

from cornetto.models import StatificationHistoric, Actions, open_session_db
from cornetto.models.Statification import Statification, Status
from cornetto.models.StatificationHistoric import StatificationHistoric
from cornetto.archive_utils import extract_archive_to_directory, execute_the_push_to_prod_script, \
    create_archive_and_rename_to_sha
from cornetto.service_utils import write_status_background, unlock_access, service_do_clean_directory

logger = logging.getLogger('cornetto')


# ==========================
# Background service creator
# ==========================


def bg_save_to_archive(s_user: str, s_project_directory: str, s_archive_repository: str,
                       s_static_repository: str, s_log_file: str, s_log_dir: str, s_lock_file: str,
                       s_file_status_background: str, s_database_uri: str):
    """

    @param s_user:
    @param s_project_directory:
    @param s_archive_repository:
    @param s_static_repository:
    @param s_log_file:
    @param s_log_dir:
    @param s_lock_file:
    @param s_file_status_background:
    @param s_database_uri:
    """
    try:
        # create a session for this specific code , because it's executed after the flask instance has been killed
        session = open_session_db(s_database_uri)

        s_archive_sha = create_archive_and_rename_to_sha(s_project_directory, s_static_repository, s_archive_repository)

        logger.info('> Rename log file with the archive sha')

        # rename the logfile of the statification by the archive SHA
        os.rename(s_log_file, s_log_dir + "/" + s_archive_sha + ".log")

        logger.info('> Register the Sha into the database')

        # update the current statification with no sha with the new sha
        Statification.upd_commit(session, '', s_archive_sha)

        # Now the statification is archived so we change the status from statified to SAVED
        Statification.upd_status(session, s_archive_sha, Status.SAVED)

        # update the date of update of the statification
        Statification.upd_upd_date(session, s_archive_sha, datetime.utcnow())

        # create a StatificationHistoric to keep track of the modification
        Statification.static_add_object_to_statification(StatificationHistoric,
                                                         session,
                                                         s_archive_sha,
                                                         datetime.utcnow(),
                                                         s_user,
                                                         Actions.COMMIT_STATIFICATION)
        logger.info('> Commit operations terminated')

        # on success write a success code and the commit id
        write_status_background(
            {
                'success': True,
                'commit': s_archive_sha,
                'operation': 'commit'
            },
            s_file_status_background
        )
    except RuntimeError as e:
        logger.error(str(e))
        write_status_background(
            {
                'success': False,
                'error': 'subprocess',
                'operation': 'commit'
            },
            s_file_status_background
        )
    except FileNotFoundError as e:
        logger.error(str(e))
        write_status_background(
            {
                'success': False,
                'error': 'log_file',
                'operation': 'commit'
            },
            s_file_status_background
        )
    except (ValueError, NoResultFound) as e:
        logger.error(str(e))
        # if no statification was found for the given commit
        # write an error in the statusBackground file
        write_status_background(
            {
                'success': False,
                'error': 'database',
                'operation': 'commit'
            },
            s_file_status_background
        )
    finally:
        # always unlock the route
        unlock_access(s_lock_file)


def bg_extract_archive_to_prod(s_archive_sha: str, s_user: str, s_path_to_the_push_to_prod_script: str,
                               s_file_status_background: str, s_lock_file: str,
                               s_database_uri: str):
    """

    @param s_archive_sha:
    @param s_user:
    @param s_path_to_the_push_to_prod_script:
    @param s_file_status_background:
    @param s_lock_file:
    @param s_database_uri:
    """
    try:
        # create a session for this specific code , because it's executed after the flask instance has been killed
        session = open_session_db(s_database_uri)

        logger.info('> Push the statification to production server(s)')

        execute_the_push_to_prod_script(s_archive_sha, s_path_to_the_push_to_prod_script)

        logger.info('> Change status of the last statification push to prod to saved')

        # catch error if there is some
        try:
            # change the status of the previous put in Production statification to SAVED status
            Statification.switch_status(session, Status.PRODUCTION, Status.SAVED)
        except (ValueError, NoResultFound) as e:
            # in the case there was no statification that had the status PRODUCTION before, we just catch the error
            # and we continue as normal
            logger.info(str(e))

        logger.info('> Change status of the new statification to push to prod')

        # change status of the statification pushed to prod to PRODUCTION
        Statification.upd_status(session, s_archive_sha, Status.PRODUCTION)

        # update the date of update of the statification
        Statification.upd_upd_date(session, s_archive_sha, datetime.utcnow())

        # create a StatificationHistoric to keep track of the modification
        Statification.static_add_object_to_statification(StatificationHistoric, session, s_archive_sha,
                                                         datetime.utcnow(),
                                                         s_user,
                                                         Actions.PUSHTOPROD_STATIFICATION)

        logger.info('> Push to prod operations terminated')
        write_status_background(
            {
                'success': True,
                'operation': 'pushtoprod',
                'commit': s_archive_sha
            },
            s_file_status_background
        )
    except RuntimeError as e:
        logger.error(str(e))
        write_status_background(
            {
                'success': False,
                'error': 'subprocess',
                'operation': 'pushtoprod'
            },
            s_file_status_background
        )
    except (ValueError, NoResultFound) as e:
        # there is no reason the process execute the code here
        logger.error(str(e))
        write_status_background(
            {
                'success': False,
                'error': 'database',
                'operation': 'pushtoprod'
            },
            s_file_status_background
        )
    finally:
        # always unlock the route
        unlock_access(s_lock_file)


def bg_open_archive_to_visualize(s_archive_sha: str, s_user: str, s_archive_repository: str,
                                 s_visualize_repository: str,
                                 s_file_status_background: str, s_lock_file: str, s_database_uri: str):
    """

    @param s_archive_sha:
    @param s_user:
    @param s_archive_repository:
    @param s_visualize_repository:
    @param s_file_status_background:
    @param s_lock_file:
    @param s_database_uri:
    """
    try:
        # create a session for this specific code , because it's executed after the flask instance has been killed
        session = open_session_db(s_database_uri)

        # clean the repository
        service_do_clean_directory(s_visualize_repository)

        logger.info('> Extract the archive')

        # extract the wanted statification archive to the visualize directory
        extract_archive_to_directory(
            s_archive_sha,
            s_archive_repository,
            s_visualize_repository
        )

        logger.info('> Change status for last visualized statification to saved')

        try:
            # change the status of the previous Visualized statification to Saved status
            Statification.switch_status(session, Status.VISUALIZED, Status.SAVED)
        except (ValueError, NoResultFound) as e:
            # in the case there was no statification that had the status VISUALIZED before, we just catch the error
            # and we continue as normal
            logger.info(str(e))

        logger.info('> Change status for new visualized statification')

        # Now the statification is on the visualize repository so we change the status from default to visualized
        Statification.upd_status(session, s_archive_sha, Status.VISUALIZED)

        # update the date of update of the statification
        Statification.upd_upd_date(session, s_archive_sha, datetime.utcnow())

        # create a StatificationHistoric to keep track of the modification
        Statification.static_add_object_to_statification(StatificationHistoric, session, s_archive_sha,
                                                         datetime.utcnow(),
                                                         s_user,
                                                         Actions.VISUALIZE_STATIFICATION)
        # on success write a success code
        write_status_background(
            {'success': True, 'operation': 'visualize', 'commit': s_archive_sha},
            s_file_status_background
        )
    except (ValueError, NoResultFound) as e:
        # there is no reason the process execute the code here
        logger.error(str(e))
        write_status_background(
            {
                'success': False,
                'error': 'database',
                'operation': 'visualize'
            },
            s_file_status_background
        )
    except RuntimeError as e:
        logger.error(str(e))
        write_status_background(
            {
                'success': False,
                'error': 'subprocess',
                'operation': 'visualize'
            },
            s_file_status_background
        )
    finally:
        unlock_access(s_lock_file)
