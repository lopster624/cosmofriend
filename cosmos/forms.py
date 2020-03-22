from django.contrib.auth.models import User
from django.forms import ModelForm, ImageField, FileInput, FileField, Select, ModelChoiceField, ModelMultipleChoiceField
from django.forms.widgets import Input, Textarea
from django.views import View

from .models import *


class CustomRegister(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
        widgets = {
            'password': Input(attrs={
                'type': 'password',
                'class': 'form-control'
            }),
            'first_name': Input(attrs={'class': 'form-control'}),
            'last_name': Input(attrs={'class': 'form-control'}),
            'username': Input(attrs={'class': 'form-control'}),
        }


class AddFrForm(ModelForm):
    class Meta:
        model = Friends
        fields = ['name', 'character', 'date_birth', 'date_begin', 'photo']
        labels = {
            'name': 'Имя',
            'character': 'Описание',
            'date_birth': 'Дата рождения',
            'date_begin': 'Дата начала дружбы',
            'photo': 'Фотография',
        }
        widgets = {
            'name': Input(attrs={'class': 'form-control bg-dark text-white'}),
            'character': Textarea(attrs={
                'class': 'form-control bg-dark text-white',
                'rows': '3',
            }),
            'date_birth': Input(attrs={'class': 'form-control bg-dark text-white'}),
            'date_begin': Input(attrs={'class': 'form-control bg-dark text-white'}),
            'photo': Input(attrs={
                'class': 'form-control-file',
                'type': 'file',
                'accept': 'image/*',
            }),
        }


class CreateEventForm(ModelForm):
    images = ImageField(label='Фотографии', required=False, widget=FileInput(attrs={'multiple': 'multiple'}))
    videos = FileField(label='Видео', required=False, widget=FileInput(attrs={'multiple': 'multiple'}))
    members = ModelMultipleChoiceField(label='Участники', queryset=Friends.objects.all())

    class Meta:
        model = Events
        fields = ['title', 'report', 'date', 'points', 'members']
        widgets = {
            'title': Input(attrs={'class': 'form-control bg-dark text-white'}),
            'report': Textarea(attrs={
                'class': 'form-control bg-dark text-white',
                'rows': '3',
            }),
            'date': Input(attrs={'class': 'form-control bg-dark text-white'}),
            'points': Select(attrs={'class': 'form-control bg-dark text-white'}),
        }

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)
        super(CreateEventForm, self).__init__(*args, **kwargs)
        if current_user:
            self.fields['members'].queryset = Friends.objects.filter(user=current_user)


