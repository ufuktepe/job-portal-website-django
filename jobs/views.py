import json
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.forms import ModelForm
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from . import util
from .models import User, Employer, Experience, JobPost, JobApplication, Education


class AddExperienceForm(ModelForm):
    """
    ModelForm for creating a new job experience.
    """
    class Meta:
        model = Experience
        fields = ["job_title", "company_name", "location", "start_month",
                  "start_year", "end_month", "end_year", "current_job", "description"]

        widgets = {
            "job_title": forms.TextInput(attrs={"class": "edit-textarea"}),
            "company_name": forms.TextInput(attrs={"class": "edit-textarea"}),
            "location": forms.TextInput(attrs={"class": "edit-textarea"}),
            "start_month": forms.Select(attrs={"class": "dropdown-field"}),
            "start_year": forms.Select(attrs={"class": "dropdown-field"}),
            "end_month": forms.Select(attrs={"class": "dropdown-field"}),
            "end_year": forms.Select(attrs={"class": "dropdown-field"}),
            "description": forms.Textarea(attrs={"class": "edit-textarea large-textarea"})
        }


class AddEducationForm(ModelForm):
    """
    ModelForm for creating a new education.
    """
    class Meta:
        model = Education
        fields = ["school", "degree", "field_of_study", "start_month",
                  "start_year", "end_month", "end_year"]

        widgets = {
            "school": forms.TextInput(attrs={"class": "edit-textarea"}),
            "degree": forms.Select(attrs={"class": "edit-textarea"}),
            "field_of_study": forms.TextInput(attrs={"class": "edit-textarea"}),
            "start_month": forms.Select(attrs={"class": "dropdown-field"}),
            "start_year": forms.Select(attrs={"class": "dropdown-field"}),
            "end_month": forms.Select(attrs={"class": "dropdown-field"}),
            "end_year": forms.Select(attrs={"class": "dropdown-field"})
        }


class EmployerForm(ModelForm):
    """
    ModelForm for employer profiles.
    """
    class Meta:
        model = Employer
        fields = ["company_name", "num_of_employees", "location", "about"]

        widgets = {
            "company_name": forms.TextInput(attrs={"class": "edit-textarea"}),
            "num_of_employees": forms.NumberInput(attrs={"class": "edit-textarea"}),
            "location": forms.TextInput(attrs={"class": "edit-textarea"}),
            "about": forms.Textarea(attrs={"class": "edit-textarea large-textarea"})
        }


class JobPostForm(ModelForm):
    """
    ModelForm for creating a new job post.
    """
    class Meta:
        model = JobPost
        fields = ["industry", "title", "job_type", "location", "min_salary", "max_salary", "description"]

        widgets = {
            "industry": forms.Select(attrs={"class": "dropdown-field-extend"}),
            "title": forms.TextInput(attrs={"class": "edit-textarea"}),
            "job_type": forms.Select(attrs={"class": "dropdown-field-extend"}),
            "location": forms.TextInput(attrs={"class": "edit-textarea"}),
            "min_salary": forms.NumberInput(attrs={"class": "edit-textarea"}),
            "max_salary": forms.NumberInput(attrs={"class": "edit-textarea"}),
            "description": forms.Textarea(attrs={"class": "edit-textarea large-textarea"})
        }


def index(request):
    """
    Default route that returns active job postings.
    """
    return render(request, "jobs/index.html", {"job_posts": JobPost.objects.filter(active=True)})


def display_profile(request, user_id):
    """
    Displays the profile page of an employer.
    """
    profile_owner = False
    # Get the user
    user = User.objects.get(pk=user_id)
    # Get the profile
    profile = util.get_profile_from_user(user)

    # Check if the current user is the owner of the profile
    if request.user.is_authenticated and user == request.user:
        profile_owner = True

    if profile.profile_type == "employer":
        # Get the Employer object of the profile
        employer = Employer.objects.get(profile=profile)

        # Pre-populate the form
        form = EmployerForm(initial={"company_name": employer.company_name,
                                     "num_of_employees": employer.num_of_employees,
                                     "location": employer.location,
                                     "about": employer.about})
    else:
        # Display 404 page not found if the profile is not an Employer profile
        return render(request, "jobs/notfound.html", {"message": "Profile does not exist."})

    # Render the profile page with the pre-populated form and employer object
    return render(request, "jobs/profile.html",
                  {"form": form, "employer": employer, "profile_owner": profile_owner, "error_msg": None})


