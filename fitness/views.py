from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from .forms import TrainingPlanForm, CommentForm, UserProfileForm, PlanGenerationForm
from .models import UserProfile, TrainingPlan, Comment, FollowRequest
from .tasks import generate_training_plan_task

# Create your views here.


# Public profile view
def profile_list(request):
    """Displays a list of user profiles."""
    profiles_queryset = UserProfile.objects.all()
    profiles = profiles_queryset.order_by('display_name')
    context = {
        'profiles': profiles,
    }
    return render(request, 'profiles/profile_list.html', context)


# Detailed profile view after logon
@login_required
def profile_detail(request, username):
    """Displays detailed profile information."""
    profile = get_object_or_404(UserProfile, user__username=username)
    plans = profile.plans.all().order_by('-start_date')
    comments = profile.comments_received.filter(approved=True, parent__isnull=True).order_by('-created_at')
    comment_form = CommentForm()

    # Check if this is the user's own profile
    is_owner = request.user == profile.user

    # Follow requests section
    is_owner = request.user == profile.user
    pending_follow_requests = []
    if is_owner:
        pending_follow_requests = FollowRequest.objects.filter(
            to_user=profile,
            accepted=False
        ).select_related('from_user') 

    # Check if current user is already following this profile
    is_following = False
    if request.user.is_authenticated and not is_owner:
        is_following = request.user.userprofile in profile.approved_followers.all()


    context = {
        'profile': profile,
        'previous_plans': plans,
        'comments': comments,
        'comment_form': comment_form,
        'is_owner': is_owner,
        'is_following': is_following,
        'pending_follow_requests': pending_follow_requests,
    }
    return render(request, 'profiles/profile_detail.html', context)


@login_required
def edit_profile(request):
    """Allows the logged-in user to edit their profile."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile_detail', username=profile.user.username)
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'profiles/edit_profile.html', {'form': form})


@login_required
def create_training_plan(request):
    """Allows the user to create a new training plan."""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    last_plan = TrainingPlan.objects.filter(user=user_profile).order_by('-start_date').first()
    
    if request.method == 'POST':
        form = PlanGenerationForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.user = request.user.userprofile
            plan.plan_json = {}  # Initialize empty JSON - will be filled by Celery task
            
            # Link to previous plan if it exists
            if last_plan:
                plan.previous_plan = last_plan
            
            plan.save()
            
            # Trigger async celery task
            generate_training_plan_task.delay(plan.pk)
            messages.success(request, "Training plan request submitted! AI generation is in progress.")
            return redirect('plan_detail', pk=plan.pk)
    else:
        form = PlanGenerationForm()

    context = {
        'form': form,
        'last_plan': last_plan
    }

    return render(request, 'plans/create_plan.html', context)


@login_required
def previous_plans(request):
    """Displays a list of the user's previously generated training plans"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    plans = TrainingPlan.objects.filter(user=request.user.userprofile).order_by('-target_date')
    context = {'plans': plans}
    return render(request, 'plans/previous_plans.html', context)


@login_required
def plan_detail(request, pk):
    """Displays the detailed view of a training plan"""
    plan = get_object_or_404(TrainingPlan, pk=pk, user__user=request.user)  # Only user can see their plan
    context = {'plan': plan}
    return render(request, 'plans/plan_detail.html', context)


@login_required
def add_comment(request, profile_id, parent_id=None):
    """Allows a user to add a comment or a reply to another user's profile."""
    profile = get_object_or_404(UserProfile, pk=profile_id)
    parent = get_object_or_404(Comment, pk=parent_id) if parent_id else None
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user.userprofile
            comment.profile = profile
            comment.parent = parent
            comment.save()
            messages.success(request, "Comment added!")
        else:
            messages.error(request, "Error adding comment. Please try again.")

    return redirect('profile_detail', username=profile.user.username)


@login_required
def edit_comment(request, comment_id):
    """Allows a user to edit their own comment."""
    comment = get_object_or_404(Comment, id=comment_id)
    # only the author can edit
    if comment.author.user != request.user:
        messages.error(request, "You do not have permission to edit this comment.")
        return redirect('profile_detail', username=comment.profile.user.username)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Comment updated!")
            return redirect('profile_detail', username=comment.profile.user.username)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'profiles/edit_comment.html', {'form': form, 'comment': comment})


