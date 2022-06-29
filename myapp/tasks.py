import dramatiq
import time
import logging

logger = logging.getLogger(__name__)


@dramatiq.actor
def super_complicated_task():
    logger.info('starting task...')
    time.sleep(2)
    logger.info('still running...')
    time.sleep(2)
    logger.info('done!')