@login_required
def edit_profile(request, user_id):
    """
    Edits the profile page of an employer and redirects to the profile page.
    """
    if request.method == "POST":

        # Get the user
        user = User.objects.get(pk=user_id)
        # Get the profile
        profile = util.get_profile_from_user(user)

        if profile.profile_type == "employer":
            # Get the Employer object of the profile
            employer = Employer.objects.get(profile=profile)

            # Check if current user is the owner of the profile
            if not request.user.is_authenticated or user != request.user:
                return render(request, "jobs/profile.html",
                              {"form": EmployerForm(),
                               "employer": employer,
                               "profile_owner": False,
                               "error_msg": "Permission Denied"})

            # Fetch the form
            form = EmployerForm(request.POST)

            if form.is_valid():
                # Update the employer object
                employer.company_name = form.cleaned_data["company_name"]
                employer.num_of_employees = form.cleaned_data["num_of_employees"]
                employer.location = form.cleaned_data["location"]
                employer.about = form.cleaned_data["about"]
                employer.save()
            else:
                # If form is invalid, return the profile page with the current form
                return render(request, "jobs/profile.html",
                              {"form": form,
                               "employer": employer,
                               "profile_owner": True,
                               "error_msg": None})

        else:
            # Display 404 page not found if the profile is not an Employer profile
            return render(request, "jobs/notfound.html", {"message": "Profile does not exist."})

    # Redirect to the profile page
    return HttpResponseRedirect(reverse("display_profile", args=(user_id,)))


def resume(request, username):
    """
    Displays the resume page.
    """
    resume_owner = False

    # Get the resume object
    resume = util.get_resume_from_username(username)

    if resume:
        # Get the experience and education objects
        experience, education = util.get_data_from_resume(resume)

        # Check if the current user is the owner of the resume
        if resume.profile.user == request.user:
            resume_owner = True
    else:
        # Display 404 page not found if resume does not exist
        return render(request, "jobs/notfound.html", {"message": "Resume does not exist."})

    # Return the resume page with a new form
    return render(request, "jobs/resume.html", {"resume": resume,
                                                "experience": experience,
                                                "education": education,
                                                "add_experience_form": AddExperienceForm(),
                                                "add_education_form": AddEducationForm(),
                                                "add_experience_error": None,
                                                "add_education_error": None,
                                                "resume_owner": resume_owner})


def edit_resume(request, field):
    """
    Edits a resume field. Then returns the serialized data of the object.
    """
    if request.method == "PUT":
        # Get the resume object
        resume = util.get_resume_from_user(request.user)

        if resume:
            # Get the form data
            data = json.loads(request.body)
            updated_content = None
            if data.get("content") is not None:
                # Update the resume
                if field == "address":
                    resume.address = data["content"]
                    updated_content = resume.address
                elif field == "summary":
                    resume.summary = data["content"]
                    updated_content = resume.summary
                elif field == "skills":
                    resume.skills = data["content"]
                    updated_content = resume.skills
                resume.save()

            # # Return updated_content
            return JsonResponse({"content": updated_content})

        else:
            # Display 404 page not found if resume does not exist
            return JsonResponse({"error": "Resume not found."}, status=400)

    # Edit must be via PUT
    else:
        return JsonResponse({"error": "PUT request required."}, status=400)


