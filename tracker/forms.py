from django import forms
from functools import partial

jqDateInput = forms.DateInput(attrs={'class':'uiDatepicker'})
jqTimeInput = forms.TimeInput() # TODO maybe not necessary

class DiscussionForm(forms.Form):
    def __init__(self,*args,**kwargs):
      eventChoices = kwargs.pop('eventChoices')
      super(DiscussionForm,self).__init__(*args,**kwargs)
      self.fields['_event'] = forms.MultipleChoiceField(label='select one or more events',choices=[(x.id, str(x)) for x in eventChoices],required=False)
    _validDate = forms.DateField(label='valid date (UTC)',widget=jqDateInput)
    _validTime = forms.TimeField(label='valid time (UTC)',widget=jqTimeInput,input_formats=['%H:%M','%H%M'])
    _text = forms.CharField(label='discussion',widget=forms.Textarea)

class DiscussionFormTextOnly(forms.Form):
    _text = forms.CharField(label='discussion',widget=forms.Textarea)
