from django import forms

class DiscussionForm(forms.Form):
    def __init__(self,*args,**kwargs):
      eventChoices = kwargs.pop('eventChoices')
      super(DiscussionForm,self).__init__(*args,**kwargs)
      self.fields['_event'] = forms.MultipleChoiceField(label='select one or more events',choices=[(x.id, str(x)) for x in eventChoices])
    _valid = forms.SplitDateTimeField(label='valid at')
    _text = forms.CharField(label='discussion')
