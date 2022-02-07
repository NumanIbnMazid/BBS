from django.views.generic import TemplateView, ListView, View
# models import
from plans.models import UserWalletTransaction
from users.models import Husband, UserWallet, User
from faq.models import FAQ
from chat.models import Message

from django.http import HttpResponse, HttpResponseNotFound
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from posts.models import Post, Comment, CommentReply, Thread
from django.contrib import messages
from django.urls import reverse
from .forms import HusbandManageForm, PostManageForm, UserManageForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View
from datetime import date, datetime, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from django.db.models import Q
import os
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.db.models.fields.files import ImageFieldFile
from django.template.defaultfilters import filesizeformat

# helper functions


def check_is_valid_image(imageFile):
    image = imageFile
    if image and isinstance(image, UploadedFile):
        file_extension = os.path.splitext(image.name)[1]
        allowed_image_types = settings.ALLOWED_IMAGE_TYPES
        content_type = image.content_type.split('/')[0]
        if not file_extension in allowed_image_types:
            return False, "Only %s image file formats are supported! Current image file format is %s" % (
                allowed_image_types, file_extension)
        if image.size > settings.MAX_UPLOAD_SIZE:
            return False, "Please keep filesize under %s. Current filesize %s" % (
                filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(image.size))
    return True, "is_valid_image"


# #-----------------------------***-----------------------------
# #---------------------------- Home ---------------------------
# #-----------------------------***-----------------------------


class HomeView(TemplateView):
    template_name = "user-panel/pages/index.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        thread_list = Thread.objects.all()
        post_list = Post.objects.all().distinct()
        context["page_title"] = "Home"
        context['page_title'] = 'Thread lists'
        context['thread_list'] = thread_list
        context['post_list'] = post_list
        context['faq_list'] = FAQ.objects.filter(is_active=True)
        context['show_baner'] = True
        return context


class PackageView(TemplateView):
    template_name = "user-panel/pages/packages.html"

    def get_context_data(self, **kwargs):
        context = super(PackageView, self).get_context_data(**kwargs)
        context["page_title"] = "Packages"
        context['page_title'] = 'Packages'
        return context


class ThreadPostListView(ListView):
    template_name = "user-panel/pages/thread.html"

    def get_thread(self):
        qs = Thread.objects.filter(slug__iexact=self.kwargs['slug'])
        if qs.exists():
            return qs.first()
        return None

    def get_queryset(self):
        qs = Post.objects.all()
        if self.kwargs.get('slug'):
            qs = qs.filter(thread__slug__iexact=self.kwargs['slug'])
        return qs

    def get_context_data(self, **kwargs):
        context = super(ThreadPostListView, self).get_context_data(**kwargs)
        context["page_title"] = "Thread Posts"
        context['page_title'] = 'Thread Posts'
        context['active_thread'] = self.get_thread(
        ) if self.get_thread else None
        context['show_baner'] = False
        return context
    
def user_subscriptions(request):
    user = request.user
    wallet_transaction_qs = UserWalletTransaction.objects.filter(user=user)
    context = {
        "wallet_transactions": wallet_transaction_qs,
    }
    return render(request, 'user-panel/pages//subscriptions.html', context)
    
def user_posts(request):
    user = request.user
    post_qs = Post.objects.filter(user=user)
    context = {
        "posts": post_qs,
    }
    return render(request, 'user-panel/pages/my-posts.html', context)

# #-----------------------------***-----------------------------
# #-------------------- User Transaction Type ------------------
# #-----------------------------***-----------------------------


