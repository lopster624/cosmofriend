from django.contrib import admin
from django.urls import path
from django.urls import include
from .views import *

urlpatterns = [
    path('', Home.as_view(), name="home"),
    path('logout/', logout, name='logout'),
    path('import_friends/', ImportFriends.as_view(), name='import_friends'),
    path('get_code/', get_code, name='get_code'),
    path('register/', Registration.as_view(), name='register'),
    path('friends/add/', AddFriends.as_view(), name='add_friends'),
    path('friends/', FriendsList.as_view(), name='friends'),
    path('friends/<int:friend_id>', SomeFriend.as_view(), name='some_friend'),
    path('friends/delete/<int:friend_id>/', DeleteFriend.as_view(), name='delete_friend'),
    path('friends/edit/<int:friend_id>/', EditFriend.as_view(), name='edit_friend'),
    path('events/', EventsList.as_view(), name='events'),
    path('events/<int:event_id>', SomeEvent.as_view(), name='some_event'),
    path('events/create/', CreateEvent.as_view(), name='create_event'),
    path('events/delete/<int:event_id>/', DeleteEvent.as_view(), name='delete_event'),
    path('events/edit/<int:event_id>/', EditEvent.as_view(), name='edit_event'),
]
