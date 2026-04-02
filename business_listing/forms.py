from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from PIL import Image

from .models import Product


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


class ProductForm(forms.ModelForm):
    MAX_IMAGE_SIZE_BYTES = 2 * 1024 * 1024
    MAX_IMAGE_WIDTH = 5000
    MAX_IMAGE_HEIGHT = 5000

    class Meta:
        model = Product
        fields = [
            'product_name',
            'product_image',
            'product_category',
            'tags',
            'price',
            'currency',
            'product_description',
            'terms_of_sale',
        ]
        widgets = {
            'product_name': forms.TextInput(attrs={'maxlength': '255'}),
            'product_category': forms.TextInput(attrs={'maxlength': '100'}),
            'tags': forms.TextInput(attrs={'maxlength': '255'}),
            'price': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
            'product_description': forms.Textarea(attrs={'class': 'materialize-textarea'}),
        }
        help_texts = {
            'product_name': 'Use the name customers would recognize immediately.',
            'product_image': 'Upload a clear product photo if you have one.',
            'product_category': 'Examples: Electronics, Furniture, Bakery, Software.',
            'tags': 'Add comma-separated tags (for example: organic, wholesale, handmade).',
            'price': 'Enter the selling price as a numeric amount.',
            'currency': 'Choose the currency that matches the listed price.',
            'product_description': 'Describe the product, condition, size, or key features.',
            'terms_of_sale': 'Select the most accurate sales condition for this product.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product_name'].label = 'Product Name'
        self.fields['product_image'].label = 'Product Image'
        self.fields['product_category'].label = 'Product Category'
        self.fields['tags'].label = 'Tags'
        self.fields['product_description'].label = 'Product Description'
        self.fields['terms_of_sale'].label = 'Terms of Sale'
        for field in self.fields.values():
            field.required = True
        if self.instance and self.instance.pk and self.instance.product_image:
            self.fields['product_image'].required = False

    def clean_price(self):
        price = self.cleaned_data['price']
        if price is not None and price < 0:
            raise forms.ValidationError('Price cannot be negative.')
        return price

    def clean_product_category(self):
        category = self.cleaned_data['product_category']
        normalized_category = Product.normalize_category(category)
        if not normalized_category:
            raise forms.ValidationError('Product category is required.')
        return normalized_category

    def clean_product_image(self):
        image = self.cleaned_data.get('product_image')
        if not image:
            if self.instance and self.instance.pk and self.instance.product_image:
                return self.instance.product_image
            raise forms.ValidationError('Product image is required.')

        if image.size > self.MAX_IMAGE_SIZE_BYTES:
            raise forms.ValidationError('Image file is too large. Maximum allowed size is 2 MB.')

        try:
            uploaded_image = Image.open(image)
            width, height = uploaded_image.size
        except OSError as exc:
            raise forms.ValidationError('Uploaded file is not a valid image.') from exc
        finally:
            image.seek(0)

        if width > self.MAX_IMAGE_WIDTH or height > self.MAX_IMAGE_HEIGHT:
            raise forms.ValidationError('Image dimensions are too large. Maximum allowed is 5000x5000 pixels.')

        return image

    def clean_product_description(self):
        description = (self.cleaned_data.get('product_description') or '').strip()
        if not description:
            raise forms.ValidationError('Product description is required.')
        return description

    def clean_tags(self):
        tags = (self.cleaned_data.get('tags') or '').strip()
        if not tags:
            raise forms.ValidationError('Tags are required.')
        return tags
