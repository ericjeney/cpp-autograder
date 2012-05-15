from AutograderWeb.code_grader.models import Quiz
from django import forms

class UploadFileForm(forms.Form):
    name = forms.CharField(max_length=80)
    file = forms.FileField()
    
    def __init__(self, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        
        t = ()
        
        for q in Quiz.objects.order_by("-id").iterator():
            t = t+((q.id, q.title),)
        self.fields['quiz'] = forms.ChoiceField(choices=t)
        
    
class CreateQuizForm(forms.Form):
    title = forms.CharField(max_length=80)
    testcases = forms.FileField()
    answers = forms.FileField()
    password = forms.CharField(widget=forms.PasswordInput)
    passwordConfirm = forms.CharField(widget=forms.PasswordInput, label="Password (Again)")

    def clean_passwordConfirm(self):
        passA = self.cleaned_data['passwordConfirm']
        passB = self.cleaned_data['password']

        if(passA != passB):
            raise forms.ValidationError("Passwords Do Not Match!")

        return passA
    
class ViewQuizForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    def __init__(self, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)

        t = ()        
        for q in Quiz.objects.order_by("-id").iterator():
            t = t+((q.id, q.title),)
        self.fields['quiz'] = forms.ChoiceField(choices=t)
    