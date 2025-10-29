# StudyTrack AI - AI-Powered Student Study Habit Recommender

StudyTrack AI is a web application built with Django designed to help students track their study progress, manage courses, and improve their learning habits through AI-powered features. It includes an adaptive quiz system that generates questions on the fly and a notification system to keep students engaged.

![User Dashboard](https://i.imgur.com/G5gqN5j.jpeg)

## Key Features ✨

* **User Authentication:** Secure registration and login system for both students and administrators.
* **Course Management:** Admins can add, track, and manage student courses, including progress, hours spent, and status.
* **AI-Powered Quizzes:** Dynamically generates multiple-choice quizzes for any course using the Google Gemini API.
* **Adaptive Learning:** The difficulty of AI-generated quizzes (Basic, Intermediate, Advanced) adjusts based on the student's previous performance.
* **Automated Email Reminders:** Uses Celery and Redis to send scheduled email notifications for:
    * Completing high-progress courses (three times a day).
    * Attempting uncompleted AI-generated quizzes (daily).
* **Personalized Dashboard:** Students see a dashboard tailored to their specific courses, progress, and pending quizzes.
* **Pop-up Alerts:** On-site notifications alert students when they are close to completing a course to provide motivation.

## Technology Stack 🛠️

* **Backend:** Python, Django
* **Database:** MySQL
* **Asynchronous Tasks:** Celery
* **Message Broker:** Redis
* **AI Integration:** Google Gemini API
* **Frontend:** HTML, Tailwind CSS, JavaScript

## Setup and Installation 🚀

Follow these steps to get the project running locally.

### 1. Prerequisites

Make sure you have the following installed on your system:
* Python 3.10+
* Redis (`brew install redis` on macOS)
* MySQL Server

### 2. Clone the Repository

git clone [https://github.com/your-username/StudyTrack_AI.git](https://github.com/your-username/StudyTrack_AI.git)
cd StudyTrack_AI/sample


### Set Up Virtual Environment

### Create and activate a virtual environment.
python3 -m venv myenv
source myenv/bin/activate

### Install Dependencies
pip install -r requirements.txt

### Configure Environment Variables
# .env

# Your Django Secret Key (you can generate a new one)
SECRET_KEY="your-django-secret-key"

# Your Google AI API Key
GOOGLE_API_KEY="your-google-api-key"

# Your Gmail App Password for sending emails
EMAIL_HOST_USER="your-email@gmail.com"
EMAIL_HOST_PASSWORD="your-16-character-app-password"

### Set Up the Database
### Make sure your MySQL server is running.
### Create a new database named studytrack.
### Update the DATABASES configuration in sample/settings.py with your MySQL username and password.
### Run migrations to create the database tables.
python manage.py makemigrations
python manage.py migrate

### Create a Superuser (Admin)
python manage.py createsuperuser

### Run the Development Servers
### Terminal 1: Start Redis
redis-server
### Terminal 2: Run the Django Server
python manage.py runserver
### Terminal 3: Start the Celery Worker
celery -A sample worker -l info
### Terminal 4: Start the Celery Beat Scheduler
celery -A sample beat -l info


### Your application should now be running at http://127.0.0.1:8000/.


### Usage Guide 📖
### Register: Create a new student account.
### Log In: Log in as a student or as the admin user you created.
### Admin Dashboard: As an admin, you can assign new courses to students.
### Student Dashboard: As a student, you can view your courses and progress.
### Take a Quiz: In the "My Courses" tab, click the "Start AI Quiz" button for any ongoing course to generate and attempt a quiz. Your score will be saved, and the difficulty will adapt for the next quiz on that subject.


### License
### This project is licensed under the MIT License. See the LICENSE file for details.
