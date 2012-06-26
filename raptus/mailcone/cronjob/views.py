import os
import grok

from zope import component
from zope.schema import vocabulary
from zope.container.contained import notifyContainerModified
from zope.formlib.itemswidgets import MultiSelectWidget, SelectWidget
from zope.publisher.interfaces import NotFound
from z3c.taskqueue.interfaces import ICronJob, PROCESSING

from raptus.mailcone.core.interfaces import IMailcone
from raptus.mailcone.layout.views import Page, EditForm, AddForm, EditForm, DeleteForm, DisplayForm
from raptus.mailcone.layout.datatable import BaseDataTable
from raptus.mailcone.layout.interfaces import ICronjobMenu
from raptus.mailcone.layout.navigation import locatormenuitem
from raptus.mailcone.core import utils

from raptus.mailcone.cronjob import _
from raptus.mailcone.cronjob import interfaces
from raptus.mailcone.cronjob import contents

grok.templatedir('templates')



def vocabulary_range(*args):
    return vocabulary.SimpleVocabulary([vocabulary.SimpleTerm(i) for i in range(*args)])

class WidgetMinute(MultiSelectWidget):
    vocabulary = vocabulary_range(0,60,5)
    def __init__(self, field, request):
        super(WidgetMinute, self).__init__(field, self.vocabulary, request)

class WidgetHour(WidgetMinute):
    vocabulary = vocabulary_range(24)

class WidgetDayOfMonth(WidgetMinute):
    vocabulary = vocabulary_range(1, 31)

class WidgetMonth(WidgetMinute):
    def __init__(self, field, request):
        self.vocabulary = self._enumerate(self._calendar().getMonthNames())
        super(MultiSelectWidget, self).__init__(field, self.vocabulary, request)
    
    def _calendar(self):
        return utils.getRequest().locale.dates.calendars['gregorian']
    
    def _enumerate(self, values):
        return vocabulary.SimpleVocabulary([vocabulary.SimpleTerm(value=i,title=v) for i,v in enumerate(values)])

class WidgetDayOfWeek(WidgetMonth):
    def __init__(self, field, request):
        self.vocabulary = self._enumerate(self._calendar().getDayNames())
        super(MultiSelectWidget, self).__init__(field, self.vocabulary, request)

class WidgetTask(SelectWidget):
    def __init__(self, field, request):
        voca = vocabulary.getVocabularyRegistry().get(field.context,'raptus.mailcone.cronjob.tasks')
        super(WidgetTask, self).__init__(field, voca, request)


def getCronJobsFields():
    form_fields = grok.Fields(interfaces.ICronJob).select('task', 'minute', 'hour', 'dayOfMonth',
                                                              'month', 'dayOfWeek','delay')
    form_fields['minute'].custom_widget = WidgetMinute
    form_fields['hour'].custom_widget = WidgetHour
    form_fields['dayOfMonth'].custom_widget = WidgetDayOfMonth
    form_fields['month'].custom_widget = WidgetMonth
    form_fields['dayOfWeek'].custom_widget = WidgetDayOfWeek
    form_fields['task'].custom_widget = WidgetTask
    form_fields['delay'].field.description = _('One Time Job if a value is set (all others settings are ignored). Time in second from now.')
    return form_fields



class CronJobTable(BaseDataTable):
    grok.context(interfaces.ICronJobContainer)
    interface_fields = interfaces.ICronJob
    select_fields = ['id', 'time_of_next_call', 'started', 'status']
    actions = ( dict( title = _('manual run'),
                      cssclass = 'ui-icon ui-icon-arrowrefresh-1-s',
                      link = 'manualrun'),
                dict( title = _('delete'),
                      cssclass = 'ui-icon ui-icon-trash ui-modal-minsize ui-datatable-ajaxlink',
                      link = 'deletecronjobform'),
                dict( title = _('edit'),
                      cssclass = 'ui-icon ui-icon-pencil ui-datatable-ajaxlink',
                      link = 'editcronjobform'),)
    
    def _metadata(self, objs):
        css_class = dict()
        for index, obj in enumerate(objs):
            css_class[index] = obj.status == PROCESSING and 'table-color-red' or ' '
        return dict(css_class = css_class)



class CronJobs(Page):
    grok.name('index')
    grok.context(interfaces.ICronJobContainer)
    locatormenuitem(ICronjobMenu, interfaces.ICronJobContainerLocator, _(u'Tasks'))
    
    @property
    def cronjobtable(self):
        return CronJobTable(self.context, self.request).html()
    
    @property
    def addurl(self):
        return '%s/addcronjobform' % grok.url(self.request, self.context)



class AddCronJobForm(AddForm):
    grok.context(interfaces.ICronJobContainer)
    grok.require('zope.Public')

    form_fields = getCronJobsFields()
    
    def create(self, **data):
        
        kw = dict(task = data['task'],
                  minute = data['minute'],
                  hour = data['hour'],
                  dayOfMonth = data['dayOfMonth'],
                  month = data['month'],
                  dayOfWeek = data['dayOfWeek'],
                  delay = data['delay'])
        
        return self.context.addCronJob(**kw)

    def add(self, obj):
        pass
    
    def apply(self, obj, **data):
        pass



class EditCronJobForm(EditForm):
    grok.context(interfaces.ICronJob)
    grok.require('zope.Public')
    form_fields = getCronJobsFields()
    label = _('Edit cron job')

    def apply(self, **data):
        super(EditCronJobForm, self).apply(**data)
        notifyContainerModified(self.context)



class DeleteCronJobForm(DeleteForm):
    grok.context(interfaces.ICronJob)
    grok.require('zope.Public')
    form_fields = getCronJobsFields()
    
    def item_title(self):
        return str(getattr(self.context, 'name', self.context.id))
    
    def delete(self):
        self.context.__parent__.deleteCronJob(self.context.id)



class ManualRun(grok.View):
    grok.context(interfaces.ICronJob)

    def render(self):
        container = component.getUtility(interfaces.ICronJobContainerLocator)()
        container._queue.put(self.context)
        self.redirect(grok.url(self.request, container))



