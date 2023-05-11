from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from .forms import RegistrationForm, EditInformationForm, PasswordChangingForm, CreateProfileForm
from Home.models import Profile, Relationship
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.db.models import Q
from Post.models import Post, Like
from Post.forms import PostModelForm, CommentModelForm
from django.contrib import messages


def error(request, exception=None):
    return render(request, 'error.html')

def register(request):
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()    
            return HttpResponseRedirect('/')
    return render(request, 'register.html', {'form': form})

def messages(request):
    return render(request, 'messages.html') 

class UserEditView(generic.UpdateView):
    form_class = EditInformationForm
    template_name = 'edit_information.html'
    success_url = reverse_lazy('profile')

    def get_object(self): 
        return self.request.user

class PasswordsChangeView(PasswordChangeView):
    form_class = PasswordChangingForm
    success_url = reverse_lazy('change_password')

class EditProfileView(generic.UpdateView):
    model = Profile
    template_name = 'edit_profile.html'
    fields = ['bio', 'ava_pic', 'background_pic']
    success_url = reverse_lazy('profile')
    
class CreateProfileView(CreateView):
    model = Profile
    form_class = CreateProfileForm
    template_name = "create_profile.html"
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

def invites_received_view(request):
    profile = Profile.objects.get(user=request.user)
    qs = Relationship.objects.invatations_received(profile)
    results = list(map(lambda x: x.sender, qs))
    is_empty = False

    user = request.user
    rel_qs = Profile.objects.get_all_profiles_to_invite(user)
    rel_r = Relationship.objects.filter(sender=profile)
    rel_s = Relationship.objects.filter(receiver=profile)
    rel_receiver = []
    rel_sender = []

    for item in rel_r:
        rel_receiver.append(item.receiver.user)
    
    for item in rel_s:
        rel_sender.append(item.sender.user)

    if len(results) == 0:
        is_empty = True

    context = {
        'rel_qs': rel_qs,
        'rel_receiver': rel_receiver,
        'rel_sender': rel_sender,
        'qs': results,
        'is_empty': is_empty,
        }

    return render(request, 'my_invites.html', context)

def accept_invatation(request):
    if request.method=="POST":
        pk = request.POST.get('profile_pk')
        sender = Profile.objects.get(pk=pk)
        receiver = Profile.objects.get(user=request.user)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        
        if rel.status == 'send':
            rel.status = 'accepted'
            rel.save()

    return redirect('my_invites')

def reject_invatation(request):
    if request.method=="POST":
        pk = request.POST.get('profile_pk')
        sender = Profile.objects.get(pk=pk)
        receiver = Profile.objects.get(user=request.user)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        
        rel.delete()

    return redirect('my_invites')

class ProfileDetailView(DetailView):
    model = Profile
    template_name = 'detail_profile.html'

    def get_object(self, slug=None):
        slug = self.kwargs.get('slug')
        profile = Profile.objects.get(slug=slug)
        return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username__iexact=self.request.user)
        profile = Profile.objects.get(user=user)

        rel_r = Relationship.objects.filter(sender=profile)
        rel_s = Relationship.objects.filter(receiver=profile)
        rel_receiver = []
        rel_sender = []

        for item in rel_r:
            rel_receiver.append(item.receiver.user)
        
        for item in rel_s:
            rel_sender.append(item.sender.user)

        context["rel_receiver"] = rel_receiver
        context["rel_sender"] = rel_sender
        context['posts'] = self.get_object().get_all_authors_posts()
        context['len_posts'] = True if len(self.get_object().get_all_authors_posts()) > 0 else False

        return context

class ToInviteProfileListView(ListView):
    model = Profile
    template_name = 'to_invite_list.html'

    def get_queryset(self):
        qs = Profile.objects.get_all_profiles_to_invite(self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username__iexact=self.request.user)
        profile = Profile.objects.get(user=user)

        rel_r = Relationship.objects.filter(sender=profile)
        rel_s = Relationship.objects.filter(receiver=profile)
        rel_receiver = []
        rel_sender = []

        for item in rel_r:
            rel_receiver.append(item.receiver.user)
        
        for item in rel_s:
            rel_sender.append(item.sender.user)

        context["rel_receiver"] = rel_receiver
        context["rel_sender"] = rel_sender
        context["is_empty"] = False

        if len(self.get_queryset()) == 0:
            context["is_empty"] = True

        return context

def invite_profiles_list_view(request):
    user = request.user
    qs = Profile.objects.get_all_profiles_to_invite(user)

    context = {'qs': qs}

    return render(request, 'base.html', context)

def send_invatation(request):
    if request.method=='POST':
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)

        rel = Relationship.objects.create(sender=sender, receiver=receiver, status='send')

        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profile')

def remove_from_friends(request):
    if request.method=='POST':
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)

        rel = Relationship.objects.get(
            (Q(sender=sender) & Q(receiver=receiver)) | 
            (Q(sender=receiver) & Q(receiver=sender))
            )

        rel.delete()
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profile')

