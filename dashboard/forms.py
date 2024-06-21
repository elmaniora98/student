from django.forms import widgets
from . models import *
from django import forms

class NotesForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title','description']

class HomeworkForm(forms.ModelForm):

    due = forms.DateTimeField(
        input_formats=['%Y-%m-%d %H:%M'], 
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%d %H:%M')
    )
    class Meta:
        model = Homework
        fields = ['title','subject','description','due','priority']

class DateInput(forms.DateInput):
    input_type = 'date'


"""class HomeworkForm(forms.ModelForm):
    due = forms.DateTimeField(
        input_formats=['%Y-%m-%d %H:%M'], 
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%d %H:%M')
    )

    class Meta:
        model = Homework
        fields = ['title', 'description', 'subject', 'due', 'priority']#class DashboardForm(forms.Form):
 #   text = forms.CharField(max_length=100,label ="Enter your search :")        

"""
class DashboardForm(forms.Form):
    text = forms.CharField(
        max_length=100,
        label="Enter your search :",
        widget=forms.TextInput(attrs={'class': 'inline-field'})
    )



from .models import Todo
class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'due_date', 'priority', 'tags', 'category', 'audio', 'video', 'file']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }



class ConversionForm(forms.Form):
    CHOICES = [('length','Length'),('mass','Mass')]
    measurement = forms.ChoiceField(choices = CHOICES, widget=forms.RadioSelect)

class ConversionLengthForm(forms.Form):
    CHOICES = [('yard','Yard'),('foot','Foot')]
    input = forms.CharField(required=False,label=False, widget=forms.TextInput(attrs ={'type':'number','placeholder':'Enter the number'}
                                                                               ))  
    measure1=forms.CharField(label='',widget=forms.Select(choices=CHOICES))

    measure2=forms.CharField(label='',widget=forms.Select(choices=CHOICES))


class ConversionMassForm(forms.Form):
    CHOICES = [('pound','Pound'),('kilogram','Kilogram')]
    input = forms.CharField(required=False,label=False, widget=forms.TextInput(attrs ={'type':'number','placeholder':'Enter the number'}
                                                                               ))  
    measure1=forms.CharField(label='',widget=forms.Select(choices=CHOICES))

    measure2=forms.CharField(label='',widget=forms.Select(choices=CHOICES))


class YouTubeSearchForm(forms.Form):
    text = forms.CharField(label='Search for videos', max_length=100)
    language = forms.ChoiceField(label='Language', choices=[
        ('en', 'English'),
        ('fr', 'Français'),
        ('es', 'Español'),
        ('de', 'Deutsch'),
        ('it', 'Italiano'),
        ('pt', 'Português')
    ])

class DashboardForms(forms.Form):
    text = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