@login_required
def delete_comment(request, comment_id):
    """Allows a user to delete their own comment."""
    comment = get_object_or_404(Comment, id=comment_id)
    # only the author can delete
    if comment.author.user != request.user:
        messages.error(request, "You do not have permission to delete this comment.")
        return redirect('profile_detail', username=comment.profile.user.username)
    
    profile_username = comment.profile.user.username
    comment.delete()
    messages.success(request, "Comment deleted.")
    return redirect('profile_detail', username=profile_username)


@login_required
def approve_comment(request, comment_id):
    """Allows a profile owner to approve a comment."""
    comment = get_object_or_404(Comment, id=comment_id)
    # only the profile owner can approve
    if comment.profile.user != request.user:
        messages.error(request, "You do not have permission to approve this comment.")
        return redirect('profile_detail', username=comment.profile.user.username)
    comment.approved = True
    comment.save()
    messages.success(request, "Comment approved.")
    return redirect('profile_detail', username=comment.profile.user.username)


@login_required
def send_follow_request(request, profile_pk): 
    """Sends a follow request to another user."""
    if request.method == "POST":
        from_user_profile = request.user.userprofile
        to_user_profile = get_object_or_404(UserProfile, pk=profile_pk) 
        if to_user_profile == from_user_profile:
            messages.error(request, "You cannot follow yourself.")
            return redirect('profile_detail', username=to_user_profile.user.username)
        follow_request, created = FollowRequest.objects.get_or_create(
            from_user=from_user_profile,
            to_user=to_user_profile
        )
        if created:
            messages.success(request, f"Follow request sent to {to_user_profile.display_name or to_user_profile.user.username}!")
        else:
            messages.info(request, f"You already sent a follow request to {to_user_profile.display_name or to_user_profile.user.username}.")
    
        return redirect('profile_detail', username=to_user_profile.user.username)
    return redirect('profile_list')


@login_required
def approve_follow_request(request, request_id):
    """Approves a follow request."""
    follow_request = get_object_or_404(FollowRequest, id=request_id)
    
    # Security check: Ensure only the recipient can approve the request
    if follow_request.to_user.user != request.user:
        messages.error(request, "You do not have permission to approve this request.")
        return redirect('profile_detail', username=request.user.username)
        
    follow_request.accepted = True
    follow_request.save()
    messages.success(request, f"Follow request from {follow_request.from_user.display_name} approved!")
  
    return redirect('profile_detail', username=follow_request.to_user.user.username) 


def signup(request):               
    """Handles user signup."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save user
            profile = user.userprofile
            profile.display_name = user.username
            profile.bio = "This user hasn't added a bio yet."
            profile.save()

            login(request, user)  # Log them in
            messages.success(request, "Signup successful!")
            return redirect('profile_detail', username=user.username)  # Redirect to their profile
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


def home(request):
    """Home page view with some profiles and example plans."""
    profiles = UserProfile.objects.all()[:5]  # 5 profiles
    example_plans = TrainingPlan.objects.all()[:3]  # 3 example plans
    context = {
        'profiles': profiles,
        'example_plans': example_plans,
    }
    return render(request, 'home.html', context)


# Search Views
def search_profiles_by_username(request):
    """Searches profiles by username."""
    query = request.GET.get('q')
    profiles = UserProfile.objects.none()
    if query:
        # Searches the User model's username field (case-insensitive)
        profiles = UserProfile.objects.filter(user__username__icontains=query, user__is_active=True).order_by('user__username')
        messages.info(request, f"Found {profiles.count()} profiles matching '{query}'.")
    return render(request, 'profiles/profile_search_results.html', {'profiles': profiles, 'query': query, 'search_type': 'Username'})

def search_profiles_by_goal_event(request):
    """Searches profiles by their goal event."""
    query = request.GET.get('q')
    profiles = UserProfile.objects.none()
    if query:
        # Searches the UserProfile model's goal_event field (case-insensitive)
        profiles = UserProfile.objects.filter(goal_event__icontains=query, user__is_active=True).order_by('user__username')
        messages.info(request, f"Found {profiles.count()} profiles matching '{query}'.")
    return render(request, 'profiles/profile_search_results.html', {'profiles': profiles, 'query': query, 'search_type': 'Goal/Event'})