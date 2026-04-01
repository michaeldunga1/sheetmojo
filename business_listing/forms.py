from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text='Use a real email address so you can sign in reliably later.',
    )
    consent = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must agree to the terms to register.'}
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Pick a public username with 150 characters or fewer.'
        self.fields['password1'].help_text = 'Use at least 8 characters and avoid common passwords.'
        self.fields['password2'].help_text = 'Enter the same password again to confirm it.'
        self.fields['consent'].label = ''
        self.fields['consent'].help_text = "I agree to the <a href='/business_listing/terms_of_service.html' target='_blank'>Terms of Service</a> and <a href='/business_listing/privacy_policy.html' target='_blank'>Privacy Policy</a>."
        self.fields['username'].widget.attrs.update({
            'autocomplete': 'username',
            'maxlength': '150',
        })
        self.fields['email'].widget.attrs.update({
            'autocomplete': 'email',
            'inputmode': 'email',
        })
        self.fields['password1'].widget.attrs.update({'autocomplete': 'new-password'})
        self.fields['password2'].widget.attrs.update({'autocomplete': 'new-password'})

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='Email or Username',
        help_text='You can sign in with either your username or your email address.',
        widget=forms.TextInput(attrs={'autofocus': True, 'autocomplete': 'username'}),
    )
    password = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
        help_text='Passwords are case-sensitive.',
    )
