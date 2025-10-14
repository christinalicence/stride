from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path('profiles/', views.profile_list, name='profile_list'),
    path('profiles/<str:username>/', views.profile_detail, name='profile_detail'),
    path('profiles/edit/', views.edit_profile, name='edit_profile'),
    path('profiles/<int:profile_pk>/comment/', views.add_comment, name='add_comment'),
    path('comments/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comments/<int:comment_id>/approve/', views.approve_comment, name='approve_comment'),
    path('signup/', views.signup, name='signup'),
    path('accounts/profile/', lambda request: redirect('profile_detail', username=request.user.username)
    ),
]
