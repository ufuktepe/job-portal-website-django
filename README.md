# **JOB PORTAL**

Job portal is a website where employers can post jobs to find suitable candidates and job seekers can search and apply for jobs.

Employers can:

● Create job postings

● Edit and close job postings

● Create a profile page for their company

● See list of job seekers who have applied for the job. Clicking on any job seeker’s name the employer can see the job seeker’s resume.

Job Seekers can:

● Apply to job postings

● Create a resume

● See a list of job posts that they have applied to

Anyone visiting the site can:

● Search for jobs by entering keywords in a search bar.

● See how many people have applied for each job.


## **Getting Started**
pip install django on your system.

In your terminal, cd into the job_portal directory.

Run python manage.py makemigrations jobs to make migrations for the jobs app.

Run python manage.py migrate to apply migrations to your database.

Run python manage.py runserver.



**TEMPLATES**
## **create.html**
Displays the create job post page. Employers can post new jobs using this page.

## **index.html**
Displays a search bar for searching jobs and displays job posts. 

## **jobpost.html**
Displays details of a single job post and includes an edit form. 

If the current user is the owner of the job post, displays “edit” and “close” listing buttons. 

If the current user is a job seeker who has not applied for this job, displays an “apply” button. Otherwise, displays a “cancel application” button.

If the current user is not logged in, displays a “login to apply” button.

## **layout.html**
Layout template html for the other html files. Includes a navigation bar that has the following links:

- All Jobs
- Post Job (for employers)
- Dropdown menu including Resume, Applied Jobs, and Logout links for job seekers 
- Dropdown menu including Profile, Posted Jobs, and Logout links for employers
- Login and Register links for users who are not logged in 

## **login.html**
Login page that asks for a username and password.

## **notfound.html**
404 error page that displays a custom message.

## **profile.html**
Displays a profile page of an employer. Consists of 2 views: display and edit. The display view displays the profile whereas the edit view includes an edit form for the profile owner.
## **register.html**
Register page for job seekers and employers, asking for a username, password, and email. Additionally, a company name should be provided for employers and a first and a last name should be provided for job seekers.

## **resume.html**
Displays the resume of the job seeker. Includes the following sections:

- Address: consists of three sections 
- Summary of Qualifications
- Experience
- Education
- Skills

Each section consists of the following divisions:

1. A header area
1. A content area for displaying the content
1. An edit form area for editing the content 

Additionally, the Experience and Education sections include a form area for adding new entries.
















**JAVASCRIPT FILES**
## **jobpost.js**
Includes the following functionalities for jobpost.html:

- Applying for a job without reloading the page for the job seeker
- Showing/hiding the edit form for the employer

## **profile.js**
Provides the functionality for switching between display and edit views.

## **resume.js**
Includes the following functionalities for resume.html:

- Editing sections without reloading the page
- Removing sections without reloading the page
- Switching between forms (edit/add) and displaying content 
- Populating month, year, and degree type dropdown menus
- Validating user inputs in edit forms














**PYTHON FILES**
## **admin.py**
All 9 models are registered to the admin site in this file.

## **models.py**
Includes the following models:
### User 
User model that Inherits from AbstractUser.
### Profile 
This is the parent model for Employer and JobSeeker models. 

- It has a OneToOne relationship with the User model. 
- It has a CharField that is either "job\_seeker" or "employer" for identifying the profile type.
### Employer 
This is the model for employers.

- It has a OneToOne relationship with the Profile model.
- It has fields for storing details of an employer such as company name, number of employees, location etc.
### JobSeeker
This is the model for job seekers.

- It has a OneToOne relationship with the Profile model.
- It has fields for storing details of a job seeker such first and last name.
### Resume
The resume model stores data of a resume.

- It has a OneToOne relationship with the Profile model.
- It has fields for storing details of a job seeker such as address, summary of qualifications, and skills. 
- I chose to create separate models for Education and Experience since each Education or Experience entry includes more than one type of data. Hence each Education and Experience model has a ForeignKey to Resume model.
### Experience
Stores data related to a single work experience.

- It has a ForeignKey to Resume model.
- Includes fields for job title, company name, location, start date, end date, and job description.
- It has a Boolean field called current\_job to indicate whether this work experience is the current job of the user. In that case, the end date will be null.
### Education
Stores data related to a single education.

- It has a ForeignKey to Resume model.
- Includes fields for school, degree, field of study, start date, and end date.
###
### JobPost
Stores data related to a single job post.

- It has a ForeignKey to Employer model since each job post is created by an employer.
- Includes fields for industry, job title, job description, job type, location, salary.
- It has a Boolean field called “active” to indicate whether the job post is open or closed.

### JobApplication
This model connects an applicant to a job post.

- It has ForeignKeys to JobSeeker and JobPost models.

## **util.py**
Includes helper methods to prevent code repetition. 

- create\_profile: creates a new Profile object and a new Employer or JobSeeker object.
- get\_resume\_from\_user: takes a user object as input and returns the resume.
- get\_resume\_from\_username: takes a username as input and returns the resume.
- ` `get\_profile\_from\_user: takes a user object as input and returns the profile object.
- get\_profile\_type\_obj: takes a profile type as input and returns either a job seeker of employer object. 
- get\_data\_from\_resume: returns education and experience objects from the resume.
- is\_date\_range\_valid: validates a date range.
- is\_salary\_range\_valid: validates a salary range.
- delete\_row: takes a model object and a primary key as input and removes the entry from the model.
- add\_to\_list: takes two lists as input and returns a merged list.

## **views.py**
Includes the following ModelForms:

- AddExperienceForm: for creating a new job experience in the resume section (resume.html)
- AddEducationForm: for creating a new education in the resume section (resume.html)
- EmployerForm: for employer profiles
- JobPostForm: for creating a new job post

Includes the following methods:

- **Index:** default route that returns active job posts
- **display\_profile:** takes user id as an input and displays the profile of that user.
- **edit\_profile:** takes user id as an input and updates the profile of that user based on a POST request.
- **resume:** takes username as an input and displays the resume of that user.
- **edit\_resume:** takes a resume field (address, summary, skills) as an input and edits the relevant resume field based on a PUT request from JavaScript.
- **add\_experience:** creates a new experience object based on a POST request.
- **edit\_experience:** takes a primary key of an experience object as an input and updates the experience object based on a PUT request from JavaScript.
- **add\_education:** creates a new education object based on a POST request.
- **edit\_education:** takes a primary key of an education object as an input and updates the education object based on a PUT request from JavaScript.
- **remove\_item:** deletes an Education or Experience entry based on a PUT request from JavaScript.
- **post\_job:** creates a new job post based on a POST request.
- **display\_job\_post:** takes a job post id as an input and renders a job post page based on that job post id.
- **edit\_job\_post:** takes a primary key of a job post object as an input and updates the job post object based on a POST request. Then renders the job post page.
- **apply\_job:** takes a primary key of a job post object as an input and creates a new job application if the current user has not applied to that job post. If the current user has already applied to that job post, then deletes the job application.
- **applied\_jobs:** displays open or closed job posts that a job seeker has applied.
- **posted\_jobs:** displays open or closed job posts of an employer.
- **close\_job\_post:** takes a job post id as an input and closes (deactivates) that job post. 
- **search:** searches job titles, descriptions, and company names of job posts for a typed query. Renders a search results page that displays a list of all entries that have the query as a substring. 
- **login\_view:** verifies user credentials and logs in the user.
- **logout\_view:** logs out the user.
- **register:** creates a new User object, a new Profile object, and a new JobSeeker or Employer object and finally logs in the user.
