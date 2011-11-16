import logging
import z3c
from z3c.taskqueue import startup

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('raptus.mailcone.cronjob')


logger = logging.getLogger('raptus.mailcone.cronjob')
logger.warning('z3c.taskqueue.startup.storeDBReference patched!')
def storeDBReference(event):
    z3c.taskqueue.GLOBALDB = event.database
startup.storeDBReference = storeDBReference
