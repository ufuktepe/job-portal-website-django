from django.contrib import admin

from .models import User, Profile, Employer, JobSeeker, Resume, Experience, JobPost, JobApplication, Education

# Register your models here.
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Employer)
admin.site.register(JobSeeker)
admin.site.register(Resume)
admin.site.register(Experience)
admin.site.register(JobPost)
admin.site.register(JobApplication)
admin.site.register(Education)
