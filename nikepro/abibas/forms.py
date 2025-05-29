from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from abibas.models import User

# ---------------------------------------------
# Формы приложения abibas
# Описывают формы регистрации, логина, профиля и т.д.
# ---------------------------------------------

class UserRegistrationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('seller', 'Продавец'),
        ('warehouse', 'Складовщик'),
        ('admin', 'Админ'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, label='Роль', required=True)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'role')

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data.get('role')
        user.role = role
        if role == 'admin':
            user.is_staff = True
            user.is_superuser = True
        elif role in ['seller', 'warehouse']:
            user.is_staff = True
        if commit:
            user.save()
        return user

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}))

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'address', 'avatar']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'custom-file-input'})
        } 