from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import CheckConstraint, Q
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from users.models import UserWallet
from django.utils import timezone
from bbs.utils import autoslugFromUUID, translate_to_jp


""" 
-------------------------------------------------------------------
                        ** PointPlan ***
-------------------------------------------------------------------
"""


@autoslugFromUUID()
class PointPlan(models.Model):
    class Currency(models.IntegerChoices):
        YEN = 0, _("Yen")
        DOLLAR = 1, _("Dollar")
    title = models.CharField(
        max_length=254, unique=True
    )
    slug = models.SlugField(unique=True, max_length=254)
    point = models.PositiveIntegerField(
        default=0
    )
    price = models.FloatField(
        default=0, validators=[MinValueValidator(0.0)]
    )
    currency = models.SmallIntegerField(
        choices=Currency.choices, default=0
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='created at'
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='updated at'
    )

    class Meta:
        verbose_name = ("Point Plan")
        verbose_name_plural = ("Point Plans")
        ordering = ["-created_at"]
        constraints = (
            # for checking in the DB
            CheckConstraint(
                check=Q(price__gte=0.0),
                name='point_plan_price_float_range'
            ),
        )

    def __str__(self):
        return self.title

    def get_fields(self):
        def get_dynamic_fields(field):
            if field.name == 'currency':
                return (field.name, self.get_currency_icon_class(), field.get_internal_type())
            else:
                return (field.name, field.value_from_object(self), field.get_internal_type())
        return [get_dynamic_fields(field) for field in self.__class__._meta.fields]

    def get_currency_icon_class(self):
        if self.currency == 1:
            return "<i class='fas fa-dollar-sign'></i>"
        return "<i class='fas fa-yen-sign'></i>"

    def get_currency_str(self):
        if self.currency == 1:
            return "USD"
        return "YEN"


""" 
-------------------------------------------------------------------
                            ** FlatRatePlan ***
-------------------------------------------------------------------
"""


@autoslugFromUUID()
class FlatRatePlan(models.Model):
    class Currency(models.IntegerChoices):
        YEN = 0, _("Yen")
        DOLLAR = 1, _("Dollar")
    class ExpirationCycle(models.IntegerChoices):
        MONTHLY = 0, _("Monthly")
        YEARLY = 1, _("Yearly")
        HALF_YEARLY = 2, _("Half-Yearly")

    title = models.CharField(
        max_length=254, unique=True
    )
    slug = models.SlugField(unique=True, max_length=254)
    price = models.FloatField(
        default=0, validators=[MinValueValidator(0.0)]
    )
    currency = models.SmallIntegerField(
        choices=Currency.choices, default=0
    )
    expiration_cycle = models.SmallIntegerField(
        choices=ExpirationCycle.choices, default=0
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='created at'
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='updated at'
    )

    class Meta:
        verbose_name = ("Flat Rate Plan")
        verbose_name_plural = ("Flat Rate Plans")
        ordering = ["-created_at"]
        constraints = (
            # for checking in the DB
            CheckConstraint(
                check=Q(price__gte=0.0),
                name='flat_rate_plan_price_float_range'
            ),
        )

    def __str__(self):
        return self.title

    def get_fields(self):
        def get_dynamic_fields(field):
            if field.name == 'currency':
                return (field.name, self.get_currency_icon_class(), field.get_internal_type())
            elif field.name == 'expiration_cycle':
                return (field.name, self.get_expiration_cycle_str(), field.get_internal_type())
            else:
                return (field.name, field.value_from_object(self), field.get_internal_type())
        return [get_dynamic_fields(field) for field in self.__class__._meta.fields]

    def get_currency_icon_class(self):
        """
        get currency icon class based on currency
        return => str
        """
        if self.currency == 1:
            return "<i class='fas fa-dollar-sign'></i>"
        return "<i class='fas fa-yen-sign'></i>"

    def get_currency_str(self):
        """
        get string representaion of currency
        return => str
        """
        if self.currency == 1:
            return 'Dollar'
        return 'Yen'

    def get_expiration_cycle_str(self):
        """
        get string representation of expiration cycle
        return => str
        """
        if self.expiration_cycle == 1:
            return "Yearly"
        elif self.expiration_cycle == 2:
            return "Half-Yearly"
        return "Monthly"

    def get_is_expired(self):
        """
        get if flat rate plan has already expired or not
        return => bool
        """
        is_expired = True
        current_datetime = timezone.now()
        timedelta_days = (current_datetime - self.created_at).days
        if self.expiration_cycle == 0:
            if timedelta_days <= 30:
                is_expired = False
        if self.expiration_cycle == 1:
            if timedelta_days <= 365:
                is_expired = False
        if self.expiration_cycle == 2:
            if timedelta_days <= 182.5:
                is_expired = False
        return is_expired


""" 
-------------------------------------------------------------------
                    ** UserWalletTransaction ***
-------------------------------------------------------------------
"""


