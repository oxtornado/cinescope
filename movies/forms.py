from django import forms
from .models import Profile
from .models import Movie, Review, ReviewComment
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(forms.ModelForm):
    class Meta:
        model = User  # Asegúrate de importar el modelo User de Django
        fields = ['username', 'email', 'password']

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title', 'release_year', 'description']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['comment']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture']
    
class ReviewCommentForm(forms.ModelForm):
    class Meta:
        model = ReviewComment
        fields = ['comment']
        
class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio']  # Campos que quieres editar