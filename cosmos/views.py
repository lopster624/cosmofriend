import datetime
import uuid
import requests
import vk
from django.contrib import auth
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from engine.settings import SOCIAL_AUTH_VK_OAUTH2_KEY as CLIENT_ID, SOCIAL_AUTH_VK_OAUTH2_SECRET as CLIENT_SECRET
from .forms import *
from .models import *
from .utils import get_statistic, save_files


class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        top_friends = get_statistic(request, end_date=datetime.date.today(),
                                    start_date=datetime.date.today().replace(day=1))
        if len(top_friends) > 3:
            top_friends = top_friends[:3]
        future_events = Event.objects.filter(user=request.user, date__gt=datetime.date.today()).reverse()
        today_events = Event.objects.filter(user=request.user, date__exact=datetime.date.today())
        return render(request, 'cosmos/home.html',
                      context={'stat_list': top_friends, 'future_events': future_events, 'today_events': today_events,
                               'short': True, 'today': datetime.date.today()})


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


class ImportFriendsView(LoginRequiredMixin, View):
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
            if not user.get('id') in chosen_friends:
                continue
            new_friend = Friend(name=f"{user.get('first_name')} {user.get('last_name')}", user=request.user)
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


class FriendsListView(LoginRequiredMixin, View):
    def get(self, request):
        f_list = Friend.objects.filter(user=request.user)
        redirect_uri = request.build_absolute_uri(reverse('get_code'))
        return render(
            request, 'cosmos/friends.html',
            context={'f_list': f_list, 'client_id': CLIENT_ID, 'redirect_uri': redirect_uri}
        )


class EventsListView(LoginRequiredMixin, View):
    def get(self, request):
        e_list = Event.objects.filter(user=request.user)
        return render(request, 'cosmos/events.html',
                      context={'e_list': e_list, 'short': True, 'today': datetime.date.today()})


class AddFriendsView(LoginRequiredMixin, View):
    def get(self, request):
        form = AddFriendForm()
        return render(request, 'cosmos/add_friends.html', context={'form': form})

    def post(self, request):
        bound_form = AddFriendForm(request.POST, request.FILES)
        if not bound_form.is_valid():
            return render(request, 'cosmos/add_friends.html', context={'form': bound_form})
        friend = bound_form.save(commit=False)
        friend.user = request.user
        if request.FILES:
            friend.photo = request.FILES['photo']
        friend.save()
        return redirect('friends')


