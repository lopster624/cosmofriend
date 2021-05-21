from django.urls import path
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('logout/', logout, name='logout'),
    path('import_friends/', ImportFriendsView.as_view(), name='import_friends'),
    path('get_code/', get_code, name='get_code'),
    path('register/', RegistrationView.as_view(), name='register'),
    path('friends/add/', AddFriendsView.as_view(), name='add_friends'),
    path('friends/', FriendsListView.as_view(), name='friends'),
    path('friends/<int:friend_id>/', SomeFriendView.as_view(), name='some_friend'),
    path('friends/delete/<int:friend_id>/', DeleteFriendView.as_view(), name='delete_friend'),
    path('friends/edit/<int:friend_id>/', EditFriendView.as_view(), name='edit_friend'),
    path('events/', EventsListView.as_view(), name='events'),
    path('events/<int:event_id>/', SomeEventView.as_view(), name='some_event'),
    path('events/share/<int:event_id>/', CreateLinkView.as_view(), name='share_event'),
    path('events/create/', CreateEventView.as_view(), name='create_event'),
    path('events/delete/<int:event_id>/', DeleteEventView.as_view(), name='delete_event'),
    path('events/edit/<int:event_id>/', EditEventView.as_view(), name='edit_event'),
    path('statistic/', StatisticView.as_view(), name='statistic'),
    path('sharelink/<str:token>/', ImportEventView.as_view(), name='import_event'),

]
