from django.views.generic import TemplateView, CreateView, UpdateView, DetailView, ListView
from bbs.decorators import has_dashboard_permission_required
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.contrib import messages
from bbs.helpers import (
    validate_normal_form, get_simple_context_data, get_simple_object, delete_simple_object, user_has_permission
)
# *** Forms Import ***
# Posts
from posts.forms import (ThreadManageForm, PostManageForm)
# Plans
from plans.forms import (
    PointPlanManageForm, FlatRatePlanManageForm, UserWalletTransactionManageForm)
# FAQ
from faq.forms import ( FAQManageForm )
# *** Models Import ***
# Posts
from posts.models import (Thread, Post)
# Plans
from plans.models import (PointPlan, FlatRatePlan, UserWalletTransaction)
# FAQ
from faq.models import FAQ
# translator
from .utils import translate_to_jp
from django.utils.translation import gettext as _
from django.utils.translation import get_language, activate, gettext



dashboard_decorators = [login_required, has_dashboard_permission_required]


@method_decorator(dashboard_decorators, name='dispatch')
class DashboardView(TemplateView):
    template_name = "dashboard/pages/index.html"

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context["page_title"] = "Dashboard"
        # context['trans'] = _("hello")
        trans = translate(language='ja')
        context['trans']=trans
        return context

def translate(language):
    cur_language = get_language()
    try:
        activate(language)
        text = gettext('hello')
    finally:
        activate(cur_language)
    return text
""" 
-------------------------------------------------------------------
                           ** Thread ***
-------------------------------------------------------------------
"""

def get_thread_common_contexts(request):
    common_contexts = get_simple_context_data(
        request=request, app_namespace=None, model_namespace="thread", model=Thread, list_template=None, fields_to_hide_in_table=["id", "slug"]
    )
    return common_contexts


@method_decorator(dashboard_decorators, name='dispatch')
class ThreadCreateView(CreateView):
    template_name = "dashboard/snippets/manage.html"
    form_class = ThreadManageForm

    def form_valid(self, form, **kwargs):
        title = form.instance.title
        field_qs = Thread.objects.filter(
            title__iexact=title
        )
        result = validate_normal_form(
            field='title', field_qs=field_qs,
            form=form, request=self.request
        )
        if result == 1:
            return super().form_valid(form)
        else:
            return super().form_invalid(form)

    def get_success_url(self):
        return reverse("create_thread")

    def get_context_data(self, **kwargs):
        context = super(
            ThreadCreateView, self
        ).get_context_data(**kwargs)
        context['page_title'] = 'Create Thread'
        context['page_short_title'] = 'Create Thread'
        for key, value in get_thread_common_contexts(request=self.request).items():
            context[key] = value
        return context


@method_decorator(dashboard_decorators, name='dispatch')
class ThreadDetailView(DetailView):
    template_name = "dashboard/snippets/detail-common.html"

    def get_object(self):
        return get_simple_object(key='slug', model=Thread, self=self)

    def get_context_data(self, **kwargs):
        context = super(
            ThreadDetailView, self
        ).get_context_data(**kwargs)
        context['page_title'] = f'Thread - {self.get_object().title} Detail'
        context['page_short_title'] = f'Thread - {self.get_object().title} Detail'
        for key, value in get_thread_common_contexts(request=self.request).items():
            context[key] = value
        return context


