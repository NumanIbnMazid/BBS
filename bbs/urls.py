from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
import debug_toolbar
# from django.views.static import serve
from . import views
from django.conf.urls.i18n import i18n_patterns
from  django.utils.translation import gettext_lazy as _

""" User Panel Views """
from .views import (
    HomeView, create_husband
)
""" Dashboard Views """

from .views import (
    DashboardView, 
    # Thread Template Views
    ThreadDetailTemplateView,
    # Thread Views
    ThreadCreateView, ThreadUpdateView, ThreadDetailView, delete_thread,
    # Point Plan Views
    PointPlanCreateView, PointPlanUpdateView, PointPlanDetailView, delete_point_plan,
    # Flat Rate Plan Views
    FlatRatePlanCreateView, FlatRatePlanUpdateView, FlatRatePlanDetailView, delete_flat_rate_plan,
    # User Wallet Transaction
    UserWalletTransactionCreateView, UserWalletTransactionUpdateView, UserWalletTransactionDetailView,
    delete_user_wallet_transaction, PostListView, PostDetailView,delete_post,PostUpdateView,
    FAQCreateView,FAQDetailView, FAQUpdateView, delete_faq
)


USER_PANEL_URLS = [
    path("", HomeView.as_view(), name="home"),
    path("thread/template/", ThreadDetailTemplateView.as_view(), name="thread_template"),
    # -----------------------------*** Thread Detail ***-----------------------------
    # -----------------------------*** User ***-----------------------------
    #   -----------------------------*** *** ***-----------------------------
    path('user-profile/', views.user_profile, name="user_profile"),
    path('user-profile-update/<slug>/', views.user_profile_update, name="user_profile_update"),

    # -----------------------------*** Husband ***-----------------------------
    #   -----------------------------*** *** ***-----------------------------
    path('create-husband/', views.create_husband, name='create_husband'),
    path('husband-details/<slug>/', views.husband_details, name='husband_details'),
    path('husband-update/<slug>/', views.husband_update, name='husband_update'),

    # -----------------------------*** Post ***-----------------------------
    #   -----------------------------*** *** ***-----------------------------
    path('create-post/', views.create_post, name='create_post'),
    path('post-details/<slug>/', views.post_details, name='post_details'),
    # path('<str:slug>/', views.post_details, name='post_details'),
    path('post-update/<slug>/', views.post_update, name='update_post'),
    path('post_delete/<slug>/', views.post_delete, name='post_delete'),
    path('comment-reply/<id>/', views.comment_reply, name='comment_reply'),
    # -----------------------------*** Post list ***------------------------
    #   -----------------------------*** *** ***-----------------------------
    path('post_list/<slug>/', views.post_list, name='post_list'),
    path('faq-list/', views.faq_list, name='faq_list'),
]

DASHBOARD_PANEL_URLS = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    # ==============================*** UTILS URLS ***==============================
    path("utils/", include(("utils.urls", "utils"), namespace="utils")),
    # ==============================*** User URLS ***==============================
    path("users/", include(("users.urls", "users"), namespace="users")),
    # ==============================*** Thread URLS ***==============================
    path("create-thread/", ThreadCreateView.as_view(), name="create_thread"),
    path("update-thread/<slug>/", ThreadUpdateView.as_view(), name="update_thread"),
    path("thread/<slug>/detail/", ThreadDetailView.as_view(), name="thread_detail"),
    path("delete/thread/", delete_thread, name="delete_thread"),
    # ==============================*** Point Plan URLS ***==============================
    path("create-point-plan/", PointPlanCreateView.as_view(), name="create_point_plan"),
    path("update-point-plan/<slug>/", PointPlanUpdateView.as_view(), name="update_point_plan"),
    path("point-plan/<slug>/detail/", PointPlanDetailView.as_view(), name="point_plan_detail"),
    path("delete/point-plan/", delete_point_plan, name="delete_point_plan"),
    # ==============================*** Flat Rate Plan URLS ***==============================
    path("create-flat-rate-plan/", FlatRatePlanCreateView.as_view(), name="create_flat_rate_plan"),
    path("update-flat-rate-plan/<slug>/", FlatRatePlanUpdateView.as_view(), name="update_flat_rate_plan"),
    path("flat-rate-plan/<slug>/detail/", FlatRatePlanDetailView.as_view(), name="flat_rate_plan_detail"),
    path("delete/flat-rate-plan/", delete_flat_rate_plan, name="delete_flat_rate_plan"),
    # ==============================*** User Wallet Transaction URLS ***==============================
    path("create-user-wallet-transaction/", UserWalletTransactionCreateView.as_view(), name="create_user_wallet_transaction"),
    # path("update-user-wallet-transaction/<slug>/", UserWalletTransactionUpdateView.as_view(), name="update_user_wallet_transaction"),
    path("user-wallet-transaction/<slug>/detail/", UserWalletTransactionDetailView.as_view(), name="user_wallet_transaction_detail"),
    path("delete/user-wallet-transaction/", delete_user_wallet_transaction, name="delete_user_wallet_transaction"),
    # ==============================*** Post URLS ***==============================
    path("post/list/", PostListView.as_view(), name="post_list"),
    path("post/<slug>/update/", PostUpdateView.as_view(), name="post_update"),
    path("post/<slug>/detail/",PostDetailView.as_view(), name="post_detail"),
    path("delete/cv/", delete_post, name="delete_post"),
    # ==============================*** FAQ URLS ***==============================
    path("create-faq", FAQCreateView.as_view(), name="create_faq"),
    path("faq-update/<slug>/", FAQUpdateView.as_view(), name="update_faq"),
    path("faq/<slug>/detail/", FAQDetailView.as_view(), name="faq_detail"),
    path("delete/faq/", delete_faq, name="delete_faq"),
]
urlpatterns = [
    # For handling Static Files in Debug False Mode
    # url(r'^media/(?P<path>.*)$', serve,
    #     {'document_root': settings.MEDIA_ROOT}),
    # url(r'^static/(?P<path>.*)$', serve,
    #     {'document_root': settings.STATIC_ROOT}),
    # Application URLS
    path(_('admin/'), admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path("select2/", include("django_select2.urls")),
    path('__debug__/', include(debug_toolbar.urls)),
] + USER_PANEL_URLS + DASHBOARD_PANEL_URLS


urlpatterns += i18n_patterns(
    path("", DashboardView.as_view(), name="translation")
    # path('', include('lang.urls', namespace='lang'))
)
if settings.DEBUG:
    urlpatterns = urlpatterns + \
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + \
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
