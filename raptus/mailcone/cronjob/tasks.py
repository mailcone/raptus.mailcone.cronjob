import grok


from zope import component
from zope.schema import vocabulary
from zope.schema.fieldproperty import FieldProperty

from raptus.mailcone.cronjob import _

from raptus.mailcone.cronjob.interfaces import ITask





class ProcessRulesTask(object):
    grok.implements(ITask)
    
    name = _('Process Rules')
    inputSchema = FieldProperty(ITask['inputSchema'])
    outputSchema = FieldProperty(ITask['outputSchema'])

    def __call__(self, service, jobid, input):
        return 'task return'
grok.global_utility(ProcessRulesTask, name='raptus.mailcone.cronjob.process_rules_task')



class ProcessMailsTask(object):
    grok.implements(ITask)
    
    name = _('Process Mails to Database')
    
    inputSchema = FieldProperty(ITask['inputSchema'])
    outputSchema = FieldProperty(ITask['outputSchema'])

    def __call__(self, service, jobid, input):
        return 'task return'
grok.global_utility(ProcessMailsTask, name='raptus.mailcone.cronjob.process_mails_task')



register = vocabulary.getVocabularyRegistry().register
def vocabulary_task(context):
    terms = list()
    for name, task in component.getUtilitiesFor(ITask):
        terms.append(vocabulary.SimpleTerm(value=name, title=task.name))
    return vocabulary.SimpleVocabulary(terms)
register('raptus.mailcone.cronjob.tasks', vocabulary_task)