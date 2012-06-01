import grok
import pytz

from datetime import datetime

from zope import component
from zope.processlifetime import IDatabaseOpenedWithRoot
from zope.app.publication.zopepublication import ZopePublication

from zope.lifecycleevent import ObjectRemovedEvent

from z3c import taskqueue
from z3c.taskqueue import processor
from z3c.taskqueue.startup import databaseOpened
from z3c.taskqueue.job import CronJob as BaseCronJob
from z3c.taskqueue.service import TaskService
from z3c.taskqueue.interfaces import CRONJOB, DELAYED

from raptus.mailcone.cronjob import interfaces
from raptus.mailcone.core import bases
from raptus.mailcone.core.interfaces import IMailcone, IIntIdManager





class CronJob(BaseCronJob, grok.Model):
    grok.implements(interfaces.ICronJob)

    @property
    def time_of_next_call(self):
        dt = datetime.utcfromtimestamp(self.timeOfNextCall())
        return datetime(dt.year,dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond, tzinfo=pytz.UTC)



class CronJobContainer(TaskService, bases.Container, grok.LocalUtility):
    """ note this container is registered as public utility
        from raptus.mailcone.app directly in the grok site!
    """
    grok.implements(interfaces.ICronJobContainer)
    grok.provides(interfaces.ICronJobContainer)
    grok.name('raptus.mailcone.cronjob.cron_job_container')
    
    processorFactory = processor.MultiProcessor
    taskInterface = interfaces.ITask


    def __init__(self):
        super(CronJobContainer, self).__init__()
        self.jobs = self

    def __getitem__(self, id):
        return super(CronJobContainer, self).__getitem__(str(id))
    
    def __setitem__(self, id, obj):
        super(CronJobContainer, self).__setitem__(str(id), obj)

    def reschedule(self, jobid):
        job = self[jobid]
        if job.delay is None:
            job.status = CRONJOB
        else:
            job.status = DELAYED
        self._scheduledQueue.put(job)

    def addCronJob(self, task, input=None, minute=(), hour=(),
                   dayOfMonth=(),  month=(), dayOfWeek=(), delay=None,):
        """ - add custom cronjob so we can subclassing in future
            - notified required events for catalog
        """
        jobid = self._generateId()
        newjob = CronJob(jobid, task, input,
                minute, hour, dayOfMonth, month, dayOfWeek, delay)
        self[str(jobid)] = newjob
        if newjob.delay is None:
            newjob.status = CRONJOB
        else:
            newjob.status = DELAYED
        self._scheduledQueue.put(newjob)
        return jobid

    def deleteCronJob(self, jobid):
        data = list()
        for i in self._scheduledQueue:
            if not i.id == jobid:
                data.append(i)
        self._scheduledQueue._data = tuple(data)
        del self[str(jobid)]
        
    def getCronJob(self, jobid):
        return self[str(jobid)]



@grok.subscribe(interfaces.ICronJob, grok.IObjectModifiedEvent)
def cronjob_modified_event(obj, event):
    container = component.getUtility(interfaces.ICronJobContainerLocator)()
    container.reschedule(obj.__name__)



class CronJobContainerLocator(bases.BaseLocator):
    splitedpath = ['cronjobs']
grok.global_utility(CronJobContainerLocator, provides=interfaces.ICronJobContainerLocator)



@grok.subscribe(IDatabaseOpenedWithRoot)
def database_opened_cronjobs(event):
    # so we don't need to add some configuration in zope.conf
    from zope.app.appsetup.product import setProductConfiguration
    db = event.database
    connection = db.open()
    root = connection.root()
    root_folder = root.get(ZopePublication.root_name, None)
    for app in root_folder.values():
        if IMailcone.providedBy(app):
            name = 'z3c.taskqueue@%s' % app.__name__
            site = '%s@*'%app.__name__
            setProductConfiguration(name, dict(autostart=site))
            databaseOpened(event, name)
            taskqueue.GLOBALDB = event.database
    connection.close()



