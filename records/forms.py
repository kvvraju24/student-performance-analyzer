from django import forms
from .models import Student, Subject

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['code', 'cohort']

class ScoreForm(forms.Form):
    subject = forms.ModelChoiceField(queryset=Subject.objects.all().order_by('name'))
    score = forms.IntegerField(min_value=0, max_value=100)