def check_user_transaction_type(request, user_wallet_transaction_qs, user_wallet_qs):
    if user_wallet_transaction_qs.transaction_type == 1:
        is_flat_rate_plan = user_wallet_qs.last().is_in_flat_plan
        if not is_flat_rate_plan:
            user_point_wallet_transaction_qs = UserWalletTransaction.objects.filter(user=request.user,
                                                                                    transaction_type=0).order_by('created_at').last()
            if not user_point_wallet_transaction_qs:
                messages.error(request, 'Please Update Your Wallet')
                return False
            elif user_wallet_qs.last().available_points <= 0:
                messages.error(
                    request, 'You have not Available Points, Please update Your Wallet')
                return False
            return 'point_transaction_type'
        today = timezone.datetime.now().date()
        # today = 2021-12-10
        flat_plan_created_date = user_wallet_qs.last().flat_plan_created_at
        flat_rate_plan_qs = user_wallet_transaction_qs.flat_rate_plan
        days = today - flat_plan_created_date.date()
        expiration_cycle = flat_rate_plan_qs.expiration_cycle
        if expiration_cycle == 0:
            if days.days >= 0 and days.days < 31:
                return True
            else:
                user_wallet_qs.update(is_in_flat_plan=False,
                                      flat_plan_created_at=None)
        elif expiration_cycle == 1:
            if days.days >= 0 and days.days < 366:
                return True
            else:
                user_wallet_qs.update(is_in_flat_plan=False,
                                      flat_plan_created_at=None)
        elif expiration_cycle == 2:
            if days.days >= 0 and days.days < 182.6:
                return True
            else:
                user_wallet_qs.update(is_in_flat_plan=False,
                                      flat_plan_created_at=None)
        else:
            return False
    else:
        return 'point_transaction_type'

# #-----------------------------***-----------------------------
# #------------------------ User All Checking -----------------------
# #-----------------------------***-----------------------------


def user_wallet_checking(request, post_qs, user_qs):
    """
    :param request:
    :param post_qs: (Post Model)
    :param user_qs: (request user)
    :return: (list)
    """
    # user_wallet_qs = ''
    # user_available_points = 0
    # post_weight = 0
    # user_wallet_transaction_qs = ''
    # transaction_type =''
    context = {}
    if not post_qs:
        return HttpResponseNotFound('<h3> Post not found </h3>')
    user_wallet_qs = UserWallet.objects.filter(
        user_id=user_qs).order_by('created_at')
    if not user_wallet_qs:
        messages.error(request, 'User Wallet not found')

    user_available_points = user_wallet_qs.last().available_points
    if post_qs.weight > 0:
        post_weight = post_qs.weight
    else:
        post_weight = post_qs.thread.weight

    user_wallet_transaction_qs = UserWalletTransaction.objects.filter(
        user=user_wallet_qs.last().user).order_by('created_at').last()
    if not user_wallet_transaction_qs:
        messages.error(
            request, 'Your Transaction Wallet Not Found, Please Purchase Point')
        return context

    transaction_type = check_user_transaction_type(
        request, user_wallet_transaction_qs, user_wallet_qs)
    if not transaction_type:
        messages.error(request, 'User Wallet Transaction not found, ')

    context = {'user_wallet_qs': user_wallet_qs,
               'user_available_points': user_available_points,
               'post_weight': post_weight,
               'user_wallet_transaction_qs': user_wallet_transaction_qs,
               'transaction_type': transaction_type}
    return context

# #-----------------------------***-----------------------------
# #------------------------ User Wallet Update -----------------------
# #-----------------------------***-----------------------------


def user_wallet_update(request, user_wallet_qs, post_weight):
    """
    :param request:
    :param user_wallet_qs:(UserWallet Model)
    :param post_weight:(int)
    :return:bool
    """
    if user_wallet_qs and post_weight:
        new_user_available_points = user_wallet_qs.last().available_points - post_weight
        user_wallet_qs.update(available_points=new_user_available_points)
    return True


# #-----------------------------***-----------------------------
# #------------------------ User Profile -----------------------
# #-----------------------------***-----------------------------

@login_required()
def user_profile(request):
    page_title = request.user.username
    msg = request.POST.get('msg')
    husband_lists = Husband.objects.filter(user=request.user)
    post_lists = Post.objects.filter(user=request.user)
    total_post_read = Post.objects.filter(allowed_users=request.user).count()
    user_wallet = UserWallet.objects.filter(user=request.user).last()
    user_wallet_transaction = UserWalletTransaction.objects.filter(
        user=request.user).first()
    context = {'husband_lists': husband_lists,
               'post_lists': post_lists, 'page_title': page_title,
               'user_wallet': user_wallet,
               'user_wallet_transaction': user_wallet_transaction,
               'total_post_read': total_post_read}
    return render(request, 'user-panel/backup/profile.html', context)

