### hw05_final
# Social Network Web Application
This is a Django-based social network web application that allows users to create and share posts, follow other users, and comment on posts.

Getting Started
To run this application on your local machine, follow these steps:

Clone this repository onto your machine
Install Django and other required packages by running 
```
pip install -r requirements.txt
```
in your terminal or command prompt.
Migrate the database by running 
```
python manage.py migrate 
```
in your terminal or command prompt.
Start the development server by running 
```
python manage.py runserver 
```
in your terminal or command prompt.
Open your web browser and go to http://localhost:8000/ to view the home page.

### Functionality
User Authentication and Authorization
This application uses the built-in Django authentication system to allow users to sign up, log in, and log out. Users can only edit their own posts and profiles, and they can only delete their own comments.

Posts and Groups
Users can create and share posts, which can be organized by group. Users can create and join groups, and posts can be viewed by group.

Follow System
Users can follow other users and view their posts on their homepage. They can also view a list of users they are following and a list of users who are following them.

[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)

## Tools and stack: 
- python 
- HTML 
- CSS 
- Django 
- Bootstrap 
- Unittest 
- Pythonanywhere

### Author:
Balakhonova Marina
