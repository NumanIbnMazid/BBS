from django.views.generic import TemplateView
from users.models import Husband
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from posts.models import Post, Comment, CommentReply
from django.contrib import messages
from django.urls import reverse
from .forms import HusbandManageForm, PostManageForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View


# #-----------------------------***-----------------------------
# #---------------------------- Home ---------------------------
# #-----------------------------***-----------------------------


class HomeView(TemplateView):
    template_name = "user-panel/index.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context["page_title"] = "Home"
        return context
# #-----------------------------***-----------------------------
# #------------------------ User Profile -----------------------
# #-----------------------------***-----------------------------

@login_required()
def user_profile(request):
    page_title = request.user.username
    husband_lists = Husband.objects.filter(user  = request.user)
    post_lists = Post.objects.all()
    context = {'husband_lists':husband_lists,
               'post_lists':post_lists,'page_title':page_title}
    return render(request,'user-panel/profile.html', context)


# #-----------------------------***-----------------------------
# #------------------------ Husband Create ---------------------
# #-----------------------------***-----------------------------
@login_required()
def create_husband(request):
    # template_name = "user-panel/husband.html"
    form = HusbandManageForm

    if request.method == 'POST':
        if request.user.is_authenticated:
            user = request.user
            name = request.POST.get('name')
            nationality = request.POST.get('nationality')
            address = request.POST.get('address')
            dob = request.POST.get('dob')
            characteristics = request.POST.get('characteristics')
            husband_qs = Husband.objects.filter(name__iexact = name).last()
            if not husband_qs:
                husband_qs = Husband.objects.create(user = user, name = name,
                                                    nationality = nationality,address = address,
                                                    dob=dob,characteristics=characteristics)
                if husband_qs:
                    return HttpResponseRedirect(reverse('user_profile'))
    context ={'form':form}
    return render(request, 'user-panel/form.html', context)


# #-----------------------------***-----------------------------
# #------------------------ Husband Details --------------------
# #-----------------------------***-----------------------------

@login_required()
def husband_details(request, slug):
    husband_qs = Husband.objects.filter(slug=slug).last()
    form = HusbandManageForm(instance=husband_qs)
    is_details = True
    context = {'form': form,'is_details':is_details}
    return render(request, 'user-panel/form.html', context)

# #-----------------------------***-----------------------------
# #------------------------ Husband Update ---------------------
# #-----------------------------***-----------------------------

@login_required()
def husband_update(request, slug):
    husband_qs = Husband.objects.filter(slug=slug).last()
    form = HusbandManageForm(instance=husband_qs)
    url = request.path
    if request.method == 'POST':
        form = HusbandManageForm(request.POST,instance=husband_qs)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('user_profile'))
    context = {'form': form}
    return render(request, 'user-panel/form.html', context)

# #-----------------------------***-----------------------------
# #------------------------ Create Post ------------------------
# #-----------------------------***-----------------------------

@login_required()
def create_post(request):
    # template_name = "user-panel/husband.html"
    form = PostManageForm

    if request.method == 'POST':
        if request.user.is_authenticated:
            user = request.user
            title = request.POST.get('title')
            thread = request.POST.get('thread')
            weight = request.POST.get('weight')
            description = request.POST.get('description')
            post_qs = Post.objects.create(user = user, title = title, thread_id = thread,
                               weight = weight, description=description)
            if post_qs:
                return HttpResponseRedirect(reverse('user_profile'))
    context ={'form':form}
    return render(request, 'user-panel/form.html', context)

# #-----------------------------***-----------------------------
# #------------------------ Post Details ------------------------
# #-----------------------------***-----------------------------

@login_required()
def post_details(request, slug):
    post_qs = Post.objects.filter(slug=slug).last()
    page_title = post_qs.title
    form = PostManageForm(instance=post_qs)
    context = {'form': form,'post_qs':post_qs,'page_title':page_title}

    if request.method == 'POST':
        if request.user.is_authenticated:
            comment = request.POST.get("comment")
            Comment.objects.create(
                post=post_qs,
                commented_by=request.user,
                comment=comment
            )
            return HttpResponseRedirect(reverse("post_details", kwargs={"slug": slug}))
        else:
            return HttpResponseRedirect(reverse("account_login"))


    return render(request, 'user-panel/post-details.html', context)

# #-----------------------------***-----------------------------
# #------------------------ Post Update ------------------------
# #-----------------------------***-----------------------------

@login_required()
def post_update(request, slug):
    post_qs = Post.objects.filter(slug=slug).last()
    form = PostManageForm(instance=post_qs)
    if request.method == 'POST':
        form = PostManageForm(request.POST,instance=post_qs)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('user_profile'))
    context = {'form': form}
    return render(request, 'user-panel/form.html', context)

# #-----------------------------***-----------------------------
# #------------------------ Post Delete ------------------------
# #-----------------------------***-----------------------------

@login_required()
def post_delete(request, slug):
    post_qs = Post.objects.filter(slug=slug).last()
    form = PostManageForm(instance=post_qs)
    if post_qs:
        post_qs.delete()
        return HttpResponseRedirect(reverse('user_profile'))
    context = {'form': form}
    return render(request, 'user-panel/form.html', context)