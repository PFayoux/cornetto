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

# APPS CONF

DEBUG = False
LOGLEVEL = 'INFO'

# define the log directory
LOGDIR = '/opt/cornetto/log/'
API_LOGFILE = '/opt/cornetto/log/api.log'

# the path to the virtual env, it is used to start scrapy as a subprocess
PYTHONPATH = '/opt/cornetto/venv/lib/python3.6/site-packages/'

# define the project directory, it should point to your installation of cornetto
PROJECT_DIRECTORY = '/opt/cornetto/'

# define the logfile used for the current statification
LOGFILE = '/opt/cornetto/log/statif.log'

# define the file used to store the pid of the statification process
PIDFILE = '/opt/cornetto/.pid.data'

# define the lock file use to block operation
LOCKFILE = '/opt/cornetto/.lock_access'

# define the file that will contain the number of crawled file
# it is updated during the statification process
# BEWARE modify scrapy_parser/spiders/MirroringSpider.py too if you change the path
CRAWLER_PROGRESS_COUNTER_FILE = '/opt/cornetto/.crawlerProgressCounterFile.txt'

# define the path to the file that will store the status of background process
STATUS_BACKGROUND = '/opt/cornetto/statusBackground.json'

# The path to the script that will be called to upload the statification to a production server
PUSH_TO_PROD_SCRIPT='/opt/cornetto/push_to_prod.sh'


# DATABASE

# deactivate tracking of modification for SQLAlchemy session (take extra resources if enabled)
SQLALCHEMY_TRACK_MODIFICATIONS = False

# the uri of the database
DATABASE_URI = 'sqlite:////opt/cornetto/cornetto.db'


# DIRECTORY CONFIGURATION

# define the directory where the statification should be created
STATIC_REPOSITORY = '/opt/cornetto/static/'
# define the directory where the statification to visualize should be deployed
VISUALIZE_REPOSITORY = '/opt/cornetto/visualize/'
# define the directory where the archives of statifications should be stored
ARCHIVE_REPOSITORY = '/opt/cornetto/archive/'


# CRAWLER CONF

# define the url of the website to crawl
URLS = 'http://web.your-private-domain.com'
# define the authorized domain(s)
DOMAINS = 'web.your-private-domain.com,www.web.com'
URL_REGEX = '(https?://)?web(.your-private-domain.com/?)?'
URL_REPLACEMENT = ''

# define the files to be deleted at the end of the process of statification
DELETE_FILES = ''
# define the directories to be deleted at the end of the process of statification
DELETE_DIRECTORIES = ''
