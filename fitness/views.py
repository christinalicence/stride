from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, TrainingPlan, Comment
from .forms import UserProfileForm, CommentForm, TrainingPlanForm
from django.shortcuts import render, redirect

# Create your views here.


# Public profile view
def profile_list(request):
    """Displays a list of user profiles, most followed first."""
    profiles = UserProfile.objects.all().order_by('-followers')
    return render(request, 'profiles/profile_list.html', {'profiles': profiles})


# Detailed orofile view after logon
@login_required
def profile_detail(request, username):
    """Displays detailed profile information."""
    profile = get_object_or_404(UserProfile, user__username=username) # fetch by username
    plans = profile.plans.all().order_by('-start_date')
    comments = profile.comments_received.filter(approved=True).order_by('-created_at')
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
    Comment = get_object_or_404(Comment, id=comment_id)
    # only the profile owner can approve
    if comment.profile.user != request.user:
        messages.error(request, "You do not have permission to approve this comment.")
        return redirect('profile_detail', username=comment.profile.user.username)
    comment.approved = True
    comment.save()
    messages.success(request, "Comment approved.")
    return redirect('profile_detail', username=comment.profile.user.username)


def signup(request):
    """Handles user signup."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save() #Save user
            UserProfile.objects.create( # Create associated profile, add some holding text
                user=user,
                display_name=user.username,
                bio="This user hasn't added a bio yet."
            )
            return redirect('login')  # Redirect to login page after signup
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})