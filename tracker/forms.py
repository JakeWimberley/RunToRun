from django import forms
from functools import partial
from .models import Thread, Event, Tag

# JS/JQuery will be present in template to stylize these inputs
jqDateInput = forms.DateInput(attrs={'class':'uiDatepicker'})
jqTimeInput = forms.TimeInput(attrs={'class':'timeBox'})
monthChoices = [
    (1,'Jan'),(2,'Feb'),(3,'Mar'),(4,'Apr'),(5,'May'),(6,'Jun'),
    (7,'Jul'),(8,'Aug'),(9,'Sep'),(10,'Oct'),(11,'Nov'),(12,'Dec'),
    (99,'All year') # handled as special case in find view
]

class ThreadForm(forms.Form):
    def __init__(self,*args,**kwargs):
      eventChoices = kwargs.pop('eventChoices')
      selectedChoice = kwargs.pop('selectedChoice')
      super(ThreadForm,self).__init__(*args,**kwargs)
      self.fields['_event'] = forms.MultipleChoiceField(label='select one or more events',choices=[(x.id, str(x)) for x in eventChoices],required=False,initial=selectedChoice)
    _title = forms.CharField(label='title')
    _validDate = forms.DateField(label='valid date (UTC)',widget=jqDateInput)
    _validTime = forms.TimeField(label='valid time (UTC)',widget=jqTimeInput,input_formats=['%H:%M','%H%M'])
    _isExtensible = forms.BooleanField(required=False,initial=True,label='allow extension by other users')
    _text = forms.CharField(label='the first discussion',widget=forms.Textarea)

class DiscussionFormTextOnly(forms.Form):
    _text = forms.CharField(label='discussion',widget=forms.Textarea)

class EventForm(forms.Form):
    #def __init__(self,*args,**kwargs):
    #  super(EventForm,self).__init__(*args,**kwargs)
    #  self.fields['_threadChoices'] = forms.MultipleChoiceField(choices=[(x.id,str(x)) for x in Thread.objects.all()])
    #  super(EventForm, self).full_clean()
    _title = forms.CharField(label='name this event')
    _isPinned = forms.BooleanField(required=False,initial=True,label='pin this event to your Home view')
    _isPublic = forms.BooleanField(required=False,label='share this event with other users')
    _isPermanent = forms.BooleanField(required=False,label='keep this event forever')
    _startDate = forms.DateField(required=False,label='start date (UTC, optional)',widget=jqDateInput)
    _startTime = forms.TimeField(required=False,label='start time (UTC, optional)',widget=jqTimeInput,input_formats=['%H:%M','%H%M'])
    _endDate = forms.DateField(required=False,label='end date (UTC, optional unless start date defined)',widget=jqDateInput)
    _endTime = forms.TimeField(required=False,label='end time (UTC, optional)',widget=jqTimeInput,input_formats=['%H:%M','%H%M'])
    # thread choice field will be populated asynchronously based on time specs
    # NOTE you will have to comment this out when starting a new database, then uncomment after migrate
    _threadChoices = forms.MultipleChoiceField(label='associate with threads (optional)',required=False,choices=[(x.id,str(x)) for x in Thread.objects.all()])
    #_threadChoices = forms.MultipleChoiceField(label='associate with threads (optional)',required=False)

class ChangeEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title','startDate','endDate','isPublic','isPermanent']

class ChangeThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['title','validDate']

class FindForm(forms.Form):
    # NOTE you will have to comment this out when starting a new database, then uncomment after migrate
    tags = forms.MultipleChoiceField(required=False,label='return events with tag(s)',widget=forms.CheckboxSelectMultiple(attrs={'id':'findTags'}),choices=[(x.name,x.name) for x in Tag.objects.all()])
    #tags = forms.MultipleChoiceField(required=False,label='return events with tag(s)',widget=forms.CheckboxSelectMultiple(attrs={'id':'findTags'}))
    textSearch = forms.CharField(required=False,label='return threads containing text')
    months = forms.MultipleChoiceField(required=False,label='get results from only these months',widget=forms.CheckboxSelectMultiple(attrs={'id':'findMonths'}),choices=monthChoices)
    textSearch = forms.CharField(required=False,label='return threads containing text')
    months = forms.MultipleChoiceField(required=False,label='get results from only these months',widget=forms.CheckboxSelectMultiple(attrs={'id':'findMonths'}),choices=monthChoices)
