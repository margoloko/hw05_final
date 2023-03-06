"""This code sets up a sign-up view that displays a form to create a new user account, 
validates the form data, and saves the new user object to the database if the form data is valid.
It then redirects the user to the posts app's index page upon successful submission."""
from django.views.generic import CreateView
from django.urls import reverse_lazy

from .forms import CreationForm


class SignUp(CreateView):
    """The CreationForm class is then defined as a subclass of UserCreationForm.
    It overrides the Meta class, which is a class used by Django to define metadata for a form or model.
    In this case, it sets the model attribute of the Meta class to User,
    which is the user model class returned by get_user_model().
    It also sets the fields attribute to a tuple of field names that should be
    included in the form, including first_name, last_name, username, and email."""

    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'
