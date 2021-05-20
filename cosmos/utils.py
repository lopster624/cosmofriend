import datetime
import re
from operator import itemgetter

from cosmos.models import Event, Friend, Photo, Video


def get_statistic(request, start_date=None, end_date=None, all_the_time=None):
    if not all_the_time:
        if type(start_date) is str or type(end_date) is str:
            try:
                start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                return -1
        events = Event.objects.filter(user=request.user, date__gte=start_date, date__lte=end_date)
    else:
        events = Event.objects.filter(user=request.user)
    stat_list = []
    f_list = Friend.objects.filter(user=request.user)
    for friend in f_list:
        events_with_friend = events.filter(members__id__iexact=friend.id)
        if len(events_with_friend) > 0:
            stat_list.append((friend, len(events_with_friend)))
    return sorted(stat_list, key=itemgetter(1), reverse=True)


def save_videos(request, new_event):
    if not request.FILES:
        return
    for f in request.FILES.getlist('images'):
        Photo(event=new_event, image=f).save()
    for f in request.FILES.getlist('videos'):
        file_format = re.findall(r"\.mp4$", f.name)
        if file_format:
            video = Video(event=new_event, video=f)
            video.save()
            video.title = video.video.name.split('/')[-1]
            video.save()