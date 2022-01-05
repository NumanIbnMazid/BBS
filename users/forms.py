from django import forms
from allauth.account.forms import LoginForm


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields['login'].widget = forms.EmailInput(
            attrs={
                'autocomplete': 'off', 'placeholder': 'Email Address', 'class': 'block w-full mb-4 text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-app-theme-400 focus:outline-none focus:shadow-outline-app-theme dark:text-gray-300 dark:focus:shadow-outline-gray form-input'
            }
        )
        self.fields['password'].widget = forms.PasswordInput(
            attrs={
                'autocomplete': 'off', 'placeholder': 'Password', 'class': 'block w-full mb-4 text-sm dark:border-gray-600 dark:bg-gray-700 focus:border-app-theme-400 focus:outline-none focus:shadow-outline-app-theme dark:text-gray-300 dark:focus:shadow-outline-gray form-input'
            }
        )

        # remove remember field checkbox and render manually in form
        if 'remember' in self.fields.keys():
            del self.fields['remember']

    def clean(self):
        cleaned_data = super(CustomLoginForm, self).clean()

        # remember me
        remember = False
        if self.request.POST.get('remember', None) == "on":
            remember = True
        self.cleaned_data.update({'remember': remember})

        # return cleaned data
        return cleaned_data
