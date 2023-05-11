from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import (
    UserEditView, 
    PasswordsChangeView, 
    EditProfileView, 
    CreateProfileView, 
    invites_received_view,  
    send_invatation,
    remove_from_friends,
    accept_invatation,
    reject_invatation,
    ProfileDetailView,
    post_comment_create_and_list_view,
    like_unlike_post,
    PostDeleteView,
    PostUpdateView,
    post_comment_create_and_list_view_in_profile,
    ToInviteProfileListView,
    friend_profile_list_view
)

urlpatterns = [
    path('home/', post_comment_create_and_list_view, name='home'),
    path('register/', views.register, name='register'),
    path('', auth_views.LoginView.as_view(template_name="login.html"), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page="/"), name='logout'),
    path('profile/', post_comment_create_and_list_view_in_profile,name="profile"),
    path('edit_information/', UserEditView.as_view(), name='edit_information'),
    path('password/', PasswordsChangeView.as_view(template_name='change_password.html'), name='change_password'),
    path('<int:pk>/edit_profile/', EditProfileView.as_view(), name='edit_profile'),
    path('create_profile', CreateProfileView.as_view(), name='create_profile'),
    path('my-invites/', invites_received_view, name='my_invites'),
    path('friends-profiles/', friend_profile_list_view, name='friends_profiles_views'),
    path('to-invite/', ToInviteProfileListView.as_view(), name='invite_profiles_views'),
    path('send-invite/', send_invatation, name='send_invite'),
    path('remove-friend/', remove_from_friends, name='remove_friend'),
    path('my-invites/accept', accept_invatation, name='accept_invite'),
    path('my-invites/reject', reject_invatation, name='reject_invite'),
    path('<slug>/', ProfileDetailView.as_view(), name='profile_detail_view'),
    path('home/liked/', like_unlike_post, name='like_post_view'),
    path('<pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('<pk>/update/', PostUpdateView.as_view(), name='post_update'),
]
