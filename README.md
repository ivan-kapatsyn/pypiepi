# Tutor Me: A Tool for Students, by Students

----
<img src="config_files/banner_group.png" alt="Logo" width="500">


## Description

The project aims to develop a web-based tutor management system designed
specifically for students. This application allows students to organize and
participate in tutoring sessions, and enables senior students to assist their peers
by offering tutoring services. The platform facilitates interaction among
students and tutors, making it easier for users to find tutoring sessions based
subjects, ratings, or specific topics. Tutoring sessions are courses designed for
students to participate in, created by tutors on various subjects and topics.
These sessions can have different maximum student capacities, levels, and
formats—either one-time or recurring on specific days—while students can
easily filter and choose sessions based on their preference


We chose this project because many students struggle with understanding
specific course topics, even after attending regular lectures. By creating this
platform, we hope to provide a space where senior students can offer their help,
creating a collaborative and supportive learning environment. In addition,
tutors will have the opportunity to receive recognition for their efforts in helping others.

By completing this project, we aim to provide students with a valuable tool to
improve their learning experience, while also offering tutors the chance to make
a positive impact in their academic community.

----
## Group Details

- Name: **PyPieπ**
- Code: **G11**
- Repository: [GitHub](https://github.com/ivan-kapatsyn/pypiepi)
- Tutor Responsible: **Frederik Hennecke**
- Team leader: **Ivan Kapatsyn**
- Group members: Birte Maria Becker, Andrii Demydenko, Melis Ahu Gülcigil, Ivan Kapatsyn

### Responsibilities

- **Ivan Kapatsyn:** Backend
- **Andrii Demydenko:** Environment setup + Frontend + API
- **Birte Maria Becker:** Frontend + API
- **Melis Ahu Gülcigil:** Database integration


----

## Functionalities


### Data Storage and Handling

- PostgreSQL is used for data storage, ensuring secure management of user accounts, session data, and ratings.
- Data is processed and stored in a normalized relational database.
- Sensitive data, such as passwords, is encrypted to ensure security and compliance with data protection standards.

### User Management/Roles

- TutorMe has different user roles: Student, Tutor, and Admin.
- **Student**: Can join tutoring courses and provide feedback after courses.
- **Tutor**: Can create and manage courses, but cannot attend them.
- **Admin**: Has the ability to access key statistics about the number of registered users.
- A user can be both a Student and a Tutor but will have separate accounts with different privileges, and options.
- Users must register with a valid token. Authentication is required to access the plattform

### Interface

- The application has a user-friendly web-based UI, with the backend preferably running on Windows. 
- It uses Flask for the backend and PostgreSQL for data storage, along with other necessary libraries and frameworks
- The interface include features such as course searching and user feedback

### Statistical Analysis and Visualization

- Matplotlib is considered for implementing visualizations, such as displaying tutor ratings.
- The system provides key statistics, such as a bar chart of the number of registered users for the admins and course ratings.


----

## Installation and Usage


### Prerequisites

Ensure you have the following installed on your system:

- **Python 3.10+**: [Download here](https://www.python.org/downloads/)
- **PostgreSQL**: [Download here](https://www.postgresql.org/download/)
- **Node.js & npm**: [Download here](https://nodejs.org/)

### 1. Clone the Repository
```sh
git clone <your-repository-url>
cd <your-project-directory>
```

### 2. Create a Virtual Environment (Recommended)
```sh
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Set Up environment variables
- Create a new `.env` file at the root.
- Copy the content of `test.env` and paste it into `.env`.
- Replace `'...'` with the values described in the comments (except for `DUMMY_VARIABLE_USED_FOR_UNITTEST`).

### 5. Install Frontend Libraries
Download and install the required frontend libraries using npm:
```sh
npm install jquery bootstrap
```

### 6. Initialise the local database
Run the following script
```sh
python3 -m scripts.initialize_db
```

### 7. Run the application
Run the following script
```sh
python3 -m scripts.run
```

### Done!
Your application should now be running successfully!

----
### How to Use

On the homepage, you have the option to log in or register as a new user. 
To register as a new user, click on the registration button, which redirects 
you to a page where you enter your personal information and specify whether 
you want to register as a Student or a Tutor. You will also need to provide 
a valid token, as registration only works with a valid token. Once registration 
is successful, the Student or Tutor is redirected to their main page, where the 
views for Students and Tutors differ slightly. The Student can edit their personal 
information, view the courses they are enrolled in, and search for additional 
courses. The Tutor can also edit their personal information, view current comments, 
check their Average Rating, see the schedules for the courses they created, and 
add new courses. The website is designed so that each button clearly indicates 
its function.

----

## Timeline



----
## Used Packages

- **pandas:** Used for data manipulation and analysis, especially for handling tabular data.
- **numpy:** Provides support for numerical computations and efficient array operations.
- **flask:** A lightweight web framework for building the backend of the application.
- **flask-wtf:** Integrates Flask with WTForms to handle web forms securely.
- **python-dotenv:** Loads environment variables from a .env file to manage configuration settings.
- **psycopg2:** A PostgreSQL adapter for Python, enabling interaction with the database.
- **bcrypt:** Handles password hashing and verification for secure authentication.
- **matplotlib:** Used for creating visualizations, such as charts and graphs.
- **markdown:** Converts Markdown text into HTML for rendering formatted content.