class RegistrationView(View):
    def get(self, request):
        form = CustomRegister()
        return render(request, 'register.html', context={'form': form})

    def post(self, request):
        bound_form = CustomRegister(request.POST)
        if not bound_form.is_valid():
            return render(request, 'register.html', context={'form': bound_form})
        new_user = User.objects.create_user(
            username=request.POST['username'],
            password=request.POST['password'],
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'])
        new_user.set_password(request.POST['password'])
        new_user.save()
        login(request, new_user)
        return redirect('home')


class DeleteFriendView(LoginRequiredMixin, View):
    def get(self, request, friend_id):
        friend = Friend.objects.get(id=friend_id)
        if request.user != friend.user:
            return render(request, 'cosmos/access_error.html', context={'error': 'Данный друг не существует.'})
        friend.delete()
        return redirect('friends')


class DeleteEventView(LoginRequiredMixin, View):
    def get(self, request, event_id):
        event = Event.objects.get(id=event_id)
        if request.user != event.user:
            return render(request, 'cosmos/access_error.html', context={'error': 'Данное событие не существует.'})
        event.delete()
        return redirect('events')


class EditFriendView(LoginRequiredMixin, View):
    def get(self, request, friend_id):
        friend = Friend.objects.get(id=friend_id)
        if request.user != friend.user:
            return render(request, 'cosmos/access_error.html', context={'error': 'Данный друг не существует.'})
        bound_form = AddFriendForm(instance=friend)
        return render(request, 'cosmos/edit_friend.html', context={'form': bound_form, 'friend': friend})

    def post(self, request, friend_id):
        friend = Friend.objects.get(id=friend_id)
        bound_form = AddFriendForm(request.POST, request.FILES, instance=friend)
        if not bound_form.is_valid():
            return render(request, 'cosmos/add_friends.html', context={'form': bound_form, 'friend': friend})
        friend = bound_form.save(commit=False)
        if request.FILES:
            friend.photo = request.FILES['photo']
        friend.save()
        return redirect('some_friend', friend.id)


class CreateEventView(LoginRequiredMixin, View):
    def get(self, request):
        form = CreateEventForm(current_user=request.user)
        return render(request, 'cosmos/create_event.html', context={'form': form})

    def post(self, request):
        bound_form = CreateEventForm(request.POST, request.FILES)
        if not bound_form.is_valid():
            return render(request, 'cosmos/create_event.html', context={'form': bound_form})
        new_event = bound_form.save(commit=False)
        new_event.user = request.user
        new_event.save()
        for mem in request.POST.getlist('members'):
            new_event.members.add(mem)
        new_event.save()
        save_files(request, new_event)
        return redirect('some_event', new_event.id)


class EditEventView(LoginRequiredMixin, View):
    def get(self, request, event_id):
        event = Event.objects.get(id=event_id)
        if request.user != event.user:
            return render(request, 'cosmos/access_error.html', context={'error': 'Данное событие не существует.'})
        photos = Photo.objects.filter(event=event_id)
        videos = Video.objects.filter(event=event_id)
        bound_form = CreateEventForm(instance=event, current_user=request.user)
        bound_form.fields['images'].label = "Добавить новые фотографии"
        bound_form.fields['videos'].label = "Добавить новые видео"
        return render(request, 'cosmos/edit_event.html',
                      context={'form': bound_form, 'photos': photos, 'event': event, 'videos': videos})

    def post(self, request, event_id):
        event = Event.objects.get(id=event_id)
        bound_form = CreateEventForm(request.POST, request.FILES, instance=event, current_user=request.user)
        if not bound_form.is_valid():
            photos = Photo.objects.filter(event=event_id)
            videos = Video.objects.filter(event=event_id)
            return render(request, 'cosmos/edit_event.html',
                          context={'form': bound_form, 'event': event, 'photos': photos, 'videos': videos})
        new_event = bound_form.save(commit=False)
        new_event.save()
        new_event.members.clear()
        for mem in request.POST.getlist('members'):
            new_event.members.add(mem)
        new_event.save()
        pictures_on_delete = request.POST.get('delete_photos', None)
        if pictures_on_delete:
            pictures_on_delete = pictures_on_delete.split()
            for pic_id in pictures_on_delete:
                current_picture = Photo.objects.get(id=int(pic_id))
                current_picture.delete()
        videos_on_delete = request.POST.get('delete_videos', None)
        if videos_on_delete:
            videos_on_delete = videos_on_delete.split()
            for vid_id in videos_on_delete:
                current_video = Video.objects.get(id=int(vid_id))
                current_video.delete()
        save_files(request, new_event)
        return redirect('some_event', new_event.id)


class SomeEventView(LoginRequiredMixin, View):
    def get(self, request, event_id):
        event = Event.objects.get(id=event_id)
        if request.user != event.user:
            return render(request, 'cosmos/access_error.html', context={'error': 'Данное событие не существует.'})
        photos = Photo.objects.filter(event=event_id)
        videos = Video.objects.filter(event=event_id)
        return render(request, 'cosmos/some_event.html',
                      context={'photos': photos, 'event': event, 'videos': videos, 'today': datetime.date.today()})


class SomeFriendView(LoginRequiredMixin, View):
    def get(self, request, friend_id):
        friend = Friend.objects.get(id=friend_id)
        if request.user != friend.user:
            return render(request, 'cosmos/access_error.html', context={'error': 'Данный друг не существует.'})
        e_list = Event.objects.filter(user=request.user, members__id__iexact=friend_id)
        return render(request, 'cosmos/some_friend.html', context={'friend': friend, 'e_list': e_list})


class StatisticView(LoginRequiredMixin, View):
    def get(self, request):
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=30)
        stat_list = get_statistic(request, start_date, end_date)
        return render(request, 'cosmos/stats.html', context={'stat_list': stat_list, 'period': 30})

    def post(self, request):
        """
        Возвращает рендер страницы с статистикой количества событий за период
        :param request: объект запроса
        Также неявно передаваемый параметр period. 0 - все время, 1 - произвольный, передается в POST,
        остальные значения - количество последних дней.
        :return: render страницы с контекстом
        """
        period = int(request.POST.get('btnradio', None))
        start_date, end_date, error = '', '', ''
        if period == 0:
            stat_list = get_statistic(request, all_the_time=True)
        else:
            if period == -1:
                start_date = request.POST.get('date_begin', None)
                end_date = request.POST.get('date_end', None)
            else:
                end_date = datetime.date.today()
                start_date = end_date - datetime.timedelta(days=period)
            stat_list = get_statistic(request, start_date, end_date)
            if stat_list == -1:
                error = "Введите корректную дату!"
                stat_list = []

        return render(request, 'cosmos/stats.html',
                      context={'stat_list': stat_list, 'period': period, 'error': error, 'start_date': start_date,
                               'end_date': end_date})


