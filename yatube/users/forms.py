from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


User = get_user_model()


class CreationForm(UserCreationForm):
    """The CreationForm class is then defined as a subclass of UserCreationForm.
    It overrides the Meta class, which is a class used by Django to define metadata for a form or model.
    In this case, it sets the model attribute of the Meta class to User, which is the user model class
    returned by get_user_model().
    It also sets the fields attribute to a tuple of field names that should be included in the form,
    including first_name, last_name, username, and email."""
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
