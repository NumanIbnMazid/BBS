from django.views.generic import TemplateView

from plans.models import UserWalletTransaction
from users.models import Husband, UserWallet, User
from django.http import HttpResponse, HttpResponseNotFound
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from posts.models import Post, Comment, CommentReply,Thread
from django.contrib import messages
from django.urls import reverse
from .forms import HusbandManageForm, PostManageForm, UserManageForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View
from datetime import date, datetime, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError

# #-----------------------------***-----------------------------
# #---------------------------- Home ---------------------------
# #-----------------------------***-----------------------------


class HomeView(TemplateView):
    template_name = "user-panel/index.html"
    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        thread_lists = Thread.objects.all()
        post_lists = Post.objects.all().distinct()
        context["page_title"] = "Home"
        context['page_title'] ='Thread lists'
        context['thread_lists'] =thread_lists
        context['post_lists'] =post_lists
        return context

# #-----------------------------***-----------------------------
# #-------------------- User Transaction Type ------------------
# #-----------------------------***-----------------------------

def check_user_transaction_type(request, user_wallet_transaction_qs, user_wallet_qs):
    """
    :param request, user_wallet_transaction_qs(UserWalletTransaction), user_wallet_qs(UserWallet):
    :return: bool
    """
    if user_wallet_transaction_qs.transaction_type == 1:
        is_flat_rate_plan = user_wallet_qs.last().is_in_flat_plan
        if not is_flat_rate_plan:
            user_point_wallet_transaction_qs = UserWalletTransaction.objects.filter(user=request.user,
                                                                              transaction_type=0).order_by('created_at').last()
            if not user_point_wallet_transaction_qs:
                messages.error(request, 'Please Update Your Wallet')
                return False
            elif user_wallet_qs.last().available_points <= 0:
                messages.error(request, 'You have not Available Points, Please update Your Wallet')
                return False
            return 'point_transaction_type'
        today = timezone.datetime.now().date()
        # today = 2021-12-10
        flat_plan_created_date = user_wallet_qs.last().flat_plan_created_at
        flat_rate_plan_qs = user_wallet_transaction_qs.flat_rate_plan
        days = today - flat_plan_created_date.date()
        expiration_cycle = flat_rate_plan_qs.expiration_cycle
        if expiration_cycle == 0:
            if days.days >=0 and days.days < 31:
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
            return True
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
    context ={}
    if not post_qs:
        return HttpResponseNotFound('<h3> Post not found </h3>')
    user_wallet_qs = UserWallet.objects.filter(user_id = user_qs).order_by('created_at')
    if not user_wallet_qs:
        messages.error(request, 'User Wallet not found')

    user_available_points = user_wallet_qs.last().available_points
    if post_qs.weight > 0:
        post_weight = post_qs.weight
    else:
        post_weight = post_qs.thread.weight

    user_wallet_transaction_qs = UserWalletTransaction.objects.filter(user=user_wallet_qs.last().user).order_by('created_at').last()
    if not user_wallet_transaction_qs:
        messages.error(request,'Your Transaction Wallet Not Found, Please Purchase Point')
        return context

    transaction_type = check_user_transaction_type(request, user_wallet_transaction_qs, user_wallet_qs)
    if not transaction_type:
        messages.error(request, 'User Wallet Transaction not found, ')

    context = {'user_wallet_qs':user_wallet_qs,
               'user_available_points':user_available_points,
               'post_weight':post_weight,
               'user_wallet_transaction_qs':user_wallet_transaction_qs,
               'transaction_type':transaction_type}
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
    husband_lists = Husband.objects.filter(user  = request.user)
    post_lists = Post.objects.filter(user = request.user)
    user_wallet = UserWallet.objects.filter(user = request.user).last()
    user_wallet_transaction = UserWalletTransaction.objects.filter(user = request.user).first()
    context = {'husband_lists':husband_lists,
               'post_lists':post_lists,'page_title':page_title,
               'user_wallet':user_wallet,'user_wallet_transaction':
               user_wallet_transaction}
    return render(request,'user-panel/profile.html', context)