def add_experience(request):
    """
    Creates a new experience object.
    """
    if request.method == "POST":
        # Fetch the form
        form = AddExperienceForm(request.POST)

        # Get the resume object
        resume = util.get_resume_from_user(request.user)

        if resume:
            # Check if form is valid
            if form.is_valid():
                # Get the form data
                job_title = form.cleaned_data["job_title"]
                company_name = form.cleaned_data["company_name"]
                location = form.cleaned_data["location"]
                start_month = form.cleaned_data["start_month"]
                start_year = form.cleaned_data["start_year"]
                end_month = form.cleaned_data["end_month"]
                end_year = form.cleaned_data["end_year"]
                current_job = form.cleaned_data["current_job"]
                description = form.cleaned_data["description"]

                # Check if the date range is valid
                if util.is_date_range_valid(start_month, start_year, end_month, end_year, current_job):
                    # Set the end month and year to None if current job
                    if current_job:
                        end_month = None
                        end_year = None

                    # Create a new Experience object
                    experience = Experience(job_title=job_title,
                                            company_name=company_name,
                                            location=location,
                                            start_month=start_month,
                                            start_year=start_year,
                                            end_month=end_month,
                                            end_year=end_year,
                                            description=description,
                                            current_job=current_job,
                                            resume=resume)

                    experience.save()

                    # Redirect to the resume page
                    return HttpResponseRedirect(reverse("resume", args=(request.user.username,)))
                else:
                    # Get the experience and education objects
                    experience, education = util.get_data_from_resume(resume)
                    # Render the resume page with an error
                    return render(request, "jobs/resume.html",
                                  {"resume": resume,
                                   "experience": experience,
                                   "education": education,
                                   "add_experience_form": form,
                                   "add_education_form": AddEducationForm(),
                                   "add_experience_error": "Please enter a valid date range.",
                                   "add_education_error": None,
                                   "resume_owner": True})

            # If form is invalid, return the resume page with the current form
            else:
                # Get the experience and education objects
                experience, education = util.get_data_from_resume(resume)
                # Render the resume page with the current form
                return render(request, "jobs/resume.html", {"resume": resume,
                                                            "experience": experience,
                                                            "education": education,
                                                            "add_experience_form": form,
                                                            "add_education_form": AddEducationForm(),
                                                            "add_experience_error": None,
                                                            "add_education_error": None,
                                                            "resume_owner": True})

        else:
            # Display 404 page not found
            return render(request, "jobs/notfound.html", {"message": "Resume does not exist."})

    # If request is not a post request, redirect to the resume page
    return HttpResponseRedirect(reverse("resume", args=(request.user.username,)))


def edit_experience(request, pk):
    """
    Edits an existing experience object.
    """
    if request.method != "PUT":
        # PUT method is required
        return JsonResponse({"error": "PUT request required."}, status=400)

    # Get the form data
    data = json.loads(request.body)

    # Check whether the experience object exists
    if Experience.objects.filter(pk=pk).exists():
        experience = Experience.objects.get(pk=pk)
        # Edit experience object
        experience.job_title = data["jobTitle"]
        experience.company_name = data["companyName"]
        experience.location = data["loc"]
        experience.start_month = data["startMonth"]
        experience.start_year = data["startYear"]
        experience.current_job = data["currentJob"]

        # Set the end date to None if this is a current job
        if experience.current_job:
            experience.end_month = None
            experience.end_year = None
        else:
            # Update the end date if this is not a current job
            experience.end_month = data["endMonth"]
            experience.end_year = data["endYear"]

        experience.description = data["desc"]
        experience.save()
    else:
        # Experience not found
        return JsonResponse({"error": "Experience object not found."}, status=404)

    # Return updated data
    return JsonResponse({"job_title": experience.job_title,
                         "company_name": experience.company_name,
                         "location": experience.location,
                         "start_month": experience.start_month,
                         "start_year": experience.start_year,
                         "end_month": experience.end_month,
                         "end_year": experience.end_year,
                         "current_job": experience.current_job,
                         "description": experience.description})


def add_education(request):
    """
    Creates a new education object.
    """
    if request.method == "POST":
        # Fetch the form
        form = AddEducationForm(request.POST)

        # Get the resume object
        resume = util.get_resume_from_user(request.user)

        if resume:
            # Check if form is valid
            if form.is_valid():
                # Get the form data
                school = form.cleaned_data["school"]
                degree = form.cleaned_data["degree"]
                field_of_study = form.cleaned_data["field_of_study"]
                start_month = form.cleaned_data["start_month"]
                start_year = form.cleaned_data["start_year"]
                end_month = form.cleaned_data["end_month"]
                end_year = form.cleaned_data["end_year"]

                # Check if the date range is valid
                if util.is_date_range_valid(start_month, start_year, end_month, end_year, False):
                    # Create a new Education object
                    education = Education(school=school,
                                          degree=degree,
                                          field_of_study=field_of_study,
                                          start_month=start_month,
                                          start_year=start_year,
                                          end_month=end_month,
                                          end_year=end_year,
                                          resume=resume)

                    education.save()

                    # Redirect to the resume page
                    return HttpResponseRedirect(reverse("resume", args=(request.user.username,)))
                else:
                    # Get the experience and education objects
                    experience, education = util.get_data_from_resume(resume)
                    # Render the resume page with an error message for the date range
                    return render(request, "jobs/resume.html",
                                  {"resume": resume,
                                   "experience": experience,
                                   "education": education,
                                   "add_experience_form": AddExperienceForm(),
                                   "add_education_form": form,
                                   "add_experience_error": None,
                                   "add_education_error": "Please enter a valid date range.",
                                   "resume_owner": True})

            # If form is invalid, return the resume page with the current form
            else:
                # Get the experience and education objects
                experience, education = util.get_data_from_resume(resume)
                # Render the resume page with the current form
                return render(request, "jobs/resume.html", {"resume": resume,
                                                            "experience": experience,
                                                            "education": education,
                                                            "add_experience_form": AddExperienceForm(),
                                                            "add_education_form": form,
                                                            "add_experience_error": None,
                                                            "add_education_error": None,
                                                            "resume_owner": True})

        else:
            # Display 404 page not found
            return render(request, "jobs/notfound.html", {"message": "Resume does not exist."})

    # If request is not a post request, redirect to the resume page
    return HttpResponseRedirect(reverse("resume", args=(request.user.username,)))