@method_decorator(dashboard_decorators, name='dispatch')
class ThreadUpdateView(UpdateView):
    template_name = 'dashboard/snippets/manage.html'
    form_class = ThreadManageForm

    def get_object(self):
        return get_simple_object(key="slug", model=Thread, self=self)

    def get_success_url(self):
        return reverse("create_thread")

    def form_valid(self, form):
        self.object = self.get_object()
        title = form.instance.title
        if not self.object.title == title:
            field_qs = Thread.objects.filter(
                title__iexact=title
            )
            result = validate_normal_form(
                field='title', field_qs=field_qs,
                form=form, request=self.request
            )
            if result == 1:
                messages.add_message(
                    self.request, messages.SUCCESS, "Thread Updated Successfully!"
                )
                return super().form_valid(form)
            else:
                messages.add_message(
                    self.request, messages.ERROR, "Failed to update!"
                )
                return super().form_invalid(form)

        messages.add_message(
            self.request, messages.SUCCESS, "Thread Updated Successfully!"
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(
            ThreadUpdateView, self
        ).get_context_data(**kwargs)
        context['page_title'] = f'Update Thread "{self.get_object().title}"'
        context['page_short_title'] = f'Update Thread "{self.get_object().title}"'
        for key, value in get_thread_common_contexts(request=self.request).items():
            context[key] = value
        return context


@csrf_exempt
@has_dashboard_permission_required
@login_required
def delete_thread(request):
    return delete_simple_object(request=request, key='slug', model=Thread, redirect_url="create_thread")


""" 
-------------------------------------------------------------------
                        ** Plans: PointPlan ***
-------------------------------------------------------------------
"""


def get_point_plan_common_contexts(request):
    common_contexts = get_simple_context_data(
        request=request, app_namespace=None, model_namespace="point_plan", model=PointPlan, list_template=None, fields_to_hide_in_table=["id", "slug"]
    )
    return common_contexts


@method_decorator(dashboard_decorators, name='dispatch')
class PointPlanCreateView(CreateView):
    template_name = "dashboard/snippets/manage.html"
    form_class = PointPlanManageForm

    def form_valid(self, form, **kwargs):
        title = form.instance.title
        field_qs = PointPlan.objects.filter(
            title__iexact=title
        )
        result = validate_normal_form(
            field='title', field_qs=field_qs,
            form=form, request=self.request
        )
        if result == 1:
            return super().form_valid(form)
        else:
            return super().form_invalid(form)

    def get_success_url(self):
        return reverse("create_point_plan")

    def get_context_data(self, **kwargs):
        context = super(
            PointPlanCreateView, self
        ).get_context_data(**kwargs)
        context['page_title'] = 'Create Point Plan'
        context['page_short_title'] = 'Create Point Plan'
        for key, value in get_point_plan_common_contexts(request=self.request).items():
            context[key] = value
        return context


@method_decorator(dashboard_decorators, name='dispatch')
class PointPlanDetailView(DetailView):
    template_name = "dashboard/snippets/detail-common.html"

    def get_object(self):
        return get_simple_object(key='slug', model=PointPlan, self=self)

    def get_context_data(self, **kwargs):
        context = super(
            PointPlanDetailView, self
        ).get_context_data(**kwargs)
        context['page_title'] = f'Point Plan - {self.get_object().title} Detail'
        context['page_short_title'] = f'Point Plan - {self.get_object().title} Detail'
        for key, value in get_point_plan_common_contexts(request=self.request).items():
            context[key] = value
        return context


@method_decorator(dashboard_decorators, name='dispatch')
class PointPlanUpdateView(UpdateView):
    template_name = 'dashboard/snippets/manage.html'
    form_class = PointPlanManageForm

    def get_object(self):
        return get_simple_object(key="slug", model=PointPlan, self=self)

    def get_success_url(self):
        return reverse("create_point_plan")

    def form_valid(self, form):
        self.object = self.get_object()
        title = form.instance.title
        if not self.object.title == title:
            field_qs = PointPlan.objects.filter(
                title__iexact=title
            )
            result = validate_normal_form(
                field='title', field_qs=field_qs,
                form=form, request=self.request
            )
            if result == 1:
                return super().form_valid(form)
            else:
                return super().form_invalid(form)

        messages.add_message(
            self.request, messages.SUCCESS, "Point Plan Updated Successfully!"
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(
            PointPlanUpdateView, self
        ).get_context_data(**kwargs)
        context['page_title'] = f'Update Point Plan "{self.get_object().title}"'
        context['page_short_title'] = f'Update Point Plan "{self.get_object().title}"'
        for key, value in get_point_plan_common_contexts(request=self.request).items():
            context[key] = value
        return context


@csrf_exempt
@has_dashboard_permission_required
@login_required
def delete_point_plan(request):
    return delete_simple_object(request=request, key='slug', model=PointPlan, redirect_url="create_point_plan")

""" 
-------------------------------------------------------------------
                        ** Plans: FlatRatePlan ***
-------------------------------------------------------------------
"""


def get_flat_rate_plan_common_contexts(request):
    common_contexts = get_simple_context_data(
        request=request, app_namespace=None, model_namespace="flat_rate_plan", model=FlatRatePlan, list_template=None, fields_to_hide_in_table=["id", "slug"]
    )
    return common_contexts


@method_decorator(dashboard_decorators, name='dispatch')
class FlatRatePlanCreateView(CreateView):
    template_name = "dashboard/snippets/manage.html"
    form_class = FlatRatePlanManageForm

    def form_valid(self, form, **kwargs):
        title = form.instance.title
        field_qs = FlatRatePlan.objects.filter(
            title__iexact=title
        )
        result = validate_normal_form(
            field='title', field_qs=field_qs,
            form=form, request=self.request
        )
        if result == 1:
            return super().form_valid(form)
        else:
            return super().form_invalid(form)

    def get_success_url(self):
        return reverse("create_flat_rate_plan")

    def get_context_data(self, **kwargs):
        context = super(
            FlatRatePlanCreateView, self
        ).get_context_data(**kwargs)
        context['page_title'] = 'Create Flat Rate Plan'
        context['page_short_title'] = 'Create Flat Rate Plan'
        for key, value in get_flat_rate_plan_common_contexts(request=self.request).items():
            context[key] = value
        return context


@method_decorator(dashboard_decorators, name='dispatch')
class FlatRatePlanDetailView(DetailView):
    template_name = "dashboard/snippets/detail-common.html"

    def get_object(self):
        return get_simple_object(key='slug', model=FlatRatePlan, self=self)

    def get_context_data(self, **kwargs):
        context = super(
            FlatRatePlanDetailView, self
        ).get_context_data(**kwargs)
        context['page_title'] = f'Flat Rate Plan - {self.get_object().title} Detail'
        context['page_short_title'] = f'Flat Rate Plan - {self.get_object().title} Detail'
        for key, value in get_flat_rate_plan_common_contexts(request=self.request).items():
            context[key] = value
        return context


@method_decorator(dashboard_decorators, name='dispatch')
class FlatRatePlanUpdateView(UpdateView):
    template_name = 'dashboard/snippets/manage.html'
    form_class = FlatRatePlanManageForm

    def get_object(self):
        return get_simple_object(key="slug", model=FlatRatePlan, self=self)

    def get_success_url(self):
        return reverse("create_flat_rate_plan")

    def form_valid(self, form):
        self.object = self.get_object()
        title = form.instance.title
        if not self.object.title == title:
            field_qs = FlatRatePlan.objects.filter(
                title__iexact=title
            )
            result = validate_normal_form(
                field='title', field_qs=field_qs,
                form=form, request=self.request
            )
            if result == 1:
                return super().form_valid(form)
            else:
                return super().form_invalid(form)

        messages.add_message(
            self.request, messages.SUCCESS, "Flat Rate Plan Updated Successfully!"
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(
            FlatRatePlanUpdateView, self
        ).get_context_data(**kwargs)
        context['page_title'] = f'Update Flat Rate Plan "{self.get_object().title}"'
        context['page_short_title'] = f'Update Flat Rate Plan "{self.get_object().title}"'
        for key, value in get_flat_rate_plan_common_contexts(request=self.request).items():
            context[key] = value
        return context


@csrf_exempt
@has_dashboard_permission_required
@login_required
def delete_flat_rate_plan(request):
    return delete_simple_object(request=request, key='slug', model=FlatRatePlan, redirect_url="create_flat_rate_plan")


""" 
-------------------------------------------------------------------
                ** Plans: UserWalletTransaction ***
-------------------------------------------------------------------
"""


def get_user_wallet_transaction_common_contexts(request):
    common_contexts = get_simple_context_data(
        request=request, app_namespace=None, model_namespace="user_wallet_transaction", model=UserWalletTransaction, list_template=None, fields_to_hide_in_table=["id", "slug"]
    )
    return common_contexts


@method_decorator(dashboard_decorators, name='dispatch')
class UserWalletTransactionCreateView(CreateView):
    template_name = "user-wallet-transaction/manage.html"
    form_class = UserWalletTransactionManageForm

    def form_valid(self, form, **kwargs):
        # title = form.instance.title
        messages.add_message(
            self.request, messages.SUCCESS, "User wallet transaction created successfully!"
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("create_user_wallet_transaction")

    def get_context_data(self, **kwargs):
        context = super(
            UserWalletTransactionCreateView, self
        ).get_context_data(**kwargs)
        context['page_title'] = 'Create User Wallet Transaction'
        context['page_short_title'] = 'Create User Wallet Transaction'
        for key, value in get_user_wallet_transaction_common_contexts(request=self.request).items():
            context[key] = value
        context["update_url"] = None
        return context


@method_decorator(dashboard_decorators, name='dispatch')
class UserWalletTransactionDetailView(DetailView):
    template_name = "user-wallet-transaction/detail-common.html"

    def get_object(self):
        return get_simple_object(key='slug', model=UserWalletTransaction, self=self)

    def get_context_data(self, **kwargs):
        context = super(
            UserWalletTransactionDetailView, self
        ).get_context_data(**kwargs)
        context['page_title'] = f'User Wallet Transaction - {self.get_object().get_transaction_type_str()} Detail'
        context['page_short_title'] = f'User Wallet Transaction - {self.get_object().get_transaction_type_str()} Detail'
        for key, value in get_user_wallet_transaction_common_contexts(request=self.request).items():
            context[key] = value
        context["update_url"] = None
        return context


@method_decorator(dashboard_decorators, name='dispatch')
class UserWalletTransactionUpdateView(UpdateView):
    template_name = 'user-wallet-transaction/manage.html'
    form_class = UserWalletTransactionManageForm

    def get_object(self):
        return get_simple_object(key="slug", model=UserWalletTransaction, self=self)

    def get_success_url(self):
        return reverse("create_flat_rate_plan")

    def form_valid(self, form):
        self.object = self.get_object()
        messages.add_message(
            self.request, messages.SUCCESS, "User wallet transaction updated successfully!"
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(
            UserWalletTransactionUpdateView, self
        ).get_context_data(**kwargs)
        context['page_title'] = f'Update User Wallet Transaction "{self.get_object().get_transaction_type_str()}"'
        context['page_short_title'] = f'Update User Wallet Transaction "{self.get_object().get_transaction_type_str()}"'
        for key, value in get_user_wallet_transaction_common_contexts(request=self.request).items():
            context[key] = value
        context["update_url"] = None
        return context


@csrf_exempt
@has_dashboard_permission_required
@login_required
def delete_user_wallet_transaction(request):
    return delete_simple_object(request=request, key='slug', model=UserWalletTransaction, redirect_url="create_user_wallet_transaction")

# #........................... **** ...........................
# #........................... Post ...........................
# #........................... **** ...........................

### Post ###

def get_post_common_contexts(request):
    common_contexts = get_simple_context_data(
        request=request, app_namespace=None, model_namespace="post", model=Post,
        list_template=None, fields_to_hide_in_table=["id", "slug",'created_at','updated_at','allowed_users']
    )
    return common_contexts

class PostListView(ListView):
    template_name = "post/manage.html"
    form_class = PostManageForm

    def form_valid(self, form, **kwargs):
        # title = form.instance.title
        messages.add_message(
            self.request, messages.SUCCESS, "User post List successfully!"
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("post_list")

    def get_queryset(self):
        Post.objects.all()

    def get_context_data(self, **kwargs):
        context = super(
            PostListView, self
        ).get_context_data(**kwargs)
        context['page_title'] = 'Post List'
        context['page_short_title'] = None
        for key, value in get_post_common_contexts(request=self.request).items():
            context[key] = value
        context["create_url"] = None
        context["update_url"] = "post_update"
        return context


@method_decorator(dashboard_decorators, name='dispatch')
class PostDetailView(DetailView):
    template_name = "post/detail-common.html"

    def get_object(self):
        return get_simple_object(key='slug', model=Post, self=self)

    def get_context_data(self, **kwargs):
        context = super(
            PostDetailView, self
        ).get_context_data(**kwargs)
        context['page_title'] = f'Post - {self.get_object()} Detail'
        context['page_short_title'] = f'Post - {self.get_object()} Detail'
        for key, value in get_post_common_contexts(request=self.request).items():
            context[key] = value

        context["create_url"] = None
        context['page_title'] = 'Post List'
        context["update_url"] = "post_update"
        return context


@method_decorator(dashboard_decorators, name='dispatch')
class PostUpdateView(UpdateView):
    template_name = 'post/manage.html'
    form_class = PostManageForm

    def get_object(self):
        return get_simple_object(key="slug", model=Post, self=self)

    def get_success_url(self):
        return reverse("post_list")

    def form_valid(self, form):
        self.object = self.get_object()
        messages.add_message(
            self.request, messages.SUCCESS, "Post updated successfully!"
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(
            PostUpdateView, self
        ).get_context_data(**kwargs)
        context['page_title'] = f'Update Post "{self.get_object()}"'
        context['page_short_title'] = f'Update Post "{self.get_object()}"'
        for key, value in get_post_common_contexts(request=self.request).items():
            context[key] = value
        context["update_url"] = "post_update"
        context["create_url"] = None
        return context


@csrf_exempt
@has_dashboard_permission_required
@login_required
def delete_post(request):
    return delete_simple_object(request=request, key='slug', model=Post, redirect_url="post_list")


# ............................... *** ...............................
# ............................... FAQ ...............................
# ............................... *** ...............................
def get_faq_common_contexts(request):
    common_contexts = get_simple_context_data(
        request=request, app_namespace=None, model_namespace="faq", model=FAQ, list_template=None, fields_to_hide_in_table=["id", "slug"]
    )
    return common_contexts

@method_decorator(dashboard_decorators, name='dispatch')
class FAQCreateView(CreateView):
    template_name = "dashboard/snippets/manage.html"
    form_class = FAQManageForm

    def form_valid(self, form, **kwargs):
        question_title = form.instance.question_title
        field_qs = FAQ.objects.filter(
            question_title__iexact=question_title
        )
        result = validate_normal_form(
            field='question_title', field_qs=field_qs,
            form=form, request=self.request
        )
        if result == 1:
            return super().form_valid(form)
        else:
            return super().form_invalid(form)

    def get_success_url(self):
        return reverse("create_faq")

    def get_context_data(self, **kwargs):
        context = super(
            FAQCreateView, self
        ).get_context_data(**kwargs)
        context['page_title'] = 'Create FAQ'
        context['page_short_title'] = 'Create FAQ'
        for key, value in get_faq_common_contexts(request=self.request).items():
            context[key] = value
        return context


@method_decorator(dashboard_decorators, name='dispatch')
class FAQDetailView(DetailView):
    template_name = "dashboard/snippets/detail-common.html"

    def get_object(self):
        return get_simple_object(key='slug', model=FAQ, self=self)

    def get_context_data(self, **kwargs):
        context = super(
            FAQDetailView, self
        ).get_context_data(**kwargs)
        context['page_title'] = f'FAQ - {self.get_object().question_title} Detail'
        context['page_short_title'] = f'FAQ - {self.get_object().question_title} Detail'
        for key, value in get_faq_common_contexts(request=self.request).items():
            context[key] = value
        return context


@method_decorator(dashboard_decorators, name='dispatch')
class FAQUpdateView(UpdateView):
    template_name = 'dashboard/snippets/manage.html'
    form_class = FAQManageForm

    def get_object(self):
        return get_simple_object(key="slug", model=FAQ, self=self)

    def get_success_url(self):
        return reverse("create_faq")

    def form_valid(self, form):
        self.object = self.get_object()
        question_title = form.instance.question_title
        if not self.object.question_title == question_title:
            field_qs = FAQ.objects.filter(
                question_title__iexact=question_title
            )
            result = validate_normal_form(
                field='question_title', field_qs=field_qs,
                form=form, request=self.request
            )
            if result == 1:
                return super().form_valid(form)
            else:
                return super().form_invalid(form)

        messages.add_message(
            self.request, messages.SUCCESS, "FAQ Updated Successfully!"
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(
            FAQUpdateView, self
        ).get_context_data(**kwargs)
        context['page_title'] = f'Update FAQ "{self.get_object().question_title}"'
        context['page_short_title'] = f'Update FAQ "{self.get_object().question_title}"'
        for key, value in get_faq_common_contexts(request=self.request).items():
            context[key] = value
        return context


@csrf_exempt
@has_dashboard_permission_required
@login_required
def delete_faq(request):
    return delete_simple_object(request=request, key='slug', model=FAQ, redirect_url="create_faq")
