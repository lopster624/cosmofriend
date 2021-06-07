from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms import ModelForm, ImageField, FileInput, FileField, Select, ModelMultipleChoiceField
from django.forms.widgets import Input, Textarea
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


class AddFriendForm(ModelForm):
    class Meta:
        model = Friend
        fields = ['name', 'character', 'date_birth', 'date_begin', 'photo']
        labels = {
            'name': 'Имя',
            'character': 'Описание',
            'date_birth': 'Дата рождения',
            'date_begin': 'Дата начала дружбы',
            'photo': 'Фотография',
        }
        widgets = {
            'name': Input(attrs={'class': 'form-control bg-light'}),
            'character': Textarea(attrs={
                'class': 'form-control bg-light',
                'rows': '3',
            }),
            'date_birth': Input(attrs={'class': 'form-control bg-light', 'type': 'date'}),
            'date_begin': Input(attrs={'class': 'form-control bg-light', 'type': 'date'}),
            'photo': Input(attrs={
                'class': 'form-control-file',
                'type': 'file',
                'accept': 'image/*',
            }),
        }


class CreateEventForm(ModelForm):
    images = ImageField(label='Фотографии', required=False, widget=FileInput(attrs={'multiple': 'multiple'}))
    videos = FileField(label='Видео', required=False, widget=FileInput(attrs={'multiple': 'multiple'}))
    members = ModelMultipleChoiceField(
        label='Участники',
        queryset=Friend.objects.all(),
        required=True,
        widget=FilteredSelectMultiple('', is_stacked=False),
    )

    class Meta:
        model = Event
        fields = ['title', 'report', 'date', 'points', 'members']
        widgets = {
            'title': Input(attrs={'class': 'form-control bg-light mt-2'}),
            'report': Textarea(attrs={
                'class': 'form-control bg-light mt-2',
                'rows': '3',
            }),
            'date': Input(attrs={'class': 'form-control bg-light mt-2', 'type': 'date'}),
            'points': Select(attrs={'class': 'form-control bg-light mt-2'}),
            'members': FilteredSelectMultiple(u'Участники', is_stacked=False),
        }

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)
        super(CreateEventForm, self).__init__(*args, **kwargs)
        if current_user:
            self.fields['members'].queryset = Friend.objects.filter(user=current_user)
