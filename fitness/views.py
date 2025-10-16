from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from .models import UserProfile, TrainingPlan, Comment, FollowRequest
from .forms import UserProfileForm, CommentForm, TrainingPlanForm
from django.shortcuts import render, redirect
from django.db.models import Count

# Create your views here.


# Public profile view
def profile_list(request):
    """Displays a list of user profiles."""
    profiles = UserProfile.objects.all().order_by('display_name')  # ordered alphabetically
    context = {
        'profiles': profiles,
    }
    return render(request, 'profiles/profile_list.html', {'profiles': profiles})


# Detailed orofile view after logon
@login_required
def profile_detail(request, username):
    """Displays detailed profile information."""
    profile = get_object_or_404(UserProfile, user__username=username)
    plans = profile.plans.all().order_by('-start_date')
    comments = profile.comments_received.filter(approved=True).order_by('-created_at')
    comment_form = CommentForm()

    # Only show follow button if logged in and not viewing your own profile
    can_follow = request.user.is_authenticated and request.user != profile.user
    follow_request_sent = FollowRequest.objects.filter(from_user=request.user.userprofile, to_user=profile).exists() if can_follow else False

    context = {
        'profile': profile,
        'plans': plans,
        'comments': comments,
        'comment_form': comment_form,
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
    if request.method == 'POST':
        form = TrainingPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.user = request.user.userprofile
            plan.save()
            messages.success(request, "Training plan request submitted! AI generation pending.")
            return redirect('plan_detail', pk=plan.pk)
    else:
        form = TrainingPlanForm()

    return render(request, 'plans/create_plan.html', {'form': form})


@login_required
def add_comment(request, profile_pk):
    """Allows a user to add a comment to another user's profile."""
    target_profile = get_object_or_404(UserProfile, pk=profile_pk)
    author_profile = get_object_or_404(UserProfile, user=request.user)  # the profile of the commenter
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = author_profile
            comment.profile = target_profile
            comment.save()
            messages.success(request, "Comment added!")
        else:
            messages.error(request, "Error adding comment. Please try again.")
    return redirect('profile_detail', username=target_profile.user.username)


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
def send_follow_request(request, username):
    """Sends a follow request to another user."""
    if request.method == "POST":
        from_user_profile = request.user.userprofile
        # Don't allow following yourself
        if from_user_profile.user.username == username:
            messages.error(request, "You cannot follow yourself.")
            return redirect('profile_detail', username=username)
        to_user_profile = get_object_or_404(UserProfile, user__username=username)
        # Create follow request if it doesn't exist
        follow_request, created = FollowRequest.objects.get_or_create(
            from_user=from_user_profile,
            to_user=to_user_profile
        )
        if created:
            messages.success(request, f"Follow request sent to {to_user_profile.display_name or username}!")
        else:
            messages.info(request, f"You already sent a follow request to {to_user_profile.display_name or username}.")
        return redirect('profile_detail', username=username)
    return redirect('profile_list')


@login_required
def approve_follow_request(request, request_id):
    """Approves a follow request."""
    follow_request = get_object_or_404(FollowRequest, id=request_id)
    follow_request.accepted = True
    follow_request.save()
    return redirect('profile_detail', username=follow_request.user.username)


def signup(request):               
    """Handles user signup."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save() #Save user
            profile = user.userprofile
            profile.display_name = user.username
            profile.bio = "This user hasn't added a bio yet."
            profile.save()

            login(request, user) #Log them in
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
