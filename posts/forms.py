from django import forms
from posts.models import Thread, Post
from ckeditor.widgets import CKEditorWidget
import os
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.db.models.fields.files import ImageFieldFile
from django.template.defaultfilters import filesizeformat

""" 
-------------------------------------------------------------------
                           ** Thread ***
-------------------------------------------------------------------
"""


class ThreadManageForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ThreadManageForm, self).__init__(*args, **kwargs)

        self.fields['title'].widget.attrs.update({
            'placeholder': 'Enter Thread Title...',
            'maxlength': 150
        })

    class Meta:
        model = Thread
        fields = [
            "title", "image", "weight", "description"
        ]
        widgets = {
            'description': CKEditorWidget(),
        }
        
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and isinstance(image, UploadedFile):
            file_extension = os.path.splitext(image.name)[1]
            allowed_image_types = settings.ALLOWED_IMAGE_TYPES
            content_type = image.content_type.split('/')[0]
            if not file_extension in allowed_image_types:
                raise forms.ValidationError("Only %s file formats are supported! Current logo format is %s" % (
                    allowed_image_types, file_extension))
            if image.size > settings.MAX_UPLOAD_SIZE:
                raise forms.ValidationError("Please keep filesize under %s. Current filesize %s" % (
                    filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(image.size)))
            return image
        return None

# #........................... **** ...........................
# #........................... Post ...........................
# #........................... **** ...........................

class PostManageForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PostManageForm, self).__init__(*args, **kwargs)

        self.fields['weight'].widget.attrs.update({
            'placeholder': 'Enter Post Weight...'
        })

    class Meta:
        model = Post
        fields = [
            'weight'
        ]
