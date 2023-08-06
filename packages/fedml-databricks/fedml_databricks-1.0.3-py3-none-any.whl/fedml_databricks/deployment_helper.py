import os
from subprocess import Popen, PIPE, STDOUT
from .logger import Logger

def _check_file_exists(file_path):
    logger = Logger.get_instance()
    try:
        return os.path.exists(file_path)
    except Exception as e:
        logger.error(e)
        raise


def _execute_script(command):
    logger = Logger.get_instance()
    try:
        process = Popen(command, stdout=PIPE, stderr=STDOUT, close_fds=True)
        for line in iter(process.stdout.readline, b''):
            logger.info(line.rstrip().decode('utf-8'))
        process.stdout.close()
        process.wait()
        return process.returncode
    except Exception as e:
        logger.error(e)
        raise