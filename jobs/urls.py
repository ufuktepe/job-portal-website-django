from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("displayprofile/<int:user_id>", views.display_profile, name="display_profile"),
    path("editprofile/<int:user_id>", views.edit_profile, name="edit_profile"),
    path("resume/<str:username>", views.resume, name="resume"),
    path("editresume/<str:field>", views.edit_resume, name="edit_resume"),
    path("addexperience", views.add_experience, name="add_experience"),
    path("editexperience/<int:pk>", views.edit_experience, name="edit_experience"),
    path("addeducation", views.add_education, name="add_education"),
    path("editeducation/<int:pk>", views.edit_education, name="edit_education"),
    path("removeitem/<str:field_id>", views.remove_item, name="remove_item"),
    path("postjob", views.post_job, name="post_job"),
    path("displayjobpost/<int:job_post_id>", views.display_job_post, name="display_job_post"),
    path("editjobpost/<int:job_post_id>", views.edit_job_post, name="edit_job_post"),
    path("applyjob/<int:job_post_id>", views.apply_job, name="apply_job"),
    path("appliedjobs/<str:status>", views.applied_jobs, name="applied_jobs"),
    path("postedjobs/<str:status>", views.posted_jobs, name="posted_jobs"),
    path("closejobpost/<int:job_post_id>", views.close_job_post, name="close_job_post"),
    path("search", views.search, name='search'),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register/<str:profile_type>", views.register, name="register")
]