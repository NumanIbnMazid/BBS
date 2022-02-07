from django import forms
from plans.models import PointPlan, FlatRatePlan, UserWalletTransaction
from django_select2 import forms as s2forms
from bbs.utils import translate_to_jp


""" 
-------------------------------------------------------------------
                           ** PointPlan ***
-------------------------------------------------------------------
"""


class PointPlanManageForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PointPlanManageForm, self).__init__(*args, **kwargs)

        self.fields['title'].widget.attrs.update({
            'placeholder': translate_to_jp('Enter Point Plan Title...'),
            'maxlength': 150
        })
    CURRENCY_CHOICES = (
        (0, translate_to_jp('Yen')),
        (1, translate_to_jp('Dollar'))
    )
    currency = forms.ChoiceField(
        required=False, help_text='Select your Currency.', choices=CURRENCY_CHOICES)

    class Meta:
        model = PointPlan
        fields = [
            "title", "point", "price", "currency"
        ]

""" 
-------------------------------------------------------------------
                        ** FlatRatePlan ***
-------------------------------------------------------------------
"""


class FlatRatePlanManageForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(FlatRatePlanManageForm, self).__init__(*args, **kwargs)

        self.fields['title'].widget.attrs.update({
            'placeholder': 'Enter Flat Rate Plan Title...',
            'maxlength': 150
        })
    CURRENCY_CHOICES = (
        (0, 'Yen'),
        (1, 'Dollar')
    )
    EXPIRATION_CYCLE_CHOICES = (
        (0, 'Monthly'),
        (1, 'Yearly'),
        (2, 'Half-Yearly')
    )
    currency = forms.ChoiceField(
       help_text='Select your Currency.', choices=CURRENCY_CHOICES)
    expiration_cycle = forms.ChoiceField(
         help_text='Select your Expiration Cycle.', choices=EXPIRATION_CYCLE_CHOICES)

    class Meta:
        model = FlatRatePlan
        fields = [
            "title", "price", "currency", "expiration_cycle"
        ]


""" 
-------------------------------------------------------------------
                    ** UserWalletTransaction ***
-------------------------------------------------------------------
"""


class UserWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "username__icontains",
        "email__icontains",
        "contact_number__icontains",
    ]

class UserWalletTransactionManageForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(UserWalletTransactionManageForm, self).__init__(*args, **kwargs)

        # self.fields['user'].widget.attrs.update({
        #     'placeholder': 'Search User Name or Email or Contact Number...',
        #     'maxlength': 150
        # })

    class Meta:
        model = UserWalletTransaction
        fields = [
            "user", "transaction_type", "point_plan", "flat_rate_plan"
        ]
        widgets = {
            "user": UserWidget
        }