# #-----------------------------***-----------------------------
# #------------------------ Profile Update-----------------------
# #-----------------------------***-----------------------------
def user_profile_update(request, slug):
    user_qs = User.objects.filter(slug = slug).order_by('date_joined').last()
    form = UserManageForm(instance=user_qs)
    if request.method == 'POST':
        form = UserManageForm(request.POST,instance=user_qs)
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
    # url = request.path
    if request.method == 'POST':
        form = HusbandManageForm(request.POST,instance=husband_qs)
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
    form = PostManageForm
    if request.method == 'POST':
        user_qs = request.user
        title = request.POST.get('title')
        post_title_qs = Post.objects.filter(title__iexact = title)
        if post_title_qs:
            messages.error(request, 'Post Title is Already Exists')
            return HttpResponseRedirect(reverse("create_post"))
        thread = request.POST.get('thread')
        description = request.POST.get('description')

        thread_qs = Thread.objects.filter(id=int(request.POST.get('thread')))

        if thread_qs.exists():
            thread_obj = thread_qs.first()
            thread_weight = thread_obj.weight

            if thread_weight > 0:
                has_valid_flat_rate_transaction = False
                has_available_points = False

                # *** Is In Flat Rate Checking ***
                flat_rate_plan_qs = UserWalletTransaction.objects.filter(user=request.user, transaction_type=1).order_by('created_at')
                if flat_rate_plan_qs.exists():
                    for user_wallet_transaction in flat_rate_plan_qs:
                        if not user_wallet_transaction.flat_rate_plan.get_is_expired():
                            has_valid_flat_rate_transaction = True
                            break

                if not has_valid_flat_rate_transaction:
                    # update user wallet and set to None
                    user_wallet_qs = UserWallet.objects.filter(user=request.user)
                    if user_wallet_qs.exists():
                        user_wallet_qs.update(is_in_flat_plan=False, flat_plan_created_at=None)

                    # *** If Available Points Checking ***
                    available_points = user_wallet_qs.first().available_points

                    # check if available point is greater than or equal thread_weight
                    if available_points >= thread_weight:
                        # update user wallet and deduct points
                        user_wallet_qs.update(available_points=(available_points - thread_weight))
                        # create post
                        post_qs = Post.objects.create(user=user_qs, title=title, thread=thread_obj,
                                                      description=description)
                        post_qs.allowed_users.add(request.user)
                        messages.success(request, 'Post created successfully!')
                        return HttpResponseRedirect(reverse('user_profile'))
                    else:
                        has_available_points = False

                # if has valid flat rate transaction
                else:
                    post_qs = Post.objects.create(user=user_qs, title=title, thread=thread_obj,
                                                  description=description)
                    post_qs.allowed_users.add(request.user)
                    messages.success(request, 'Successfully Post Added')
                    return HttpResponseRedirect(reverse('user_profile'))

                if not has_valid_flat_rate_transaction and not has_available_points:
                    messages.error(request, f'Please purchase points or flat rate plan to create post '
                                            f'under this thread. This thread requires at least {thread_weight} points.')
                    return redirect('user_profile')

            # if there is no weight of thread
            else:
                post_qs = Post.objects.create(user=user_qs, title=title, thread=thread_obj,
                                              description=description)
                post_qs.allowed_users.add(request.user)
                messages.success(request, 'Successfully Post Added')
                return HttpResponseRedirect(reverse('user_profile'))
        else:
            messages.error(request, 'Thread not found!')
            return redirect('user_profile')

        messages.error(request, 'Something went wrong!')
    context = {'form': form}
    return render(request, 'user-panel/form.html', context)

# #-----------------------------***-----------------------------
# #------------------------ Post Details ------------------------
# #-----------------------------***-----------------------------