class CreateLinkView(LoginRequiredMixin, View):
    def get(self, request, event_id):
        event = Event.objects.get(id=event_id)
        if request.user != event.user:
            return render(request, 'cosmos/access_error.html', context={'error': 'Данное событие не существует.'})
        try:
            link_object = ShareLink.objects.get(event=event)
            link_object.date_of_die = datetime.datetime.now() + datetime.timedelta(days=1)
            link_object.save()
            token = link_object.token
        except ShareLink.DoesNotExist:
            token = uuid.uuid4()
            ShareLink(
                token=token,
                event=event,
                date_of_die=datetime.datetime.now() + datetime.timedelta(days=1)
            ).save()
        sharelink = request.build_absolute_uri(reverse('home')) + f'sharelink/{token}/'
        photos = Photo.objects.filter(event=event_id)
        videos = Video.objects.filter(event=event_id)
        return render(request, 'cosmos/some_event.html',
                      context={'photos': photos, 'event': event, 'videos': videos, 'sharelink': sharelink})


class ImportEventView(LoginRequiredMixin, View):
    def get(self, request, token):
        try:
            link_object = ShareLink.objects.get(token=token)
        except ShareLink.DoesNotExist:
            return render(request, 'cosmos/access_error.html', context={'error': 'Данное событие не существует.'})
        event = link_object.event
        new_event = Event(title=event.title, user=request.user, date=event.date, report=event.report)
        photos = Photo.objects.filter(event=event.id)
        videos = Video.objects.filter(event=event.id)
        bound_form = CreateEventForm(instance=new_event, current_user=request.user)
        return render(request, 'cosmos/import_event.html',
                      context={'form': bound_form, 'photos': photos, 'event': new_event, 'videos': videos,
                               'token': token})

    def post(self, request, token):
        bound_form = CreateEventForm(request.POST, request.FILES)
        try:
            link_object = ShareLink.objects.get(token=token)
        except ShareLink.DoesNotExist:
            return render(request, 'cosmos/access_error.html', context={'error': 'Данное событие не существует.'})
        orig_event = link_object.event
        photos = Photo.objects.filter(event=orig_event.id)
        videos = Video.objects.filter(event=orig_event.id)
        if not bound_form.is_valid():
            return render(request, 'cosmos/import_event.html',
                          context={'form': bound_form, 'photos': photos, 'event': bound_form, 'videos': videos,
                                   'token': token})
        new_event = bound_form.save(commit=False)
        new_event.user = request.user
        new_event.save()
        new_event.members.clear()
        for mem in request.POST.getlist('members'):
            new_event.members.add(mem)
        new_event.save()
        pictures_on_delete = request.POST.get('delete_photos', None)
        if pictures_on_delete:
            pictures_on_delete = [int(i) for i in pictures_on_delete.split()]
        for pic in photos:
            if pic.id not in pictures_on_delete:
                Photo(event=new_event, image=pic.image).save()
        videos_on_delete = request.POST.get('delete_videos', None)
        if videos_on_delete:
            videos_on_delete = [int(i) for i in videos_on_delete.split()]
        for vid in videos:
            if vid.id not in videos_on_delete:
                Video(event=new_event, video=vid.video, title=vid.title).save()
        save_files(request, new_event)
        return redirect('some_event', new_event.id)
