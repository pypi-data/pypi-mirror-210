from django.urls import path

from NEMO_rs2_access import views

urlpatterns = [
    # Override user preferences to add default project selection
    path("user_preferences/", views.custom_user_preferences, name="user_preferences"),

    path("rs2_sync_readers/", views.rs2_sync_reader, name="rs2_sync_readers"),
    path("rs2_sync_access/", views.rs2_sync_access, name="rs2_sync_access"),
]
