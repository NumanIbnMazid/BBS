from django import forms
from users.models import Husband, User
from posts.models import Post
from django.conf import settings
import re
from django.core.exceptions import ValidationError
# from util.helpers import validate_chars, simple_form_widget
from ckeditor.widgets import CKEditorWidget
from django.core.files.uploadedfile import UploadedFile
from django.db.models.fields.files import ImageFieldFile
from django.template.defaultfilters import filesizeformat
import os

# # -------------------------------------------------------------------
# #                              User
# # -------------------------------------------------------------------
class UserManageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserManageForm, self).__init__(*args, **kwargs)

        GENDER_CHOICES = (
            ('', '--- Select Gender ---'),
            (0, 'Male'),
            (1, 'Female'),
            (2, 'Other'),
        )

        gender = forms.ChoiceField(
            choices=GENDER_CHOICES, label="Gender", initial='',
            widget=forms.Select(), required=True
        )
        self.fields['marriage_experience'].widget.attrs.update({
            'id': 'marriage_experience',
            'placeholder': 'Enter Marriage Experience...',
            'rows': 10,
            'cols': 30,
        })
        self.fields['purpose_of_use'].widget.attrs.update({
            'id': 'purpose_of_use',
            'placeholder': 'Enter Purpose of Use...',
            'rows': 10,
            'cols': 30,
        })
    class Meta:
        model = User
        fields = ['name','gender','contact_number','age',
                 'address','marriage_experience','purpose_of_use']
        widgets = {
            'marriage_experience': CKEditorWidget(),
        }
        widgets = {
            'purpose_of_use': CKEditorWidget(),
        }

# # -------------------------------------------------------------------
# #                              Husband
# # -------------------------------------------------------------------

class HusbandManageForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(HusbandManageForm, self).__init__(*args, **kwargs)

        self.fields['name'].widget.attrs.update({
            'placeholder': 'Full Name'
        })
        self.fields['nationality'].widget.attrs.update({
            'placeholder': 'Nationality'
        })
        self.fields['address'].widget.attrs.update({
            'placeholder': 'Address'
        })
        self.fields['dob'].widget.attrs.update({
            'placeholder': 'YYYY-MM-DD'
        })

    class Meta:
        model = Husband
        fields = '__all__'
        exclude = ['slug','user']

class PostManageForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PostManageForm, self).__init__(*args, **kwargs)

        self.fields['title'].widget.attrs.update({
            'placeholder': 'Title'
        })

    class Meta:
        model = Post
        fields = '__all__'
        exclude = ['slug','user','weight','allowed_users']

        widgets = {
            'description': CKEditorWidget(),
        }
