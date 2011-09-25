import grok

from z3c.taskqueue.interfaces import ICronJob

from raptus.mailcone.layout.views import Page, EditForm


grok.template_dir('templates')

class CronjobSettings(Page, EditForm):
    form_fields = grok.AutoFields(ICronJob)