@login_required()
def user_profile_details(request, slug):
    page_title = "User Profile"
    user = get_user_model().objects.filter(slug__iexact=slug).first()
    husband_lists = Husband.objects.filter(user=user)
    post_lists = Post.objects.filter(user=user)
    total_post_read = Post.objects.filter(allowed_users=user).count()
    user_wallet = UserWallet.objects.filter(user=user).last()
    user_wallet_transaction = UserWalletTransaction.objects.filter(
        user=user).first()
    context = {'husband_lists': husband_lists,
               'post_lists': post_lists, 'page_title': page_title,
               'user_wallet': user_wallet,
               'user_wallet_transaction': user_wallet_transaction,
               'total_post_read': total_post_read}
    return render(request, 'user-panel/pages/user-profile.html', context)

# #-----------------------------***-----------------------------
# #------------------------ Profile Update-----------------------
# #-----------------------------***-----------------------------


def user_profile_edit(request, slug):
    if request.method == 'POST':
        user = get_user_model().objects.filter(slug__iexact=slug).first()
        
        # get form data
        
        # check if image is valid
        image = request.FILES.get('image')
        if image:
            is_valid_image = check_is_valid_image(image)
            if is_valid_image[0] == False:
                messages.add_message(
                    request, messages.ERROR, is_valid_image[1])
                return HttpResponseRedirect(reverse("user_profile_detail", kwargs={'slug': slug}))
            else:
                user.image = image
                
        # get user personal infromation
        user.name = request.POST.get('name')
        user.age = int(request.POST.get('age', None)) if request.POST.get('age') else None
        user.address = request.POST.get('address')
        user.marriage_experience = request.POST.get('marriage-experience')
        user.save()
        
        # check if user has husband otherwise create new husband
        husband_qs = Husband.objects.filter(user=user)
        if husband_qs:
            husband_qs.update(
                name=request.POST.get('husband-name'),
                age=int(request.POST.get('husband-age', None)) if request.POST.get('husband-age') else None,
                address=request.POST.get('husband-address'),
                characteristics=request.POST.get('characteristics'),
            )
        else:
            Husband.objects.create(
                user=user,
                name=request.POST.get('husband-name'),
                age=int(request.POST.get('husband-age', None)) if request.POST.get('husband-age') else None,
                address=request.POST.get('husband-address'),
                characteristics=request.POST.get('characteristics'),
            )
        return HttpResponseRedirect(reverse('user_profile_detail', kwargs={'slug': slug}))
    return render(request, 'user-panel/pages/user-profile-edit.html')


def user_profile_update(request, slug):
    user_qs = User.objects.filter(slug=slug).order_by('date_joined').last()
    form = UserManageForm(instance=user_qs)
    if request.method == 'POST':
        form = UserManageForm(request.POST, instance=user_qs)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('user_profile'))
    context = {'form': form}
    return render(request, 'user-panel/form.html', context)
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
            husband_qs = Husband.objects.filter(name__iexact=name).last()
            if not husband_qs:
                husband_qs = Husband.objects.create(user=user, name=name,
                                                    nationality=nationality, address=address,
                                                    dob=dob, characteristics=characteristics)
                if husband_qs:
                    return HttpResponseRedirect(reverse('user_profile'))
    context = {'form': form}
    return render(request, 'user-panel/form.html', context)


# #-----------------------------***-----------------------------
# #------------------------ Husband Details --------------------
# #-----------------------------***-----------------------------

@login_required()
def husband_details(request, slug):
    husband_qs = Husband.objects.filter(slug=slug).last()
    form = HusbandManageForm(instance=husband_qs)
    is_details = True
    context = {'form': form, 'is_details': is_details}
    return render(request, 'user-panel/form.html', context)

# #-----------------------------***-----------------------------
# #------------------------ Husband Update ---------------------
# #-----------------------------***-----------------------------


@login_required()
def husband_update(request, slug):
    husband_qs = Husband.objects.filter(slug=slug).last()
    form = HusbandManageForm(instance=husband_qs)
    # url = request.path
    if request.method == 'POST':
        form = HusbandManageForm(request.POST, instance=husband_qs)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('user_profile'))
    context = {'form': form}
    return render(request, 'user-panel/form.html', context)


# #----------------------------------------****----------------------------------------
# #--------------------------------------- Post ---------------------------------------
# #----------------------------------------****----------------------------------------

