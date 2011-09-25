import grok

from z3c.taskqueue.interfaces import ICronJobs

from raptus.mailcone.core.interfaces import IMailcone
from raptus.mailcone.layout.views import Page, EditForm, AddForm

from raptus.mailcone.customers import interfaces

grok.templatedir('templates')

class CronjobSettings(AddForm, Page):
    grok.context(IMailcone)
    form_fields = grok.AutoFields(ICronJobs)