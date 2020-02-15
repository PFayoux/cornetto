import os
from sh import tar, shasum, rm, scp, bash
import logging

logger = logging.getLogger('cornetto')

# =================
# Archive Utilities
# =================


def create_archive_and_rename_to_sha(s_project_directory: str, s_static_repository: str,
                                     s_archive_repository: str) -> str:
    """

    @param s_project_directory:
    @param s_static_repository:
    @param s_archive_repository:
    @return:
    """
    logger.info('> Create the statification archive')

    for log in tar(
            '-cf',
            s_static_repository+'.tar.gz',
            s_static_repository,
            _cwd=s_project_directory,
            _tty_out=False,
            _iter='err'):
        # if there are error logs
        logger.error(log)

    logger.info('> Create the statification archive sha')

    s_archive_sha = None
    for sha in shasum(s_static_repository+'.tar.gz', _cwd=s_project_directory, _tty_out=False, _iter='out'):
        s_archive_sha = sha

    if s_archive_sha is None:
        raise RuntimeError('The sha is empty')

    logger.info('> Rename the archive and move it to the archive directory')
    os.rename(s_static_repository + '.tar.gz', s_archive_repository + "/" + s_archive_sha + ".tar.gz")

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

    @param s_archive_sha:
    @param s_path_to_archive_directory:
    @param s_path_to_destination_directory:
    """
    s_archive_path = s_path_to_archive_directory+'/'+s_archive_sha+'.tar.gz'
    for log in tar('-xf', s_archive_path, s_path_to_destination_directory, _cwd=s_path_to_archive_directory,
                   _tty_out=False, _iter='err'):
        logger.error(log)