@login_required()
def create_post(request):
    # form = PostManageForm
    if request.method == 'POST':
        user_qs = request.user

        # get form data
        title = request.POST.get('title')
        thread_slug = request.POST.get('thread-slug')
        summary = request.POST.get('summary')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        post_title_qs = Post.objects.filter(title__iexact=title)
        if post_title_qs:
            messages.error(request, 'Post Title is Already Exists')
            return HttpResponseRedirect(reverse("thread_post_list", kwargs={'slug': thread_slug}))

        # check if image is valid
        if image:
            is_valid_image = check_is_valid_image(image)
            if is_valid_image[0] == False:
                messages.add_message(
                    request, messages.ERROR, is_valid_image[1])
                return HttpResponseRedirect(reverse("thread_post_list", kwargs={'slug': thread_slug}))

        thread_qs = Thread.objects.filter(slug__iexact=thread_slug)

        if thread_qs.exists():
            thread_obj = thread_qs.first()
            thread_weight = thread_obj.weight

            if thread_weight > 0:
                has_valid_flat_rate_transaction = False
                has_available_points = False

                # *** Is In Flat Rate Checking ***
                flat_rate_plan_qs = UserWalletTransaction.objects.filter(
                    user=request.user, transaction_type=1).order_by('created_at')
                if flat_rate_plan_qs.exists():
                    for user_wallet_transaction in flat_rate_plan_qs:
                        if not user_wallet_transaction.flat_rate_plan.get_is_expired():
                            has_valid_flat_rate_transaction = True
                            break

                if not has_valid_flat_rate_transaction:
                    # update user wallet and set to None
                    user_wallet_qs = UserWallet.objects.filter(
                        user=request.user)
                    if user_wallet_qs.exists():
                        user_wallet_qs.update(
                            is_in_flat_plan=False, flat_plan_created_at=None)

                    # *** If Available Points Checking ***
                    available_points = user_wallet_qs.first().available_points

                    # check if available point is greater than or equal thread_weight
                    if available_points >= thread_weight:
                        # update user wallet and deduct points
                        user_wallet_qs.update(available_points=(
                            available_points - thread_weight))
                        # create post
                        post_qs = Post.objects.create(user=user_qs, title=title, thread=thread_obj, summary=summary,
                                                      description=description, image=image)
                        post_qs.allowed_users.add(request.user)
                        messages.success(request, 'Post created successfully!')
                        return HttpResponseRedirect(reverse("thread_post_list", kwargs={'slug': thread_slug}))
                    else:
                        has_available_points = False

                # if has valid flat rate transaction
                else:
                    post_qs = Post.objects.create(user=user_qs, title=title, thread=thread_obj, summary=summary,
                                                  description=description, image=image)
                    post_qs.allowed_users.add(request.user)
                    messages.success(request, 'Successfully Post Added')
                    return HttpResponseRedirect(reverse('user_profile'))

                if not has_valid_flat_rate_transaction and not has_available_points:
                    messages.error(request, f'Please purchase points or flat rate plan to create post '
                                            f'under this thread. This thread requires at least {thread_weight} points.')
                    return HttpResponseRedirect(reverse("thread_post_list", kwargs={'slug': thread_slug}))

            # if there is no weight of thread
            else:
                post_qs = Post.objects.create(user=user_qs, title=title, thread=thread_obj, summary=summary,
                                              description=description, image=image)
                post_qs.allowed_users.add(request.user)
                messages.success(request, 'Successfully Post Added')
                return HttpResponseRedirect(reverse("thread_post_list", kwargs={'slug': thread_slug}))
        else:
            messages.error(request, 'Thread not found!')
            return HttpResponseRedirect(reverse("thread_post_list", kwargs={'slug': thread_slug}))

        messages.error(request, 'Something went wrong!')
    # context = {'form': form}
    context = {}
    return render(request, 'user-panel/pages/index.html', context)

# #-----------------------------***-----------------------------
# #------------------------ Post Details ------------------------
# #-----------------------------***-----------------------------


def post_details_free(request, slug):
    post_qs = Post.objects.filter(slug=slug).order_by('created_at').last()
    form = PostManageForm(instance=post_qs)

    # page contexts
    context = {
        'form': form,
        'post': post_qs,
        'active_thread': post_qs.thread,
        'post_qs': post_qs,
        'page_title': post_qs.title,
    }

    return render(request, 'user-panel/pages/post/post-details.html', context)

