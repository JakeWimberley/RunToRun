from django import forms
from functools import partial

jqDateInput = forms.DateInput(attrs={'class':'uiDatepicker'})
jqTimeInput = forms.TimeInput() # TODO maybe not necessary

class ThreadForm(forms.Form):
    def __init__(self,*args,**kwargs):
      eventChoices = kwargs.pop('eventChoices')
      selectedChoice = kwargs.pop('selectedChoice')
      super(ThreadForm,self).__init__(*args,**kwargs)
      self.fields['_event'] = forms.MultipleChoiceField(label='select one or more events',choices=[(x.id, str(x)) for x in eventChoices],required=False,initial=selectedChoice)
    _title = forms.CharField(label='title')
    _validDate = forms.DateField(label='valid date (UTC)',widget=jqDateInput)
    _validTime = forms.TimeField(label='valid time (UTC)',widget=jqTimeInput,input_formats=['%H:%M','%H%M'])
    _text = forms.CharField(label='the first discussion',widget=forms.Textarea)

class DiscussionFormTextOnly(forms.Form):
    _text = forms.CharField(label='discussion',widget=forms.Textarea)

class EventForm(forms.Form):
    _title = forms.CharField(label='name this event')
    _isPinned = forms.BooleanField(required=False,initial=True,label='pin this event to your Home view')
    _isPublic = forms.BooleanField(required=False,label='share this event with other users')
    _isPermanent = forms.BooleanField(required=False,label='keep this event forever')
    _startDate = forms.DateField(required=False,label='start date (UTC, optional)',widget=jqDateInput)
    _startTime = forms.TimeField(required=False,label='start time (UTC, optional)',widget=jqTimeInput,input_formats=['%H:%M','%H%M'])
    _endDate = forms.DateField(required=False,label='end date (UTC, optional unless start date defined)',widget=jqDateInput)
    _endTime = forms.TimeField(required=False,label='end time (UTC, optional)',widget=jqTimeInput,input_formats=['%H:%M','%H%M'])
    # discussion choice field will be populated asynchronously based on time specs
    _threadChoices = forms.MultipleChoiceField(label='associate with threads (optional)',required=False)