@login_required()
def post_details(request, slug):
    post_qs = Post.objects.filter(slug=slug).order_by('created_at').last()
    form = PostManageForm(instance=post_qs)
    user_wallet = None
    has_valid_flat_rate_transaction = False
    available_points = False
    # ...***... For Comment Show ...***...
    is_comment_show = True
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
                user_wallet_qs = UserWallet.objects.filter(user = request.user).order_by('-created_at')
                # ...***... Update User Wallet and Set to None Start ...***...
                if user_wallet_qs.exists():
                    user_wallet_qs.update(is_in_flat_plan=False, flat_plan_created_at=None)
                # ...***... Update User Wallet and Set to None End ...***...
                # ...***... Available Points Check Start ...***...
                available_points = user_wallet_qs.first().available_points
                # ...***... Available Points Check End ...***...

                # ...***... Available Point is less than or not Post Weight Checking Start ..***..
                if available_points >= post_weight:
                    if request.method == 'POST':
                        user_wallet_qs.update(available_points =(available_points-post_weight))
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
                        messages.error(request, f'Please purchase points or flat rate plan to create post under this'
                                                f' thread. This thread requires at least {post_weight} points.')
                    # ..***.. If User Want to Read  Part of Post Or Comment End..***..
                # ...***... Available Point is less than or not Post Weight Checking End ..***..
            # ...***... Is Has Flat Rate is valid Start ...***...
            else:
                if request.method == 'POST':
                    post_qs.allowed_users.add(request.user)
                    if read_more:
                        is_read_more = True
                    if comment:
                        Comment.objects.create(post=post_qs,
                                               commented_by=request.user,
                                               comment=comment)
                        messages.success(request, 'Comment Add Successfully!')
            # ...***... Is Has Flat Rate is valid End ...***...

            # ..***.. Point Validation Checking  End ..***..

        else:
            if request.method == 'POST':
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
            # if read_more or comment:
            #     is_read_more = True
            #     messages.error(request, f'Please purchase points or flat rate plan to '
            #                             f'create post under this thread. This thread'
            #                             f' requires at least {post_weight} points.')
    else:
        if request.method == 'POST':
            if read_more:
                is_read_more = True
            if comment:
                Comment.objects.create(post=post_qs,
                                       commented_by=request.user,
                                       comment=comment)
                messages.success(request, 'Comment Add Successfully')
    # ..***.. Check Request User is Creator of This Post Or Not End ..***..

    # if not has_valid_flat_rate_transaction and not available_points:
    #     messages.error(request, f'Please purchase points or flat rate plan to create post under this'
    #                             f' thread. This thread requires at least {post_weight} points.')
    #     return redirect('user_profile')

    context = {'form': form, 'post_qs': post_qs,
               'page_title': post_qs.title,
               'available_point': available_points,
               'post_weight': post_weight,
               'user_wallet': user_wallet,
               'is_comment_show': is_comment_show,
               'is_read_more': is_read_more
               }
    return render(request, 'user-panel/post-details.html', context)