@login_required()
def post_details(request, slug):
    post_qs = Post.objects.filter(slug=slug).order_by('created_at').last()
    form = PostManageForm(instance=post_qs)
    user_wallet = None
    has_valid_flat_rate_transaction = False
    available_points = False
    # ...***... For Comment Show ...***...
    is_comment_show = True
    # ...***... For Chat Box Show ...***...
    is_chat_show = False
    # ...***... For Post Details  Show ...***...
    is_read_more = False
    comment = request.POST.get('comment')
    read_more = request.POST.get('read_more')
    already_post_read_user = post_qs.allowed_users.filter(name=request.user)
    # ...***... Post Weight Check Start ...***...
    if post_qs.weight > 0:
        post_weight = post_qs.weight
    else:
        post_weight = post_qs.thread.weight
    # ...***... Post Weight Check End...***...
    # ..***.. Check Request User is Creator of This Post Or Not Start ..***..
    if not already_post_read_user:
        if post_weight > 0:
            # ...***... Is In Flat Rate Checking Start ...***...
            flat_rate_plan_qs = UserWalletTransaction.objects.filter(user=request.user, transaction_type=1).order_by(
                'created_at')
            # ..***.. If Flat Rate Validation Checking Start ..***..
            if flat_rate_plan_qs.exists():
                for user_wallet_transaction in flat_rate_plan_qs:
                    if not user_wallet_transaction.flat_rate_plan.get_is_expired():
                        has_valid_flat_rate_transaction = True
                        break
            # ..***.. If Flat Rate Validation Checking End ..***..

            # ..***.. Point Validation Checking  Start ..***..
            if not has_valid_flat_rate_transaction:
                user_wallet_qs = UserWallet.objects.filter(user=request.user).order_by('-created_at')
                # ...***... Update User Wallet and Set to None Start ...***...
                if user_wallet_qs.exists():
                    user_wallet_qs.update(is_in_flat_plan=False, flat_plan_created_at=None)
                # ...***... Update User Wallet and Set to None End ...***...
                # ...***... Available Points Check Start ...***...
                available_points = user_wallet_qs.first().available_points
                # ...***... Available Points Check End ...***...

                # ...***... Available Point is less than or not Post Weight Checking Start ..***..
                if available_points >= post_weight:
                    is_chat_show = True
                    if request.method == 'POST':
                        user_wallet_qs.update(available_points = (available_points - post_weight))
                        post_qs.allowed_users.add(request.user)
                        if read_more:
                            is_read_more = True
                        # ...***... Comment Create Start ...***...
                        if comment:
                            Comment.objects.create(post=post_qs,
                                                   commented_by=request.user,
                                                   comment=comment)
                            messages.success(request, 'Comment Add Successfully!')
                        # ...***... Comment Create End ...***...
                else:
                    # ..***.. If User Want to Read  Part of Post Or Comment Start..***..
                    if read_more or comment:
                        is_read_more = False
                        is_comment_show = False
                        messages.error(request, f'Please purchase points or flat rate plan to view this post.'
                                                f' This post requires at least {post_weight} points.')
                        return HttpResponseRedirect(reverse("thread_post_list", kwargs={'slug': post_qs.thread.slug}))
                    # ..***.. If User Want to Read  Part of Post Or Comment End..***..
                # ...***... Available Point is less than or not Post Weight Checking End ..***..

            # ...***... Is Has Flat Rate is valid Start ...***...
            else:
                is_chat_show = True
                if request.method == 'POST':
                    post_qs.allowed_users.add(request.user)
                    if read_more:
                        is_read_more = True
                    if comment:
                        Comment.objects.create(post=post_qs,
                                               commented_by=request.user,
                                               comment=comment)
                        messages.success(request, 'Comment added successfully!')
            # ...***... Is Has Flat Rate is valid End ...***...

            # ..***.. Point Validation Checking  End ..***..

        else:
            # ...**... For Chat Box Show Start ...**...
            is_chat_show = True
            # ...**... For Chat Box Show End ...**...
            if request.method == 'POST':
                # post_qs.allowed_users.add(request.user)
                if read_more:
                    is_read_more = True
                # ...***... Comment Create Start ...***...
                if comment:
                    Comment.objects.create(post=post_qs,
                                           commented_by=request.user,
                                           comment=comment)
                    messages.success(request, 'Comment added successfully!')
                # ...***... Comment Create End ...***..
    else:
        # is_chat_show = True
        if request.method == 'POST':
            if read_more:
                is_read_more = True
            if comment:
                Comment.objects.create(post=post_qs,
                                       commented_by=request.user,
                                       comment=comment)
                messages.success(request, 'Comment added successfully')
    # ..***.. Check Request User is Creator of This Post Or Not End ..***..

    # if not has_valid_flat_rate_transaction and not available_points:
    #     messages.error(request, f'Please purchase points or flat rate plan to create post under this'
    #                             f' thread. This thread requires at least {post_weight} points.')
    #     return redirect('user_profile')

    # if post_qs.user == request.user:
    #     is_chat_show = False

    # For Chat Option
    # message_list = Message.objects.filter((Q(sender = request.user)|Q(receiver = request.user)) and
    #                                       (Q(sender = post_qs.user)|Q(receiver = post_qs.user)),
    #                                       room = slug
    #                                       ).order_by('created_at')[0:25]
    user = request.user.id
    user_name = request.user
    # receiver_id = post_qs.user.id
    context = {'form': form,
               'post': post_qs,
               'active_thread': post_qs.thread,
               'post_qs': post_qs,
               'page_title': post_qs.title,
               'available_point': available_points,
               'post_weight': post_weight,
               'user_wallet': user_wallet,
               'is_comment_show': is_comment_show,
               'is_read_more': is_read_more,
            #    'is_chat_show':is_chat_show,
               # For Chat Option
               'user':user,
            #    'message_list':message_list,
            #    'receiver_id':receiver_id,
            #    'room_name': slug,
               'user_name': user_name
               }
    return render(request, 'user-panel/pages/post/post-details.html', context)

