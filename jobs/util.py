from django.db import IntegrityError
from sqlite3 import OperationalError

from .models import Profile, JobSeeker, Employer, Experience, Resume, User, Education


def create_profile(user, profile_type, company_name="", first_name="", last_name=""):
    """
    Creates a new profile based on the profile type.
    """
    # Create a new profile object
    new_profile = Profile(user=user, profile_type=profile_type)
    new_profile.save()
    if profile_type == "job_seeker":
        # Create a new job seeker object
        new_job_seeker = JobSeeker(profile=new_profile, first_name=first_name, last_name=last_name)
        new_job_seeker.save()
    else:
        # Create a new employer object
        new_employer = Employer(profile=new_profile, company_name=company_name,
                                num_of_employees=0, location="", about="")
        new_employer.save()

    return new_profile


def get_resume_from_user(user):
    """
    Fetches the resume from the user object
    """
    resume = None
    # Get the profile object
    profile = get_profile_from_user(user)

    if profile:
        # Get the resume object
        try:
            resume = Resume.objects.get(profile=profile)
        except Resume.DoesNotExist or IntegrityError:
            # Create resume
            if profile.profile_type == "job_seeker":
                resume = Resume(profile=profile)
                resume.save()

    return resume


def get_resume_from_username(username):
    """
    Gets the resume from the username
    """
    try:
        user = User.objects.get(username=username)
        resume = get_resume_from_user(user)
    except User.DoesNotExist:
        resume = None

    return resume


def get_profile_from_user(user):
    """
    Gets the profile object from the user object
    """
    profile = None

    if user.is_anonymous:
        return profile

    # Get the profile object
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist or IntegrityError:
        # If user is superuser create a profile
        if user.is_superuser:
            profile = create_profile(user=user, profile_type="job_seeker")
            profile.save()

    return profile


def get_profile_type_obj(user, profile_type):
    """
    Returns either a job seeker of employer object. Returns None if profile does not exist.
    """
    profile = get_profile_from_user(user)

    if profile and profile.profile_type == profile_type:
        if profile_type == "job_seeker":
            return profile.jobseeker
        else:
            return profile.employer

    return None


def get_data_from_resume(resume):
    """
    Returns education and experience objects from the resume
    """
    # Get the experience objects
    try:
        experience = Experience.objects.filter(resume=resume)
    except Experience.DoesNotExist or OperationalError:
        experience = None

    # Get the education objects
    try:
        education = Education.objects.filter(resume=resume)
    except Education.DoesNotExist or OperationalError:
        education = None

    return experience, education


def is_date_range_valid(start_month, start_year, end_month, end_year, current_job):
    """
    Validates the date range if not current job.
    """
    # Return true if current job
    if current_job:
        return True
    # Check if end dates exit
    if not (end_month and end_year):
        return False
    # Check the date range
    if end_year < start_year or (start_year == end_year and end_month <= start_month):
        return False
    return True


def is_salary_range_valid(min_salary, max_salary):
    """
    Validates the salary range.
    """
    if max_salary < min_salary:
        return False
    return True


def delete_row(data_object, pk):
    """
    Deletes row from a model based on the primary key
    """
    try:
        data_object.objects.get(pk=pk).delete()
    except Exception as e:
        print(str(e))
        return False
    return True


def add_to_list(primary, secondary):
    """
    Appends secondary list items to primary list.
    """
    for secondary_item in secondary:
        if secondary_item not in primary:
            primary.append(secondary_item)
    return primary