# @login_required()
# def post_details_dummy(request, slug):
#     post_qs = Post.objects.filter(slug=slug).order_by('created_at').last()
#     page_title = post_qs.title
#     form = PostManageForm(instance=post_qs)
#     user_wallet = None
#     # ...***... Post Weight Check Start ...***...
#     if post_qs.weight > 0:
#         post_weight = post_qs.weight
#     else:
#         post_weight = post_qs.thread.weight
#     # ...***... Post Weight Check End...***...
#
#     has_valid_flat_rate_transaction = False
#     available_points = False
#     # ...***... For Comment Show ...***...
#     is_comment_show = True
#     # ...***... For Post Details  Show ...***...
#     is_read_more = False
#     comment = request.POST.get('comment')
#     read_more = request.POST.get('read_more')
#     already_post_read_user = post_qs.allowed_users.filter(name = request.user)
#
#
#     if post_weight > 0:
#         # ...***... Is In Flat Rate Checking Start ...***...
#         flat_rate_plan_qs = UserWalletTransaction.objects.filter(user=request.user, transaction_type=1).order_by(
#             'created_at')
#         if flat_rate_plan_qs.exists():
#             for user_wallet_transaction in flat_rate_plan_qs:
#                 if not user_wallet_transaction.flat_rate_plan.get_is_expired():
#                     has_valid_flat_rate_transaction = True
#                     # is_valid = True
#                     is_read_more = False
#                     break
#
#         # ...***... Flat Rate Validation Checking Start ...***...
#         if not has_valid_flat_rate_transaction:
#             # ...***... Update User Wallet and Set to None Start ...***...
#             user_wallet_qs = UserWallet.objects.filter(user=request.user)
#             if user_wallet_qs.exists:
#                 user_wallet_qs.update(is_in_flat_plan=False, flat_plan_created_at=None)
#             # ...***... Update User Wallet and Set to None End ...***...
#             # ...***... Available Points Check Start ...***...
#             available_points = user_wallet_qs.first().available_points
#             # ...***... Available Points Check End ...***...
#
#             # ...***... Available Point is less than or not Post Weight Checking Start ...***...
#             if available_points >= post_weight:
#                 # is_valid = True
#                 # ...***... Comment Create Start ...***...
#                 is_read_more = True
#                 if request.method == 'POST':
#                     if not already_post_read_user:
#                         user_wallet_qs.update(available_points=(available_points - post_weight))
#                         post_qs.allowed_users.add(request.user)
#                     if read_more or comment:
#                         is_read_more = True
#                     if comment:
#                         # messages.error(request, 'Comment is Null!')
#                         # return HttpResponseRedirect(reverse("post_details", kwargs={"slug": slug}))
#                         Comment.objects.create(post=post_qs,
#                                                commented_by=request.user,
#                                                comment=comment)
#                         messages.success(request, 'Comment Add Successfully!')
#                 # ...***... Comment Create End ...***...
#             else:
#                 available_points = True
#                 # is_read_more = True
#                 # ..***.. when user click read more button or comment button Start ..***..
#                 if read_more or comment:
#                     # ..***.. If The Post is User Own Post Read Details Permission Provided Start ..***..
#                     if already_post_read_user:
#                         is_read_more = True
#                     # ..***.. If The Post is User Own Post Read Details Permission Provided Start ..***..
#                     else:
#                         is_comment_show = False
#                         messages.error(request, f'Please purchase points or flat rate plan to create post under this'
#                                             f' thread. This thread requires at least {post_weight} points.')
#                 # ..***.. when user click read more button or comment button End ..***..
#             # ...***... Available Point is less than or not Post Weight Checking End ...***...
#         # ...***... Is Has Flat Rate is valid ...***...
#         else:
#             if request.method == 'POST':
#                 if read_more or comment:
#                     is_read_more = True
#                 if comment:
#                     Comment.objects.create(post=post_qs,
#                                            commented_by=request.user,
#                                            comment=comment)
#                     messages.success(request, 'Comment Add Successfully!')
#         # ...***... Flat Rate Validation Checking End ...***...
#
#     # ...***.. When Post Weight or Thread Weight is Zero Start...***...
#     else:
#         # is_valid = True
#         available_points = True
#         if request.method == 'POST':
#             if read_more or comment:
#                 is_read_more = True
#             if comment:
#                 # messages.error(request, 'Comment is Null!')
#                 # return HttpResponseRedirect(reverse("post_details", kwargs={"slug": slug}))
#                 Comment.objects.create(post=post_qs,
#                                    commented_by=request.user,
#                                    comment=comment)
#             # ..***.. User Read Post Or Not ..***..
#             if not already_post_read_user:
#                 post_qs.allowed_users.add(request.user)
#             # messages.success(request, 'Comment Add Successfully!')
#     # ...***.. When Post Weight or Thread Weight is Zero End ...***...
#     # ...***.. When User Wallet is not Valid Start ...***...
#     if not has_valid_flat_rate_transaction and not available_points:
#         if read_more or comment:
#             # ..***.. If The Post is User Own Post Read Details Permission Provided Start ..***..
#             if already_post_read_user:
#                 is_read_more = True
#             # ..***.. If The Post is User Own Post Read Details Permission Provided Start ..***..
#             else:
#                 is_comment_show = False
#                 messages.error(request, f'Please purchase points or flat rate plan to create post under this'
#                                         f' thread. This thread requires at least {post_weight} points.')
#         return redirect('user_profile')
#     # ...***.. When User Wallet is not Valid End ...***...
#
#     context = {'form': form, 'post_qs': post_qs,
#                'page_title': page_title,
#                'available_point': available_points,
#                'post_weight': post_weight,
#                'user_wallet': user_wallet,
#                'is_comment_show':is_comment_show,
#                'is_read_more':is_read_more
#                }
#     return render(request, 'user-panel/post-details.html', context)

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


