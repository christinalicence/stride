from django.urls import path
from . import views

urlpatterns = [
    path('profiles/', views.profile_list, name='profile_list'),
    path('profiles/<str:username>/', views.profile_detail, name='profile_detail'),
    path('profiles/edit/', views.edit_profile, name='edit_profile'),
    path('profiles/<str:username>/comment/', views.add_comment, name='add_comment'),
]