def edit_education(request, pk):
    """
    Edits an existing education object.
    """
    if request.method != "PUT":
        # PUT method is required
        return JsonResponse({"error": "PUT request required."}, status=400)

    # Get the form data
    data = json.loads(request.body)

    # Check whether the education object exists
    if Education.objects.filter(pk=pk).exists():
        education = Education.objects.get(pk=pk)
        # Edit education object
        education.school = data["school"]
        education.degree = data["degree"]
        education.field_of_study = data["fieldOfStudy"]
        education.start_month = data["startMonth"]
        education.start_year = data["startYear"]
        education.end_month = data["endMonth"]
        education.end_year = data["endYear"]
        education.save()
    else:
        # Education not found
        return JsonResponse({"error": "Education object not found."}, status=404)

    # Return updated data
    return JsonResponse({"school": education.school,
                         "degree": education.degree,
                         "field_of_study": education.field_of_study,
                         "start_month": education.start_month,
                         "start_year": education.start_year,
                         "end_month": education.end_month,
                         "end_year": education.end_year})


def remove_item(request, field_id):
    """
    Removes an Experience or Education object.
    """
    # Decompose the field id to identify the object type and primary key
    field = field_id.split('_')[0]
    pk = field_id.split('_')[1]

    if request.method == "PUT":
        if field == "experience":
            # Attempt to delete the experience object
            if not util.delete_row(Experience, pk):
                return JsonResponse({"message": "Experience does not exist."}, status=404)

            # Return status 200
            return JsonResponse({"message": "Experience deleted successfully."}, status=200)

        elif field == "education":
            # Attempt to delete the education object
            if not util.delete_row(Education, pk):
                return JsonResponse({"message": "Education does not exist."}, status=404)

            # Return status 200
            return JsonResponse({"message": "Education deleted successfully."}, status=200)

        # If field is not education or experience return 400 bad request
        return JsonResponse({"message": "Unknown field."}, status=400)

    # PUT request required
    else:
        return JsonResponse({"message": "PUT request required."}, status=400)


def post_job(request):
    """
    Creates a job post. Then redirects to the index page.
    """
    if request.method == "POST":
        # Fetch the form
        form = JobPostForm(request.POST)

        # Check if form is valid
        if form.is_valid():
            # Get the form data
            industry = form.cleaned_data["industry"]
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            job_type = form.cleaned_data["job_type"]
            location = form.cleaned_data["location"]
            min_salary = form.cleaned_data["min_salary"]
            max_salary = form.cleaned_data["max_salary"]

            # Validate the salary range
            if not util.is_salary_range_valid(min_salary, max_salary):
                return render(request, "jobs/create.html",
                              {"form": form, "error_msg": "Please enter a valid salary range."})

            # Get the profile object
            profile = util.get_profile_from_user(request.user)

            try:
                # Get the employer object
                employer = profile.employer
            except AttributeError:
                # Render the create page with a permission denied error
                return render(request, "jobs/create.html",
                              {"form": JobPostForm(), "error_msg": "Permission Denied."})

            # Create a new JobPost object
            new_job_post = JobPost(industry=industry,
                                   title=title,
                                   description=description,
                                   job_type=job_type,
                                   location=location,
                                   min_salary=min_salary,
                                   max_salary=max_salary,
                                   employer=employer)
            new_job_post.save()

            # Redirect to the index page
            return HttpResponseRedirect(reverse("index"))

        # If form is invalid, render the post job page with the current form
        else:
            return render(request, "jobs/create.html", {"form": form, "error_msg": None})

    # If request is not a post request, render the create page with a new form
    return render(request, "jobs/create.html", {"form": JobPostForm(), "error_msg": None})