def post_comment_create_and_list_view(request):
    qs = Post.objects.all()
    user = request.user

    friend_profile = Profile.objects.get_all_profiles_is_friend(user)
    profile = Profile.objects.get(user=user)


    rel_qs = Profile.objects.get_all_profiles_to_invite(user)
    rel_r = Relationship.objects.filter(sender=profile)
    rel_s = Relationship.objects.filter(receiver=profile)
    rel_receiver = []
    rel_sender = []

    for item in rel_r:
        rel_receiver.append(item.receiver.user)
    
    for item in rel_s:
        rel_sender.append(item.sender.user)

    #Post form, comment form
    post_form = PostModelForm()
    comment_form = CommentModelForm()
    post_added = False

    if 'submit_post_form' in request.POST:
        post_form = PostModelForm(request.POST, request.FILES)
        if post_form.is_valid():
            instance = post_form.save(commit=False)
            instance.author = profile
            instance.save()
            post_form = PostModelForm()
            post_added = True
            return HttpResponseRedirect('/home')
    
    if 'submit_comment_form' in request.POST:
        comment_form = CommentModelForm(request.POST)
        if comment_form.is_valid():
            instance = comment_form.save(commit=False)
            instance.user = profile
            instance.post = Post.objects.get(id=request.POST.get('post_id'))
            instance.save()
            comment_form = CommentModelForm()
            return HttpResponseRedirect('/home')

    context = {
        'rel_qs': rel_qs,
        'rel_receiver': rel_receiver,
        'rel_sender': rel_sender,
        'qs': qs,
        'profile': profile,
        'friend_profile': friend_profile,
        'post_form': post_form,
        'comment_form': comment_form,
        'post_added': post_added,
    }

    return render(request, 'home.html', context)

def like_unlike_post(request):
    user = request.user
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post_obj = Post.objects.get(id=post_id)
        profile = Profile.objects.get(user=user)

        if profile in post_obj.liked.all():
            post_obj.liked.remove(profile)
        else:
            post_obj.liked.add(profile)

        like, created = Like.objects.get_or_create(user=profile, post_id=post_id)

        if not created:
            if like.value=='Like':
                like.value='Unlike'
            else:
                like.value='Like'
        else:
            like.value='Like'

        post_obj.save()
        like.save()
    
    return redirect('home')

class PostDeleteView(DeleteView):
    model = Post
    template_name = 'confirm_del.html'
    success_url = reverse_lazy('home')

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        obj = Post.objects.get(pk=pk)
        if not obj.author.user == self.request.user:
            messages.warning(self.request, 'You need to be the author of the post in order to delete it!')

        return obj

class PostUpdateView(UpdateView):
    form_class = PostModelForm
    model = Post
    template_name = 'update.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        profile = Profile.objects.get(user=self.request.user)
        if form.instance.author == profile:
            return super().form_valid(form)
        else:
            form.add_error(None, "You need to be the author of the post in order to update it")
            return super().form_invalid(form)

def post_comment_create_and_list_view_in_profile(request):
    qs = Post.objects.all()
    profile = Profile.objects.get(user=request.user)

    user = request.user
    rel_qs = Profile.objects.get_all_profiles_to_invite(user)
    rel_r = Relationship.objects.filter(sender=profile)
    rel_s = Relationship.objects.filter(receiver=profile)
    rel_receiver = []
    rel_sender = []

    for item in rel_r:
        rel_receiver.append(item.receiver.user)
    
    for item in rel_s:
        rel_sender.append(item.sender.user)

    #Post form, comment form
    post_form = PostModelForm()
    comment_form = CommentModelForm()
    post_added = False

    if 'submit_post_form' in request.POST:
        post_form = PostModelForm(request.POST, request.FILES)
        if post_form.is_valid():
            instance = post_form.save(commit=False)
            instance.author = profile
            instance.save()
            post_form = PostModelForm()
            post_added = True
    
    if 'submit_comment_form' in request.POST:
        comment_form = CommentModelForm(request.POST)
        if comment_form.is_valid():
            instance = comment_form.save(commit=False)
            instance.user = profile
            instance.post = Post.objects.get(id=request.POST.get('post_id'))
            instance.save()
            comment_form = CommentModelForm()

    context = {
        'rel_qs': rel_qs,
        'rel_receiver': rel_receiver,
        'rel_sender': rel_sender,
        'qs': qs,
        'profile': profile,
        'post_form': post_form,
        'comment_form': comment_form,
        'post_added': post_added,
    }

    return render(request, 'profile.html', context)

def friend_profile_list_view(request):
    user = request.user
    profile = Profile.objects.get(user=request.user)


    qs = Profile.objects.get_all_profiles_is_friend(user)

    rel_r1 = Relationship.objects.filter(sender=profile)
    rel_s1 = Relationship.objects.filter(receiver=profile)
    rel_receiver1 = []
    rel_sender1 = []
    is_empty = False

    for item in rel_r1:
        rel_receiver1.append(item.receiver.user)
    
    for item in rel_s1:
        rel_sender1.append(item.sender.user)

    

    if len(qs) == 0:
        is_empty = True


##################################################

    rel_qs = Profile.objects.get_all_profiles_to_invite(user)
    
    rel_r = Relationship.objects.filter(sender=profile)
    rel_s = Relationship.objects.filter(receiver=profile)
    rel_receiver = []
    rel_sender = []

    for item in rel_r:
        rel_receiver.append(item.receiver.user)
    
    for item in rel_s:
        rel_sender.append(item.sender.user)

    #Post form, comment form

    context = {
        'rel_qs': rel_qs,
        'rel_receiver': rel_receiver,
        'rel_sender': rel_sender,
        'qs': qs,
        'rel_receiver1': rel_receiver1,
        'rel_sender1': rel_sender1,
        'is_empty': is_empty
    }

    return render(request, 'friend_profile_list.html', context)