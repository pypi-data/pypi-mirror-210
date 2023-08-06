from NEMO.urls import router
from django.urls import path, re_path

from NEMO_user_details import api
from NEMO_user_details.views import email, users

router.register(r"users_with_details", api.UserWithDetailsViewSet)

urlpatterns = [
    # Override modify user page to add user details fields
    re_path(
        r"^user/(?P<user_id>\d+|new)/",
        users.create_or_modify_user_and_details,
        name="create_or_modify_user_and_details",
    ),
    # Override broadcast email to add new search by groups
    path("email_broadcast/", email.email_broadcast, name="email_broadcast"),
    re_path(
        r"^email_broadcast/(?P<audience>tool|area|account|project|user|group)/$",
        email.email_broadcast,
        name="email_broadcast",
    ),
]
