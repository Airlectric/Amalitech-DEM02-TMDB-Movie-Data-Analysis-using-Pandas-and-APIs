import logging
from logging.handlers import RotatingFileHandler
import os

# Determine project root relative to this file
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

log_dir = os.path.join(project_root, 'logs')
os.makedirs(log_dir, exist_ok=True)

log_file_path = os.path.join(log_dir, 'app.log')

# created a logger named movie_project_logger
logger = logging.getLogger('movie_project_logger')

# set the general logger level to debug 
logger.setLevel(logging.DEBUG) 


# this help solve the issue of duplicate logs
if not logger.handlers:

    # a handler for the console
	console = logging.StreamHandler()
	console.setLevel(logging.DEBUG)

	# logging to a file called app.log and ensuring the logs don't grow too large
	file = RotatingFileHandler(
		log_file_path,
		maxBytes=2_000_000,
		backupCount=5
	)
	file.setLevel(logging.DEBUG)

    # formatting the log message format
	formatter = logging.Formatter(
		"%(asctime)s - %(levelname)s - %(module)s - %(message)s"
	)

	# added the formatter to the console and file 
	console.setFormatter(formatter)
	file.setFormatter(formatter)

	logger.addHandler(console)
	logger.addHandler(file)
