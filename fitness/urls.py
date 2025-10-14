from django.urls import path
from . import views

urlpatterns = [
    path('profiles/', views.profile_list, name='profile_list'),
    path('profiles/<str:username>/', views.profile_detail, name='profile_detail'),
    path('profiles/edit/', views.edit_profile, name='edit_profile'),
    path('profiles/<int:profile_pk>/comment/', views.add_comment, name='add_comment'),
    path('comments/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comments/<int:comment_id>/approve/', views.approve_comment, name='approve_comment'),
]