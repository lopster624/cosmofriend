import datetime

import requests
import vk
from django.contrib import auth
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse

from engine.settings import SOCIAL_AUTH_VK_OAUTH2_KEY as CLIENT_ID, SOCIAL_AUTH_VK_OAUTH2_SECRET as CLIENT_SECRET
from .forms import *
from .models import *


class Home(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'cosmos/home.html', context={})


def logout(request):
    auth.logout(request)
    return redirect('home')

@login_required
def get_code(request):
    code = request.GET.get('code', '')
    redirect_uri = request.build_absolute_uri(reverse('get_code'))
    answer = requests.get(
        f'https://oauth.vk.com/access_token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&redirect_uri={redirect_uri}&code={code}')
    request.session['access_token'] = answer.json()['access_token']
    return redirect('import_friends')


class ImportFriends(LoginRequiredMixin, View):
    def get(self, request):
        access_token = request.session['access_token']
        session = vk.Session(access_token=access_token)
        vk_api = vk.API(session)
        friends_list = vk_api.friends.get(fields='bdate, photo_50, photo_max, about', v='5.130')['items']
        request.session['friends_list'] = friends_list
        return render(request, 'cosmos/import_friends.html', context={'f_list': friends_list})

    def post(self, request):
        chosen_friends = request.POST.getlist('exported_friends')
        chosen_friends = [int(friend_id) for friend_id in chosen_friends]
        friends_list = request.session['friends_list']
        for user in friends_list:
            if user.get('id') in chosen_friends:
                new_friend = Friends(name=f"{user.get('first_name')} {user.get('last_name')}", user=request.user)
                character = user.get('about')
                if character is not None:
                    new_friend.character = character
                date_of_birth = user.get('bdate')
                if date_of_birth:
                    date_of_birth = date_of_birth.split('.')
                    if len(date_of_birth) == 3:
                        date_of_birth = datetime.date(int(date_of_birth[2]), int(date_of_birth[1]),
                                                      int(date_of_birth[0]))
                        new_friend.date_birth = date_of_birth
                new_friend.get_remote_image(id_user=user.get('id'), url=user.get('photo_max'))
        return redirect('friends')


class FriendsList(LoginRequiredMixin, View):
    def get(self, request):
        f_list = Friends.objects.filter(user=request.user)
        redirect_uri = request.build_absolute_uri(reverse('get_code'))
        return render(request, 'cosmos/friends.html',
                      context={'f_list': f_list, 'client_id': CLIENT_ID, 'redirect_uri': redirect_uri})


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
        print(friend)
        friend.delete()
        # удаляет всех пользователей
        # for i in Friends.objects.filter(user=request.user):
        #    i.delete()
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
                friend = Friends.objects.get(id=mem)
                friend.points += 1
                friend.save()
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
            return render(request, 'cosmos/create_event.html', context={'form': bound_form})


class EditEvent(LoginRequiredMixin, View):
    def get(self, request, event_id):
        event = Events.objects.get(id=event_id)
        photos = Photos.objects.filter(event=event_id)
        videos = Videos.objects.filter(event=event_id)
        bound_form = CreateEventForm(instance=event, current_user=request.user)
        bound_form.fields['images'].label = "Добавить новые фотографии"
        bound_form.fields['videos'].label = "Добавить новые видео"
        return render(request, 'cosmos/edit_event.html',
                      context={'form': bound_form, 'photos': photos, 'event': event, 'videos': videos})

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
