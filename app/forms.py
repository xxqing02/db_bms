from django.forms import ModelForm
from . import models

class ReaderLoginForm(ModelForm):
    class Meta:
        model = models.Reader
        fields = ['username', 'password']


class LibrarianLoginForm(ModelForm):
    class Meta:
        model = models.Librarian
        fields = ['username', 'password']

