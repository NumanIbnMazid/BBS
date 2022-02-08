
"""
Custom Signup View (Overrides the default django-allauth)
"""

from allauth.account.views import SignupView
from allauth.account.utils import (
    complete_signup,
)
from allauth.account import app_settings
from allauth.exceptions import ImmediateHttpResponse


class AccountSignupView(SignupView):
    # NOTE: Overrides the default django-allauth signup view
    def form_valid(self, form):
        # By assigning the User to a property on the view, we allow subclasses
        # of SignupView to access the newly created User instance
        self.user = form.save(self.request)
        
        # TODO: Custom Login Implementation here
 
        try:
            return complete_signup(
                self.request,
                self.user,
                app_settings.EMAIL_VERIFICATION,
                self.get_success_url(),
            )
        except ImmediateHttpResponse as e:
            return e.response


account_signup_view = AccountSignupView.as_view()
