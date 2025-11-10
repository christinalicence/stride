from django.urls import path
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from . import views
from . import forms

urlpatterns = [
    # Signup
    path('signup/', views.signup, name='signup'),

    # Account auth
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/profile/', lambda request: redirect('profile_detail', username=request.user.username)),

    # Profiles
    path('profiles/', views.profile_list, name='profile_list'),  # list of all profiles
    path('profiles/edit/', views.edit_profile, name='edit_profile'),  # edit current user
    path('profiles/<str:username>/', views.profile_detail, name='profile_detail'),  # profile detail (catch-all)

    # Comments CRUD
    path('comments/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comments/<int:comment_id>/approve/', views.approve_comment, name='approve_comment'),
    path('profiles/<int:profile_id>/comment/', views.add_comment, name='add_comment'),  
    path('profiles/<int:profile_id>/comment/<int:parent_id>/', views.add_comment, name='reply_comment'), 

    # Following
    path('follow/<int:profile_pk>/', views.send_follow_request, name='send_follow_request'),
    path('approve_follow/<int:request_id>/', views.approve_follow_request, name='approve_follow_request'),

    # Training Plans
    path('plans/create/', views.create_training_plan, name='create_training_plan'),
    path('plans/', views.previous_plans, name='previous_plans'),
    path('plans/<int:pk>/', views.plan_detail, name='plan_detail'),
    path('plans/<int:pk>/retry/', views.delete_plan_and_retry, name='delete_plan_and_retry'),

    # Home page
    path('', views.home, name='home'),

    # Search
    path('search/username/', views.search_profiles_by_username, name='search_profiles_by_username'),
    path('search/goal/', views.search_profiles_by_goal_event, name='search_profiles_by_goal_event'),
]






