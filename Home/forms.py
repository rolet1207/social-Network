from cProfile import label
import email
from django import forms
import re
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from Home.models import Profile

class RegistrationForm(forms.Form):
    # username = forms.CharField(label='Username', max_length=30)
    # email = forms.EmailField(label='Email')
    # password1 = forms.CharField(label='Password', widget=forms.PasswordInput())
    # password2 = forms.CharField(label='Retype password', widget=forms.PasswordInput())

    username = forms.CharField(label="", max_length=30, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Username'
    })) 
    email = forms.EmailField(label="",widget=forms.EmailInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Email'
    })) 
    password1 = forms.CharField(label="",widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Password'
    })) 
    password2 = forms.CharField(label="",widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Confirm password'
    })) 


    def clean_password2(self):
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']
            if password1==password2 and password1:
                return password2
        raise forms.ValidationError("Not valid password")

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.search(r'^\w+$', username):
            raise forms.ValidationError("Username must not have special character")
        try:
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            return username
        raise forms.ValidationError("Username has existed")

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            User.objects.get(email=email)
        except ObjectDoesNotExist:
            return email
        raise forms.ValidationError("Email has existed")

    def save(self):
        User.objects.create_user(username=self.cleaned_data['username'],
        email=self.cleaned_data['email'],
        password=self.cleaned_data['password1'])

class EditInformationForm(UserChangeForm):
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Username'
    })) 
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Email'
    }))
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'First name'
    })) 
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Last name'
    })) 
    last_login = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Last login',
        'readonly':True
    }))
    date_joined = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Date joined',
        'readonly':True
    })) 

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'last_login', 'date_joined')

class PasswordChangingForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-lg',
        'type': 'password',
        'placeholder': 'Old password',
    }))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-lg',
        'type': 'password',
        'placeholder': 'New password',
    }))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-lg',
        'type': 'password',
        'placeholder': 'Confirm new password',
    }))

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')

class CreateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'ava_pic', 'background_pic')

        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control-lg'})
        }
