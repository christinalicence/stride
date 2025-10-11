from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, TrainingPlan, Comment

# Create your views here.


# Public profile view
def profile_list(request):
    """Displays a list of user profiles, most followed first."""
    profiles = UserProfile.objects.all().order_by('-followers')
    return render(request, 'profiles/profile_list.html', {'profiles': profiles})


# Detailed orofile view after logon
@login_required
def profile_detail(request, pk):
    """Displays detailed profile information."""
    profile = get_object_or_404(UserProfile, pk=pk)
    plans = profile.plans.all().order_by('-start_date')
    comments = profile.comments_received.all().order_by('-created_at')
    comment_form = CommentForm()

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
            return redirect('profile_detail', pk=profile.pk)
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
    target_profile = get_object_or_404(UserProfile, pk=profile_pk) # the profile being commented on
    author_profile = get_object_or_404(UserProfile, user=request.user) # the profile of the commenter
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = author_profile
            comment.profile = target_profile
            comment.save()
            messages.success(request, "Comment added!")
            return redirect('profile_detail', pk=target_profile.pk)

    # If not a POST request (or if POST fails), redirect back to the profile detail page
    messages.error(request, "Could not submit comment.")
    return redirect("profile_detail", pk=profile_pk)