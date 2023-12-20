# MuroChat Backend

This is a Django project that utilizes Poetry as the package manager, Django tests for running tests, PyMongo for MongoDB integration, and Djongo as the MongoDB backend for Django.


## MuroChat
MuroChat by Privado is an LLM Chat platform with secure, AI-powered communication tailored for employees within enterprises. It's a robust platform that emphasizes productivity and privacy. This README file will guide you through the setup process and explain how to get the application up and running.

### Key Features
- Sensitive Data Redaction with a message firewall.
- Okta Integration for user management.
- Flexible LLM Integration for any open-source or premium models.
- User-Centric Design to manage, pin, share, and bookmark chats.
- Real-Time Admin Oversight for chat monitoring and access control.

### Why MuroChat?
- Focused on Data Privacy with a security-first approach.
- Developer Freedom to choose and customize LLMs and data models.
- Community-Centric Updates for continuous platform enhancement.

### For Employees, By Employees 
- We want to empower every employee to be the best at what they do by leveraging AI without breaking the security fabric of the company. 
- MuroChat is highly modular and open for all to innovate.


## Prerequisites

- Python 3.x
- Poetry (installed globally or within a virtual environment)
- MongoDB server (running locally or remotely)

## Installation

1. Clone the repository:

   ```shell
   git clone https://github.com/Privado-Inc/private-gpt-backend.git
   ```
2. Install Poetry
    ```
    pip install poetry
    ```

3. Run Project
    Set Environment Variable `export VIRTUAL_ENV=.venv`

    ```
    mkdir .venv
    python3 -m venv .venv
    source env/bin/activate
    export VIRTUAL_ENV=.venv && poetry shell
    poetry update
    poetry install
    poetry run python -m spacy download en_core_web_lg 
    poetry run python manage.py makemigrations
    poetry run python manage.py migrate
    poetry run python manage.py runserver

    ```

#### How to run linter
```
pylint --load-plugins=pylint_django --rcfile .pylintrc *
```