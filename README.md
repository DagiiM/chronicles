# WELCOME TO EQUITY AFIA WEBSITE PROTOTYPE
- This is a django project and it leverages on drf for the API

The project is divided into two scopes
1. API ACCESS `https://eleso.ltd/api/...`
2. WEB ACCESS

Demo is available through `https://eleso.ltd`

Admin Login Credentials are presented in the pdf about the project in the submission.

Collection for Website API calls is available under `api_collection.json`

The project works as is with a few remaining fixes.

## Modules
- Clinic module
- Pharmacy Module
- NotificationsModule
- About module
- Consultations Module

Of all Modules, clinic is like the infrastructure composed of humanware to manage and optimization of the resources.

## Installation
- Use normal installation procedures
- Create the virtual environment, be sure to use the `requirements.txt`
- Be sure to rename `.env.example` to `.env` and update environment variables accordingly
- After all the set up run `python manage.py collectstatic` - This step assumes you have already spinned up the environment and it's active if not
- Go where virtual environment directory is and run `source venv/bin/activate` if on linux and environment is saved as `venv`
