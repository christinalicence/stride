from django.urls import path
from . import views

urlpatterns = [
    path('profiles/', views.profile_list, name='profile_list'),
    path('profiles/<int:pk>/', views.profile_detail, name='profile_detail'),
    path('profiles/edit/', views.edit_profile, name='edit_profile'),
]