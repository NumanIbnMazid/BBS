from django.views.generic import CreateView, DetailView, UpdateView, ListView, View
from bbs.decorators import has_dashboard_permission_required
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.contrib import messages
from users.models import User
from bbs.helpers import (
    validate_normal_form, get_simple_context_data, get_simple_object, delete_simple_object, user_has_permission
)
from django.contrib.auth import get_user_model


dashboard_decorators = [login_required, has_dashboard_permission_required]


""" 
-------------------------------------------------------------------
                           ** User ***
-------------------------------------------------------------------
"""


def get_user_common_contexts(request):
    common_contexts = get_simple_context_data(
        request=request, app_namespace='users', model_namespace="user", model=get_user_model(), list_template="users/list.html", fields_to_hide_in_table=["id", "slug", "password", "updated_at", "is_active", "date_joined", "last_login", "groups", "user_permissions"]
    )
    common_contexts.update(
        {
            "create_url": None,
            "update_url": None,
            "delete_url": None,
        }
    )
    return common_contexts


@method_decorator(dashboard_decorators, name='dispatch')
class UserListView(ListView):
    template_name = "dashboard/snippets/list-common.html"

    def get_queryset(self):
        return get_user_model().objects.all()
    
    def get_context_data(self, **kwargs):
        context = super(
            UserListView, self
        ).get_context_data(**kwargs)
        context['page_title'] = 'User List'
        context['page_short_title'] = 'User List'
        for key, value in get_user_common_contexts(request=self.request).items():
            context[key] = value
        return context


@method_decorator(dashboard_decorators, name='dispatch')
class UserDetailView(DetailView):
    template_name = "users/detail.html"

    def get_object(self):
        return get_simple_object(key='slug', model=get_user_model(), self=self)

    def get_context_data(self, **kwargs):
        context = super(
            UserDetailView, self
        ).get_context_data(**kwargs)
        context['page_title'] = f'User Detail'
        context['page_short_title'] = f'User Detail'
        for key, value in get_user_common_contexts(request=self.request).items():
            context[key] = value
        return context
