from django.urls import path
from . import views
urlpatterns=[path('partners/public-map/',views.public_partner_map_api),path('partners/',views.partner_list),path('partners/import/',views.import_excel),path('partners/<int:pk>/coordinates/',views.save_coordinates),path('content/',views.content_feed)]


# === PUBLIC MEMBER REGISTER URL ===
from django.urls import path as _member_path
from .views import member_register as _member_register

urlpatterns += [
    _member_path(
        "member-register/",
        _member_register,
        name="member_register",
    ),
]


# === PUBLIC CSRF COOKIE URL ===
from .views import csrf_cookie as _csrf_cookie

urlpatterns += [
    _member_path(
        "csrf/",
        _csrf_cookie,
        name="csrf_cookie",
    ),
]


# === PUBLIC LOGIN URLS ===
from .views import (
    member_login as _member_login,
    member_logout as _member_logout,
    member_session as _member_session,
)

urlpatterns += [
    _member_path(
        "member-login/",
        _member_login,
        name="member_login",
    ),
    _member_path(
        "member-logout/",
        _member_logout,
        name="member_logout",
    ),
    _member_path(
        "member-session/",
        _member_session,
        name="member_session",
    ),
]


# === MEMBER ACCOUNT RECOVERY URLS ===
# Append this block to backend/partners/urls.py

from .views import (
    member_find_id as _member_find_id,
    member_reset_password as _member_reset_password,
)

urlpatterns += [
    _member_path("member-find-id/", _member_find_id, name="member_find_id"),
    _member_path(
        "member-reset-password/",
        _member_reset_password,
        name="member_reset_password",
    ),
]


from . import payment_views
urlpatterns += [
    _member_path('payments/success/', payment_views.payment_success, name='payment_success'),
    _member_path('payments/fail/', payment_views.payment_fail, name='payment_fail'),
]

from .views import member_mypage, member_self_withdraw
urlpatterns += [_member_path('member-mypage/',member_mypage,name='member_mypage'),_member_path('member-withdraw/',member_self_withdraw,name='member_self_withdraw')]
