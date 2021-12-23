from django.urls import path
from .views import UserListView, UserDetailView

urlpatterns = [
    # ==============================*** User URLS ***==============================
    path("list/", UserListView.as_view(), name="user_list"),
    path("<slug>/detail/", UserDetailView.as_view(), name="user_detail"),
]
