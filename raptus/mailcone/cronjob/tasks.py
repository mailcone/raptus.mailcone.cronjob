import grok
import datetime

from megrok import rdb

from zope import component
from zope.schema import vocabulary
from zope.schema.fieldproperty import FieldProperty

from raptus.mailcone.rules.processor import process
from raptus.mailcone.mails.contents import Mail

from raptus.mailcone.cronjob import _
from raptus.mailcone.cronjob.interfaces import ITask





class ProcessRulesTask(object):
    grok.implements(ITask)
    
    name = _('Process Rules')
    inputSchema = FieldProperty(ITask['inputSchema'])
    outputSchema = FieldProperty(ITask['outputSchema'])

    def __call__(self, service, jobid, input):
        process()
        return 'rules processed'
grok.global_utility(ProcessRulesTask, name='raptus.mailcone.cronjob.process_rules_task')



class CleanupMails7Days(object):
    grok.implements(ITask)
    
    delay = 7
    
    @property
    def name(self):
        return _('Remove mails older than ${days} days', mapping=dict(days=self.delay))
    
    def __call__(self, service, jobid, input):
        session = rdb.Session()
        filter = Mail.parsing_date < datetime.datetime.now() - datetime.timedelta(seconds=self.delay)
        session.query(Mail).filter(filter).delete()
grok.global_utility(CleanupMails7Days, name='raptus.mailcone.cronjob.cleanupmails_07_days')


class CleanupMails14Days(CleanupMails7Days):
    delay = 14
grok.global_utility(CleanupMails14Days, name='raptus.mailcone.cronjob.cleanupmails_14_days')


class CleanupMails30Days(CleanupMails7Days):
    delay = 30
grok.global_utility(CleanupMails30Days, name='raptus.mailcone.cronjob.cleanupmails_30_days')


class CleanupMails60Days(CleanupMails7Days):
    delay = 60
grok.global_utility(CleanupMails60Days, name='raptus.mailcone.cronjob.cleanupmails_60_days')



register = vocabulary.getVocabularyRegistry().register
def vocabulary_task(context):
    terms = list()
    for name, task in component.getUtilitiesFor(ITask):
        terms.append(vocabulary.SimpleTerm(value=name, title=task.name))
    return vocabulary.SimpleVocabulary(terms)
register('raptus.mailcone.cronjob.tasks', vocabulary_task)
