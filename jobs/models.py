import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


MONTHS = ((1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12))
YEARS = list()
for i in range(1960, (datetime.datetime.now().year + 1)):
    YEARS.append((i, i))
INDUSTRIES = (("Aerospace", "Aerospace"), ("Agriculture", "Agriculture"), ("Automotive", "Automotive"),
              ("Construction", "Construction"), ("Education", "Education"), ("Energy", "Energy"),
              ("Entertainment", "Entertainment"), ("Financial Services", "Financial Services"),
              ("Government", "Government"), ("Healthcare", "Healthcare"), ("Hotels", "Hotels"),
              ("Human Resources", "Human Resources"), ("IT", "IT"), ("Insurance", "Insurance"),
              ("Legal", "Legal"), ("Management", "Management"), ("Manufacturing", "Manufacturing"),
              ("Media", "Media"), ("Nonprofit", "Nonprofit"),
              ("Personal Consumer Services", "Personal Consumer Services"),
              ("Pharmaceutical", "Pharmaceutical"), ("Real Estate", "Real Estate"),
              ("Restaurants", "Restaurants"), ("Retail", "Retail"), ("Telecommunications", "Telecommunications"),
              ("Transportation", "Transportation"), )
DEGREES = (("High School", "High School"), ("Vocational Degree", "Vocational Degree"),
           ("Associate's Degree", "Associate's Degree"), ("Bachelor's Degree", "Bachelor's Degree"),
           ("Master's Degree", "Master's Degree"), ("Doctoral Degree", "Doctoral Degree"))


class User(AbstractUser):
    """
    User model that inherits from AbstractUser
    """
    pass

    def __str__(self):
        return f"{self.username}"


class Profile(models.Model):
    """
    Profile model for both employers and job seekers
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # profile_type is either "job_seeker" or "employer"
    profile_type = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.user.username}"


class Employer(models.Model):
    """
    Model for employers
    """
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=128)
    num_of_employees = models.PositiveIntegerField()
    location = models.CharField(max_length=128, blank=True, null=True)
    about = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.profile.user.username}"


class JobSeeker(models.Model):
    """
    Model for job seekers
    """
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.profile.user.username}"


class Resume(models.Model):
    """
    Resume model that stores various attributes of a resume
    """
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    address = models.CharField(max_length=128, blank=True, null=True)

    # Summary of Qualifications
    summary = models.TextField()
    skills = models.TextField()

    def __str__(self):
        return f"{self.profile.user.username}"


class Experience(models.Model):
    """
    Experience model for storing job experience
    """
    job_title = models.CharField(max_length=128)
    company_name = models.CharField(max_length=128)
    location = models.CharField(max_length=128)
    start_month = models.PositiveSmallIntegerField(choices=MONTHS)
    start_year = models.PositiveSmallIntegerField(choices=YEARS)
    end_month = models.PositiveSmallIntegerField(choices=MONTHS, blank=True, null=True)
    end_year = models.PositiveSmallIntegerField(choices=YEARS, blank=True, null=True)
    description = models.TextField()
    current_job = models.BooleanField(default=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="experience")

    class Meta:
        # Sort experience by start_year and start_month when queried so that recent experiences appear first.
        # The minus sign is used to sort in descending order.
        ordering = ["-start_year", "-start_month"]

    def __str__(self):
        return f"User: {self.resume.profile.user.username} Company: {self.company_name} " \
               f"Start Date:{self.start_month}/{self.start_year}"


class Education(models.Model):
    """
    Education model for storing education details
    """
    school = models.CharField(max_length=128)
    degree = models.CharField(max_length=128, choices=DEGREES)
    field_of_study = models.CharField(max_length=128)
    start_month = models.PositiveSmallIntegerField(choices=MONTHS, default=1)
    start_year = models.PositiveSmallIntegerField(choices=YEARS, default=2016)
    end_month = models.PositiveSmallIntegerField(choices=MONTHS, default=1)
    end_year = models.PositiveSmallIntegerField(choices=YEARS, default=2020)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="education")

    class Meta:
        # Sort by start_year and start_month when queried so that recent education appear first.
        # The minus sign is used to sort in descending order.
        ordering = ["-start_year", "-start_month"]

    def __str__(self):
        return f"User: {self.resume.profile.user.username} School: {self.school} " \
               f"Degree:{self.degree}"


class JobPost(models.Model):
    """
    JobPost model that stores various attributes of a single job post
    """
    # The industry of the job
    industry = models.CharField(max_length=128, choices=INDUSTRIES)
    # Title of the job
    title = models.CharField(max_length=128)
    # Description of the job
    description = models.TextField()
    # Part time/Full time
    job_type = models.CharField(max_length=128, choices=(("Part Time", "Part Time"), ("Full Time", "Full Time")))
    # Location of the job
    location = models.CharField(max_length=128)
    # Salary range
    min_salary = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    max_salary = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    # Boolean field to identify whether the job post is active or closed
    active = models.BooleanField(default=True)
    # Creator of the job post
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name="job_posts")
    # Creation time of the job post
    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Company: {self.employer.company_name}, Title: {self.title}"

    class Meta:
        # Sort job posts by created_on when queried so that job posts created recently will appear first. The minus sign
        # is used to sort them in descending order.
        ordering = ["-created_on"]

    def __str__(self):
        return f"{self.title} {self.created_on}"


class JobApplication(models.Model):
    """
    JobApplication model for storing applicant and job post info
    """
    applicant = models.ForeignKey(JobSeeker, on_delete=models.CASCADE, related_name="applications")
    job_post = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name="applications")

    def __str__(self):
        return f"{self.job_post}, Applicant: {self.applicant.first_name} {self.applicant.last_name}"