@autoslugFromUUID()
class UserWalletTransaction(models.Model):
    class TransactionType(models.IntegerChoices):
        POINT = 0, _("Point")
        FLATRATE = 1, _("Flat Rate")

    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="user_wallet_transaction_users"
    )
    slug = models.SlugField(unique=True, max_length=254)
    transaction_type = models.PositiveSmallIntegerField(
        default=0, choices=TransactionType.choices
    )
    point_plan = models.ForeignKey(
        PointPlan, on_delete=models.CASCADE, related_name="user_wallet_transaction_point_plans", blank=True, null=True
    )
    flat_rate_plan = models.ForeignKey(
        FlatRatePlan, on_delete=models.CASCADE, related_name="user_wallet_transaction_flat_rate_plans", blank=True, null=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='created at'
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='updated at'
    )

    class Meta:
        verbose_name = ("UserWalletTransaction")
        verbose_name_plural = ("UserWalletTransactions")
        ordering = ["-created_at"]
    
    def __str__(self):
        return self.user.get_dynamic_username()

    def get_transaction_type_str(self):
        """
        get string representation of transaction type
        return => str
        """
        if self.transaction_type == 1:
            return "Flat Rate"
        return "Point"

    def get_fields(self):
        def get_dynamic_fields(field):
            if field.name == 'user':
                return (field.name, self.user.get_dynamic_username(), field.get_internal_type())
            elif field.name == 'transaction_type':
                return (field.name, self.get_transaction_type_str(), field.get_internal_type())
            elif field.name == 'point_plan':
                return (field.name, self.point_plan.title if not self.point_plan == None else "-", field.get_internal_type())
            elif field.name == 'flat_rate_plan':
                return (field.name, self.flat_rate_plan.title if not self.flat_rate_plan == None else "-", field.get_internal_type())
            else:
                return (field.name, field.value_from_object(self), field.get_internal_type())
        return [get_dynamic_fields(field) for field in self.__class__._meta.fields]



# # -------------------------------------------------------------------
# #                  Pre-Save Post-Save Configurations
# # -------------------------------------------------------------------


@receiver(post_save, sender=UserWalletTransaction)
def update_user_wallet_on_post_save(sender, instance, **kwargs):
    """ Updates User Wallet on User Wallet Transaction's post_save hook """
    try:
        def update_user_wallet():
            # check if user wallet exists
            user_wallet_qs = UserWallet.objects.filter(user=instance.user)
            if user_wallet_qs.exists():
                # get user wallet instance
                user_wallet = user_wallet_qs.last()
                # get transaction type to update on user wallet
                transactionType = instance.transaction_type
                # check if transaction type is point plan
                if transactionType == 0:
                    # calculate point
                    calculated_points = user_wallet.available_points + instance.point_plan.point
                    # update user wallet
                    user_wallet_qs.update(
                        available_points=calculated_points
                    )
                # check if transaction type is flat rate plan
                elif transactionType == 1:
                    user_wallet_qs.update(
                        is_in_flat_plan=True,
                        flat_plan_created_at=timezone.now()
                    )
                # raise exception for improper transaction type
                else:
                    raise ValueError(
                        f"Invalid transaction type {transactionType}. Availabe transaction types are [0: Point Plan, 1: Flat Rate Plan]"
                    )
            # create user wallet if not found
            else:
                UserWallet.objects.create(
                    user=instance.user
                )
                update_user_wallet()
            pass
        
        # check if created (Otherwise it will be called twice on created and saved hook)
        if kwargs['created']:
            update_user_wallet()
            
    except Exception as E:
        raise Exception(
            f"Failed to update user wallet! Exception: {str(E)}"
        )


@receiver(pre_delete, sender=UserWalletTransaction)
def update_user_wallet_on_pre_delete(sender, instance, **kwargs):
    """ Updates User Wallet on User Wallet Transaction's pre_delete hook """
    try:
        def update_user_wallet():
            # check if user wallet exists
            user_wallet_qs = UserWallet.objects.filter(user=instance.user)
            if user_wallet_qs.exists():
                # get user wallet instance
                user_wallet = user_wallet_qs.last()
                # get transaction type to update on user wallet
                transactionType = instance.transaction_type
                # check if transaction type is point plan
                if transactionType == 0:
                    # calculate point
                    calculated_points = max(user_wallet.available_points - instance.point_plan.point, 0)
                    # update user wallet
                    user_wallet_qs.update(
                        available_points=calculated_points
                    )
                # check if transaction type is flat rate plan
                elif transactionType == 1:
                    user_wallet_qs.update(
                        is_in_flat_plan=False,
                        flat_plan_created_at=None
                    )
                # raise exception for improper transaction type
                else:
                    raise ValueError(
                        f"Invalid transaction type {transactionType}. Availabe transaction types are [0: Point Plan, 1: Flat Rate Plan]"
                    )
            # create user wallet if not found
            else:
                UserWallet.objects.create(
                    user=instance.user
                )
                update_user_wallet()
            pass
        
        # Finally update the user wallet
        update_user_wallet()
            
    except Exception as E:
        raise Exception(
            f"Failed to update user wallet! Exception: {str(E)}"
        )
