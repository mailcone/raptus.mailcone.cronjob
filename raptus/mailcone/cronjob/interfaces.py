from zope import interface
from zope import schema
from zope.location.interfaces import ILocation

from z3c.taskqueue.interfaces import ITaskService
from z3c.taskqueue.interfaces import ITask as BaseITask
from z3c.taskqueue.interfaces import ICronJob as IBaseCronJob

from raptus.mailcone.core.interfaces import IContainer
from raptus.mailcone.core.interfaces import IContainerLocator

from raptus.mailcone.cronjob import _



class ICronJobContainer(ITaskService, ILocation):
    """ A container for cronjobs
    """



class ICronJobContainerLocator(IContainerLocator):
    """ interface for locate the cronjobs folder.
    """



class ICronJob(IBaseCronJob, IContainer):
    
    time_of_next_call = schema.Datetime(title=_('time of next call'), readonly=True)



class ITask(BaseITask):
    """ custom task
    """
    name = interface.Attribute('i18n name of this task')