# #-----------------------------***-----------------------------
# #----------------------Post Comment Reply --------------------
# #-----------------------------***-----------------------------

@login_required()
def comment_reply(request, id):
    comment_qs = Comment.objects.filter(id=id)
    if comment_qs:
        if request.method == 'POST':
            comment_object = comment_qs.last()
            reply = request.POST.get("reply")
            slug = comment_object.post.slug
            post_qs = Post.objects.filter(slug=slug).last()
            page_title = post_qs.title
            form = PostManageForm(instance=post_qs)
            user_wallet = None
            is_valid = False
            # ...***... Post Weight Check Start ...***...
            if post_qs.weight > 0:
                post_weight = post_qs.weight
            else:
                post_weight = post_qs.thread.weight
            # ...***... Post Weight Check End...***...

            has_valid_flat_rate_transaction = False
            available_points = False
            # ...***... For Details Post Show ...***...
            if post_weight > 0:
                # ...***... Is In Flat Rate Checking Start ...***...
                flat_rate_plan_qs = UserWalletTransaction.objects.filter(user=request.user,
                                                                         transaction_type=1).order_by(
                    'created_at')
                if flat_rate_plan_qs.exists():
                    for user_wallet_transaction in flat_rate_plan_qs:
                        if not user_wallet_transaction.flat_rate_plan.get_is_expired():
                            has_valid_flat_rate_transaction = True
                            is_valid = True
                            break
                # ...***... Is In Flat Rate Checking End ...***...
                # ...***... Flat Rate Validation Checking Start ...***...
                if not has_valid_flat_rate_transaction:
                    # ...***... Update User Wallet and Set to None Start ...***...
                    user_wallet_qs = UserWallet.objects.filter(user = request.user)
                    if user_wallet_qs.exists():
                        user_wallet_qs.update(is_in_flat_plan=False, flat_plan_created_at=None)
                    # ...***... Update User Wallet and Set to None End ...***...
                    # ...***... Available Points Check Start ...***...
                    available_points = user_wallet_qs.first().available_points
                    # ...***... Available Points Check End ...***...
                    # ...***... Available Point is less than or not Post Weight Checking Start ...***...
                    if available_points >= post_weight:
                        # update user wallet and deduct points
                        user_wallet_qs.update(available_points=(available_points - post_weight))
                        # ...***... Comment Reply Create Start ...***...
                        CommentReply.objects.create(comment=comment_object,
                                                    replied_by=request.user,
                                                    reply=reply)
                        messages.success(request, 'Reply created successfully!')
                        return HttpResponseRedirect(reverse("post_details", kwargs={"slug": slug}))
                    # ...***... Comment Reply Create End ...***...
                    else:
                        available_points = False
                else:
                    CommentReply.objects.create(comment=comment_object,
                                                replied_by=request.user,
                                                reply=reply)
                    messages.success(request, 'Successfully Reply Added')
                    return HttpResponseRedirect(reverse("post_details", kwargs={"slug": slug}))

                if not has_valid_flat_rate_transaction and not available_points:
                    messages.error(request, f'Please purchase points or flat rate plan to create post '
                                            f'under this thread. This thread requires at least {post_weight} points.')
                    return redirect('user_profile')
            else:
                CommentReply.objects.create(comment=comment_object,
                                            replied_by=request.user,
                                            reply=reply)
                messages.success(request, 'Successfully Reply Added')
                return HttpResponseRedirect(reverse("post_details", kwargs={"slug": slug}))
        else:
            messages.error(request, 'Comment Not Found')
            return redirect('user_profile')
    context = {'form': form,
               'post_qs':post_qs,
               'page_title':page_title,
               'is_valid':is_valid}
    return render(request, 'user-panel/post-details.html', context)

# #-----------------------------***-----------------------------
# #------------------------ All Post List ------------------------
# #-----------------------------***-----------------------------

def post_list(request, slug):
    thread_qs = Thread.objects.filter(slug = slug).last()
    post_lists = Post.objects.filter(thread = thread_qs)
    context = {'page_title':thread_qs.title,
               'thread_qs':thread_qs, 'post_lists':post_lists}
    return render(request, 'user-panel/post_list.html', context)
