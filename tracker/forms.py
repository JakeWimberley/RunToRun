from django import forms
from functools import partial

jqDateInput = forms.DateInput(attrs={'class':'datepicker'})
jqTimeInput = forms.TimeInput(attrs={'class':'spinner'})

class DiscussionForm(forms.Form):
    def __init__(self,*args,**kwargs):
      eventChoices = kwargs.pop('eventChoices')
      super(DiscussionForm,self).__init__(*args,**kwargs)
      self.fields['_event'] = forms.MultipleChoiceField(label='select one or more events',choices=[(x.id, str(x)) for x in eventChoices])
    _validDate = forms.DateField(label='valid date',widget=jqDateInput)
    _validTime = forms.TimeField(label='valid time',widget=jqTimeInput)
    _text = forms.CharField(label='discussion')
