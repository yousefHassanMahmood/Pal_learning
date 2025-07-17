# Pal Learning

A lightweight Django-based Learning Management System (LMS) where instructors can create courses (with modules, lessons, quizzes) and students can enroll, track progress, take quizzes, and discuss.

---

## 🚀 Features

- **Custom Auth & Roles**  
  `CustomUser` extends `AbstractUser` with:  
  - `role` (`student` / `instructor` / `admin`)  
  - `address`  
  - `is_approved` (instructors require admin approval)

- **Course Catalog**  
  AJAX-powered search & filter by title or topic.

- **Instructor Dashboard**  
  - CRUD courses, modules, lessons, quizzes  
  - Upload video (YouTube embed) or text content  
  - View enrollment stats

- **Student Dashboard**  
  - Browse all courses or view “My Courses” (enrolled)  
  - Enroll / drop / re-enroll  
  - Track lesson completion & quiz scores

- **Quizzes**  
  - Single-choice or multiple-choice questions  
  - Randomized answer order on each load  
  - Immediate scoring via form submission

- **Discussion Forum**  
  Per-lesson threads and comments.

- **Responsive UI**  
  Bootstrap-based templates adapt to mobile & desktop.

- **Security & Validation**  
  CSRF protection, form validation, role-based access.

- **Deployment Ready**  
  Easily deployable to AWS EC2 / RDS MySQL + S3 for static/media.

---

## 🛠️ Installation & Setup

1. **Clone the repo**  
   ```bash
   git clone https://github.com/yousefHassanMahmood/pal_learning.git
   cd pal_learning
   ```

2. **Create & activate virtualenv**  
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # on Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure MySQL & environment**  
   Create a file named `.env` in the project root with:
   ```ini
   SECRET_KEY=your-django-secret-key
   DEBUG=True

   DB_NAME=pal_learning
   DB_USER=dbuser
   DB_PASSWORD=dbpassword
   DB_HOST=localhost
   DB_PORT=3306
   ```

4. **Run migrations & create superuser**  
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Collect static files & start server**  
   ```bash
   python manage.py collectstatic
   python manage.py runserver
   ```
   Visit <http://localhost:8000> to see the app.

---

## ⚙️ Configuration

- **`settings.py`**  
  ```python
  AUTH_USER_MODEL = 'pal_learning_app.CustomUser'
  ```

- **`INSTALLED_APPS`**  
  Make sure `pal_learning_app` is included:
  ```python
  INSTALLED_APPS = [
      'pal_learning_app',
      'django.contrib.admin',
      'django.contrib.auth',
      'django.contrib.contenttypes',
      'django.contrib.sessions',
      'django.contrib.messages',
      'django.contrib.staticfiles',
  ]
  ```

- **Templates**  
  - Located under `templates/`  
  - Base layout: `base.html`

- **URLs**  
  - Auth: `/signup/`, `/login/`, `/logout/`  
  - Courses:  
    - List: `/courses/`  
    - Detail: `/courses/<id>/`  
    - Create/Edit/Delete: `/courses/create/`, `/courses/<id>/edit/`, `/courses/<id>/delete/`  
  - Modules/Lessons/Quizzes are nested under their parent course

- **Forms**  
  ModelForms provided for Course, Module, Lesson, Quiz, Question

- **Permissions**  
  Decorators: `@login_required` and `@user_passes_test(is_instructor_or_admin)`