def display_job_post(request, job_post_id):
    """
    Displays job post based on the job_post_id.
    """
    # Get the job post and render the job post page
    if JobPost.objects.filter(pk=job_post_id):
        job_post = JobPost.objects.get(pk=job_post_id)
        # Get the job applications
        applications = JobApplication.objects.filter(job_post=job_post)
        # Check if the current user has already applied to the job
        applied = False
        job_seeker = util.get_profile_type_obj(request.user, profile_type="job_seeker")
        if job_seeker and JobApplication.objects.filter(applicant=job_seeker, job_post=job_post).exists():
            applied = True

        # Render the job post page
        return render(request, "jobs/jobpost.html",
                      {"job_post": JobPost.objects.get(pk=job_post_id),
                       "form": JobPostForm(instance=job_post),
                       "show_edit_mode": False,
                       "applied": applied,
                       "applications": applications,
                       "error_msg": None})
    else:
        # Display 404 page not found
        return render(request, "jobs/notfound.html", {"message": "Requested job post does not exist."})


@login_required
def edit_job_post(request, job_post_id):
    """
    Edits an existing job post.
    """
    # Check if the job post exists
    if JobPost.objects.filter(pk=job_post_id).exists():

        job_post = JobPost.objects.get(pk=job_post_id)

        # Get the job applications
        applications = JobApplication.objects.filter(job_post=job_post)
        
        if request.method == "POST":
            # Fetch the form
            form = JobPostForm(request.POST)

            # Check if form is valid
            if form.is_valid():
                
                # Get the job post
                job_post = JobPost.objects.get(pk=job_post_id)
                
                # Get the form data
                min_salary = form.cleaned_data["min_salary"]
                max_salary = form.cleaned_data["max_salary"]

                # Check if the salary range is valid
                if not util.is_salary_range_valid(min_salary, max_salary):
                    return render(request, "jobs/jobpost.html",
                                  {"job_post": JobPost.objects.get(pk=job_post_id),
                                   "form": form,
                                   "show_edit_mode": True,
                                   "applied": False,
                                   "applications": applications,
                                   "error_msg": "Please enter a valid salary range."})

                # Update the job post object with the form data
                job_post.industry = form.cleaned_data["industry"]
                job_post.title = form.cleaned_data["title"]
                job_post.description = form.cleaned_data["description"]
                job_post.job_type = form.cleaned_data["job_type"]
                job_post.location = form.cleaned_data["location"]
                job_post.min_salary = form.cleaned_data["min_salary"]
                job_post.max_salary = form.cleaned_data["max_salary"]

                job_post.save()

                # Redirect to the job post page
                return HttpResponseRedirect(reverse("display_job_post", args=(job_post_id,)))

            # If form is invalid, render the job post page with the current form
            else:
                return render(request, "jobs/jobpost.html", 
                              {"job_post": JobPost.objects.get(pk=job_post_id),
                               "form": form,
                               "show_edit_mode": True,
                               "applied": False,
                               "applications": applications,
                               "error_msg": None})

        # If request is not a put request, render the job post page
        return render(request, "jobs/jobpost.html",
                      {"job_post": JobPost.objects.get(pk=job_post_id),
                       "form": JobPostForm(instance=JobPost.objects.get(pk=job_post_id)),
                       "show_edit_mode": False,
                       "applied": False,
                       "applications": applications,
                       "error_msg": None})

    else:
        # Display 404 page not found
        return render(request, "jobs/notfound.html", {"message": "Requested job post does not exist."})


def apply_job(request, job_post_id):
    """
    Creates/cancels a job application.
    """
    # Check if tje job post exists
    if JobPost.objects.filter(pk=job_post_id):

        if request.method == "PUT":
            # Get the job post based on job_post_id
            job_post = JobPost.objects.get(pk=job_post_id)

            applied = False
            # Get the job seeker object using the current user
            job_seeker = util.get_profile_type_obj(request.user, profile_type="job_seeker")

            if job_seeker:
                # Check if there exists a Job Application object for the user
                if JobApplication.objects.filter(applicant=job_seeker, job_post=job_post).exists():
                    # Delete the job application
                    JobApplication.objects.get(applicant=job_seeker, job_post=job_post).delete()
                else:
                    # Create job application
                    job_application = JobApplication(applicant=job_seeker, job_post=job_post)
                    job_application.save()
                    applied = True

            # Get the applications for this job post
            applications = JobApplication.objects.filter(job_post=job_post)

            # Return the number of applications (applicants) and a boolean value for indicating
            # job application or cancellation of application
            return JsonResponse({"applicants": len(applications), "applied": applied})

        # PUT request required
        else:
            return JsonResponse({"error": "PUT request required."}, status=400)

    else:
        # Display 404 page not found
        return JsonResponse({"error": "Job post does not exist."}, status=404)


