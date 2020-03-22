import re

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import View
from .utils import *
from .forms import *
from .models import *
from django.contrib.auth.models import User
from django.contrib import auth


class Home(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'cosmos/home.html', context={})


def logout(request):
    auth.logout(request)
    return redirect('home')


class FriendsList(LoginRequiredMixin, View):
    def get(self, request):
        f_list = Friends.objects.filter(user=request.user)
        return render(request, 'cosmos/friends.html', context={'f_list': f_list})


class EventsList(LoginRequiredMixin, View):
    def get(self, request):
        e_list = Events.objects.filter(user=request.user)
        return render(request, 'cosmos/events.html', context={'e_list': e_list, 'short': True})


class AddFriends(LoginRequiredMixin, View):
    def get(self, request):
        form = AddFrForm()
        return render(request, 'cosmos/add_friends.html', context={'form': form})

    def post(self, request):
        bound_form = AddFrForm(request.POST, request.FILES)
        if bound_form.is_valid():
            friend = bound_form.save(commit=False)
            friend.user = request.user
            if request.FILES:
                friend.photo = request.FILES['photo']
            friend.save()
            return redirect('friends')
        else:
            return render(request, 'cosmos/add_friends.html', context={'form': bound_form})


class Registration(View):
    def get(self, request):
        form = CustomRegister()
        return render(request, 'register.html', context={'form': form})

    def post(self, request):
        bound_form = CustomRegister(request.POST)
        if bound_form.is_valid():
            new_user = User.objects.create_user(
                username=request.POST['username'],
                password=request.POST['password'],
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name'])
            new_user.set_password(request.POST['password'])
            new_user.save()
            login(request, new_user)
            return redirect('home')
        else:
            return render(request, 'register.html', context={'form': bound_form})


class DeleteFriend(LoginRequiredMixin, View):
    def get(self, request, friend_id):
        friend = Friends.objects.get(id=friend_id)
        friend.delete()
        return redirect('friends')


class DeleteEvent(LoginRequiredMixin, View):
    def get(self, request, event_id):
        friend = Events.objects.get(id=event_id)
        friend.delete()
        return redirect('events')


class EditFriend(LoginRequiredMixin, View):
    def get(self, request, friend_id):
        friend = Friends.objects.get(id=friend_id)
        bound_form = AddFrForm(instance=friend)
        return render(request, 'cosmos/edit_friend.html', context={'form': bound_form, 'friend': friend})

    def post(self, request, friend_id):
        friend = Friends.objects.get(id=friend_id)
        bound_form = AddFrForm(request.POST, request.FILES, instance=friend)
        if bound_form.is_valid():
            friend = bound_form.save(commit=False)
            if request.FILES:
                friend.photo = request.FILES['photo']
            friend.save()
            return redirect('friends')
        else:
            return render(request, 'cosmos/add_friends.html', context={'form': bound_form, 'friend': friend})


class CreateEvent(LoginRequiredMixin, View):
    def get(self, request):
        form = CreateEventForm(current_user=request.user)
        return render(request, 'cosmos/create_event.html', context={'form': form})

    def post(self, request):
        bound_form = CreateEventForm(request.POST, request.FILES)
        if bound_form.is_valid():
            new_event = bound_form.save(commit=False)
            new_event.user = request.user
            new_event.save()
            for mem in request.POST.getlist('members'):
                new_event.members.add(mem)
            new_event.save()
            if request.FILES:
                for f in request.FILES.getlist('images'):
                    Photos(event=new_event, image=f).save()
                for f in request.FILES.getlist('videos'):
                    file_format = re.findall(r"\.mp4$", f.name)
                    if file_format:
                        video = Videos(event=new_event, video=f)
                        video.save()
                        video.title = video.video.name[18:]
                        video.save()
            return redirect('events')
        else:
            return render(request, 'cosmos/create_event.html', context={'form': bound_form})


class EditEvent(LoginRequiredMixin, View):
    def get(self, request, event_id):
        event = Events.objects.get(id=event_id)
        bound_form = CreateEventForm(instance=event, current_user=request.user)
        bound_form.fields['images'].label = "Добавить новые фотографии"
        bound_form.fields['videos'].label = "Добавить новые видео"
        return render(request, 'cosmos/edit_event.html', context={'form': bound_form, 'event': event})

    def post(self, request, event_id):
        event = Events.objects.get(id=event_id)
        bound_form = CreateEventForm(request.POST, request.FILES, instance=event, current_user=request.user)
        if bound_form.is_valid():
            new_event = bound_form.save(commit=False)
            new_event.save()
            for mem in request.POST.getlist('members'):
                new_event.members.add(mem)
            new_event.save()
            if request.FILES:
                for f in request.FILES.getlist('images'):
                    Photos(event=new_event, image=f).save()
                for f in request.FILES.getlist('videos'):
                    file_format = re.findall(r"\.mp4$", f.name)
                    if file_format:
                        video = Videos(event=new_event, video=f)
                        video.save()
                        video.title = video.video.name[18:]
                        video.save()
            return redirect('some_event', new_event.id)
        else:
            return render(request, 'cosmos/edit_event.html', context={'form': bound_form, 'event': event})


class SomeEvent(LoginRequiredMixin, View):
    def get(self, request, event_id):
        event = Events.objects.get(id=event_id)
        photos = Photos.objects.filter(event=event_id)
        videos = Videos.objects.filter(event=event_id)
        return render(request, 'cosmos/some_event.html', context={'photos': photos, 'event': event, 'videos': videos})


class SomeFriend(LoginRequiredMixin, View):
    def get(self, request, friend_id):
        friend = Friends.objects.get(id=friend_id)
        e_list = Events.objects.filter(user=request.user).filter(members__id__icontains=friend_id)
        return render(request, 'cosmos/some_friend.html', context={'friend': friend, 'e_list': e_list})