# #-----------------------------***-----------------------------
# #------------------------ Post Update ------------------------
# #-----------------------------***-----------------------------


@login_required()
def post_update(request, slug):
    post_qs = Post.objects.filter(slug=slug).last()
    form = PostManageForm(instance=post_qs)
    if request.method == 'POST':
        form = PostManageForm(request.POST, instance=post_qs)
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


# #-----------------------------***-----------------------------
# #----------------------Post Comment Reply --------------------
# #-----------------------------***-----------------------------

@login_required()
def comment_reply(request, id):
    comment_qs = Comment.objects.filter(id=id)
    post_qs = None
    is_read_more = False
    is_comment_show = True
    page_title = None
    if comment_qs:
        if request.method == 'POST':
            comment_object = comment_qs.last()
            reply = request.POST.get("reply")
            comment = request.POST.get("comment")
            has_valid_flat_rate_transaction = False
            available_points = False
            slug = comment_object.post.slug
            post_qs = Post.objects.filter(slug=slug).last()
            page_title = post_qs.title
            user_wallet = None
            read_more = request.POST.get('read_more')
            already_post_read_user = post_qs.allowed_users.filter(
                name=request.user)
            # ...***... Post Weight Check Start ...***...
            if post_qs.weight > 0:
                post_weight = post_qs.weight
            else:
                post_weight = post_qs.thread.weight
            # ...***... Post Weight Check End...***...

            # ...***... For Add Comment Reply When The Post User \
            # Doesn't Read or Add Comment Before...***...

            if not already_post_read_user:
                if post_weight > 0:
                    # ...***... Is In Flat Rate Checking Start ...***...
                    flat_rate_plan_qs = UserWalletTransaction.objects.filter(user=request.user,
                                                                             transaction_type=1)
                    if flat_rate_plan_qs:
                        for user_wallet_transaction in flat_rate_plan_qs:
                            if not user_wallet_transaction.flat_rate_plan.get_is_expired():
                                has_valid_flat_rate_transaction = True
                                is_valid = True
                                break

                    # ...***... Is In Flat Rate Checking End ...***...

                    # ...***... Point Validation Checking Start ...***...
                    if not has_valid_flat_rate_transaction:
                        user_wallet_qs = UserWallet.objects.filter(
                            user=request.user).order_by('-created_at')
                        # ...***... Update User Wallet and Set to None Start ...***...
                        if user_wallet_qs.exists():
                            user_wallet_qs.update(
                                is_in_flat_plan=False, flat_plan_created_at=None)
                        # ...***... Update User Wallet and Set to None End ...***...
                        1
                        # ...***... Available Points Check Start ...***...

                        # ...***... Available Points Check Start ...***...
                        available_points = user_wallet_qs.first().available_points
                        # ...***... Available Points Check End ...***...

                        # ...***... Available Point is less than or not Post Weight Checking Start ..***..
                        if available_points >= post_weight:
                            user_wallet_qs.update(available_points=(
                                available_points - post_weight))
                            post_qs.allowed_users.add(request.user)
                            if read_more:
                                is_read_more = True
                            if comment:
                                # ..***.. Comment Create Start ..***..
                                Comment.objects.create(post=post_qs,
                                                       commented_by=request.user,
                                                       comment=comment)
                                # ..***.. Comment Create End ..***..
                            if reply:
                                # ..***.. Reply Create Start ..***..
                                CommentReply.objects.create(comment=comment_object,
                                                            replied_by=request.user,
                                                            reply=reply)
                                messages.success(
                                    request, ' Reply added successfully')
                                # ..***.. Reply Create End ..***..

                        # ...***... Available Point is less than or not Post Weight Checking End ..***..
                        else:
                            if read_more or comment or reply:
                                is_read_more = False
                                is_comment_show = False
                                messages.error(request, f'Please purchase points or flat rate plan to '
                                                        f'create post under this thread. This thread'
                                                        f' requires at least {post_weight} points.')
                    else:
                        # ..***.. If User Want to Read Rest Part of Post Or Comment  or Reply Start ..***..
                        if read_more or comment or reply:
                            is_read_more = False
                            is_comment_show = False
                            messages.error(request, f'Please purchase points or flat rate plan to '
                                                    f'create post under this thread. This thread'
                                                    f' requires at least {post_weight} points.')
                        # ..***.. If User Want to Read Rest Part of Post Or Comment  or Reply End ..***..
                    # ...***... Available Point is less than or not Post Weight Checking End ..***..
                    # ...***... Point Validation Checking End ...***...
                # ..***.. Post Weight is 0 Reply & Comment Add Start ..***..
                else:
                    # post_qs.allowed_users.add(request.user)
                    if read_more:
                        is_read_more = True
                    if reply:
                        is_comment_show = True
                        CommentReply.objects.create(comment=comment_object,
                                                    replied_by=request.user,
                                                    reply=reply)
                        messages.success(request, 'Reply added successfully')
                # ..***.. Post Weight is 0 Reply & Comment Add End ..***..

            # ...***... For Add Comment Reply When The Post User \
            # Doesn't Read or Add Comment Before End ...***...

            # ...***... For Add Comment Reply When The Post is Already User \
            #  Read or Add Comment Before Start...***...
            else:
                if read_more:
                    is_read_more = True
                if reply:
                    is_comment_show = True
                    CommentReply.objects.create(comment=comment_object,
                                                replied_by=request.user,
                                                reply=reply)
                    messages.success(request, 'Reply added successfully')
                if comment:
                    is_comment_show = True
                    Comment.objects.create(post=post_qs,
                                           commented_by=request.user,
                                           comment=comment)
                    messages.success(request, 'Comment added successfully!')

            # ...***... For Add Comment Reply When The Post is Already User \
            #  Read or Add Comment Before End...***...
        else:
            # messages.error(request, 'Can Not Found')
            return redirect('user_profile')
    context = {'post_qs': post_qs,
               'post': post_qs,
               'active_thread': post_qs.thread,
               'page_title': page_title,
               'post_weight': post_weight,
               'is_comment_show': is_comment_show,
               'is_read_more': is_read_more}
    return render(request, 'user-panel/pages/post/post-details.html', context)

# #-----------------------------***-----------------------------
# #------------------------ All Post List ----------------------
# #-----------------------------***-----------------------------


def post_list(request, slug):
    thread_qs = Thread.objects.filter(slug=slug).last()
    post_lists = Post.objects.filter(thread=thread_qs)
    context = {'page_title': thread_qs.title,
               'thread_qs': thread_qs, 'post_lists': post_lists}
    return render(request, 'user-panel/post_list.html', context)

# #-----------------------------***-----------------------------
# #------------------------ All FAQ List ------------------------
# #-----------------------------***-----------------------------


def faq_list(request):
    faq_lists = FAQ.objects.filter(is_active=True)
    context = {
        'faq_lists': faq_lists
    }
    return render(request, 'user-panel/post_list.html', context)