def applied_jobs(request, status):
    """
    Displays open or closed job posts that a job seeker has applied.
    """
    # Get the job seeker
    job_seeker = util.get_profile_type_obj(request.user, profile_type="job_seeker")

    # Get the job applications
    if status == "open":
        job_applications = JobApplication.objects.filter(applicant=job_seeker, job_post__active=True)
    else:
        job_applications = JobApplication.objects.filter(applicant=job_seeker, job_post__active=False)

    # Create a list of job posts from job applications
    job_posts = list()
    for job_application in job_applications:
        job_posts.append(job_application.job_post)

    # Render the index page with the found job posts
    return render(request, "jobs/index.html", {"job_posts": job_posts})


def posted_jobs(request, status):
    """
    Displays open or closed job posts of an employer.
    """
    # Get the employer
    employer = util.get_profile_type_obj(request.user, profile_type="employer")

    # Get the job applications
    if status == "open":
        job_posts = JobPost.objects.filter(employer=employer, active=True)
    else:
        job_posts = JobPost.objects.filter(employer=employer, active=False)

    # Render the index page with the found job posts
    return render(request, "jobs/index.html", {"job_posts": job_posts})


@login_required
def close_job_post(request, job_post_id):
    """
    Deactivates the job post.
    """
    # Get the job post object
    try:
        job_post = JobPost.objects.get(pk=job_post_id)
    except JobPost.DoesNotExist:
        # Display 404 page not found
        return render(request, "jobs/notfound.html", {"message": "Job post does not exist."})

    # Check if the logged in user is the owner of the job post
    if not util.get_profile_type_obj(request.user, "employer") == job_post.employer:
        # Redirect to the index page
        return HttpResponseRedirect(reverse("index"))

    # Deactivate the job post
    job_post.active = False
    job_post.save()

    # Redirect to the job post page
    return HttpResponseRedirect(reverse("display_job_post", args=(job_post_id,)))


def search(request):
    """
    Searches jobs for a typed query. Renders a search results page that displays a list of all entries that have
    the query as a substring.
    """
    # Get the query and existing entries
    query = request.GET.get('q')
    job_posts = JobPost.objects.filter(active=True)

    # First search in job titles
    matches_first = [job_post for job_post in job_posts if query.casefold() in job_post.title.casefold()]

    # Second search in job descriptions
    matches_second = [job_post for job_post in job_posts if query.casefold() in job_post.description.casefold()]

    # Finally search in company names
    matches_third = [job_post for job_post in job_posts if query.casefold() in
                     job_post.employer.company_name.casefold()]

    # Merge lists
    matches = util.add_to_list(matches_first, matches_second)
    matches = util.add_to_list(matches, matches_third)

    # Return a search results page with a list of all matching entries
    return render(request, "jobs/index.html", {"job_posts": matches})


def login_view(request):
    """
    Verifies user credentials and logs in the user.
    """
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "jobs/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "jobs/login.html")


def logout_view(request):
    """
    Logs out the user.
    """
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request, profile_type):
    """
    Creates a new user a new profile and logs in the user.
    """
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "jobs/register.html", {
                "message": "Passwords must match."
            })

        # Initialize fields
        first_name = ""
        last_name = ""
        company_name = ""

        if profile_type == "job_seeker":
            first_name = request.POST["first_name"]
            last_name = request.POST["last_name"]
            if first_name == "" or last_name == "":
                return render(request, "jobs/register.html", {"profile_type": profile_type,
                                                              "message": "Please enter your name."})
        else:
            company_name = request.POST["company_name"]
            if company_name == "":
                return render(request, "jobs/register.html", {"profile_type": profile_type,
                                                              "message": "Please enter your company name."})

        # Attempt to create new user and profile
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "jobs/register.html",
                          {"profile_type": profile_type,
                           "message": "Username already taken."})

        # Create profile
        util.create_profile(user=user, profile_type=profile_type, first_name=first_name,
                            last_name=last_name, company_name=company_name)

        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "jobs/register.html", {"profile_type": profile_type})
