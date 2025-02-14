# Tutor Me: A Tool for Students, by Students

----
<img src="config_files/banner_group.png" alt="Logo" width="500">

## Description

- what your project is
- why you chose this project and goal, and
- how you plan to achieve it.

----

## Instalation

# Project Installation Guide

## Prerequisites

Ensure you have the following installed on your system:

- **Python 3.10+**: [Download here](https://www.python.org/downloads/)
- **PostgreSQL**: [Download here](https://www.postgresql.org/download/)
- **Node.js & npm**: [Download here](https://nodejs.org/)

## Installation Steps

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
Your application should now be running successfully! 🚀

----
## Functionalities

### Data Storage and Handling

Will you be using a database system (eg. SQL, MongoDB,...)?
How will you load and process data, and what libraries do you plan to use for this (eg. pandas/polars, numpy,...)?

### User Management

Will your project have distinct users?
If so, how do you store and check credentials?
Are there different roles (eg. customer/admin) with privileges?

### Interface

What kind of interface are you planning (CLI/GUI)?
What operating system will it run on, or will it be a web-based app?
What libraries do you need for this?

### Statistical Analysis

What statistical analyses will you conduct on your data?
Will specialized libraries be required for this, and if so, which?
What quintessential point(s)/takeaways are you planning to substantiate?

### Visualizations

How can you effectively communicate your takeaways (probably from statistical analysis) visually?
I.e., what kinds of visual representations are suitable for your project?
Will they be included in a dashboard-like part of your interface, or non-interactive infographics?
With what libraries will you implement this?

----
## Installation and Usage

This should inform anyone who looks at your project repository on how they can install and run the project code on their own machine, e.g. by cloning this repository, installing dependencies and running some main script.

----
## Timeline

Give some outline as to what should be achieved at what time during project development.

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
## Acknowlegdments

Here, you can (and should) mention all libraries you used, data sources, as well as other credits such as inspirations for your projects, papers that helped with your methodology or similar things.

If you want, you can create subsections for all of these, or just create bullet-points for it. If possible, provide a link to the original source(s).
