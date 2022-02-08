from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from bbs.utils import simple_random_string, unique_slug_generator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from bbs.helpers import get_dynamic_fields
from bbs.utils import autoslugFromUUID
from users.image_upload_helper import upload_user_image


def generate_username_from_email(email):
    return email.split("@")[0][:15] + "__" + simple_random_string()

class UserManager(BaseUserManager):

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        user = self._create_user(email, password, True, True, **extra_fields)
        user.save(using=self._db)
        return user


@autoslugFromUUID()
class User(AbstractBaseUser, PermissionsMixin):

    class Gender(models.IntegerChoices):
        MALE = 0, _("Male")
        FEMALE = 1, _("Female")
        OTHERS = 2, _("Others")

    class MembershipType(models.IntegerChoices):
        REGULAR = 0, _("Regular")
        SENIOR = 1, _("Senior")

    email = models.EmailField(
        max_length=254, unique=True
    )
    username = models.CharField(
        max_length=254, unique=True
    )
    slug = models.SlugField(unique=True, max_length=254)
    name = models.CharField(
        max_length=254, null=True, blank=True
    )
    image = models.ImageField(upload_to=upload_user_image, null=True, blank=True)
    gender = models.SmallIntegerField(
        choices=Gender.choices, default=1
    )
    contact_number = models.CharField(
        max_length=30, blank=True, null=True
    )
    # dob = models.DateField(
    #     blank=True, null=True, verbose_name="date of birth"
    # )
    age = models.PositiveIntegerField(blank=True, null=True)
    address = models.CharField(
        max_length=254, blank=True, null=True
    )
    membership_type = models.SmallIntegerField(
        choices=MembershipType.choices, default=0
    )
    marriage_experience = models.TextField(
        blank=True, null=True
    )
    purpose_of_use = models.TextField(
        blank=True, null=True
    )
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = ("User")
        verbose_name_plural = ("Users")
        ordering = ["-date_joined"]

    def get_absolute_url(self):
        return "/users/%i/" % (self.pk)

    def __str__(self):
        return self.get_dynamic_username()
    
    def get_dynamic_username(self):
        """ Get a dynamic username for a specific user instance. if the user has a name then returns the name, if the user does not have a name but has a username then return username, otherwise returns email as username """
        if not self.name == None and not self.name == "":
            return self.name
        elif not self.username == None and not self.username == "":
            return self.username
        return self.email

    def get_membership_type(self):
        if self.membership_type == 1:
            return "Senior"
        return "Regular"

    def get_gender(self):
        if self.gender == 0:
            return "Male"
        elif self.gender == 1:
            return "Female"
        return "Others"
    
    def get_fields(self):
        def get_dynamic_fields(field):
            if field.name == 'gender':
                return (field.name, self.get_gender(), field.get_internal_type())
            elif field.name == 'membership_type':
                return (field.name, self.get_membership_type(), field.get_internal_type())
            else:
                return (field.name, field.value_from_object(self), field.get_internal_type())
        return [get_dynamic_fields(field) for field in self.__class__._meta.fields]


@receiver(pre_save, sender=User)
def update_username_from_email(sender, instance, **kwargs):
    """ Generates and updates username from user email and updates slug on User pre_save hook """
    instance.username = generate_username_from_email(email=instance.email)


@autoslugFromUUID()
class UserWallet(models.Model):
    user = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, related_name="user_wallet_user"
    )
    slug = models.SlugField(unique=True, max_length=254)
    available_points = models.PositiveIntegerField(
        default=0
    )
    is_in_flat_plan = models.BooleanField(
        default=False
    )
    flat_plan_created_at = models.DateTimeField(
        null=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='created at'
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='updated at'
    )

    class Meta:
        verbose_name = ("User Wallet")
        verbose_name_plural = ("User Wallets")
        ordering = ["-created_at"]

    def __str__(self):
        return self.user.get_dynamic_username()
    
    def get_fields(self):
        def get_dynamic_fields(field):
            if field.name == 'user':
                return (field.name, self.get_dynamic_username(), field.get_internal_type())
            else:
                return (field.name, field.value_from_object(self), field.get_internal_type())
        return [get_dynamic_fields(field) for field in self.__class__._meta.fields]


@receiver(post_save, sender=User)
def assign_user_wallet_on_post_save(sender, instance, **kwargs):
    """ Assigns Wallet to User on User post_save hook """
    try:
        # NOTE: check if created (Otherwise it will be called twice on created and saved hook)
        if kwargs['created']:
            user_wallet = UserWallet.objects.create(
                user=instance
            )
            # assign 200 points to user on signup
            user_wallet.available_points = 200
            # save user wallet
            user_wallet.save()
            
    except Exception as E:
        raise Exception(
            f"Failed to create user wallet! Exception: {str(E)}"
        )


@autoslugFromUUID()
class Husband(models.Model):
    user = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, related_name="user_husband"
    )
    slug = models.SlugField(unique=True, max_length=254)
    name = models.CharField(
        max_length=100
    )
    nationality = models.CharField(
        max_length=50
    )
    address = models.CharField(
        max_length=254, blank=True, null=True
    )
    # dob = models.DateField(
    #     blank=True, null=True, verbose_name="Date of Birth"
    # )
    age = models.PositiveIntegerField(blank=True, null=True)
    characteristics = models.TextField(
        blank=True, null=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='created at'
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='updated at'
    )

    class Meta:
        verbose_name = ("User Husband")
        verbose_name_plural = ("User Husbands")
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_fields(self):
        def get_dynamic_fields(field):
            if field.name == 'user':
                return (field.name, self.get_dynamic_username(), field.get_internal_type())
            else:
                return (field.name, field.value_from_object(self), field.get_internal_type())
        return [get_dynamic_fields(field) for field in self.__class__._meta.fields]


class UserCostTransaction(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="user_cost_transaction_users"
    )
    post = models.ForeignKey(to='posts.Post', on_delete=models.CASCADE, related_name='user_cost_transaction_posts',
                             )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='created at'
    )

    class Meta:
        verbose_name = ("User Cost Transaction")
        verbose_name_plural = ("User Cost Transactions")
        ordering = ["-created_at"]

    def __str__(self):
        return self.get_dynamic_username()

    def get_fields(self):
        def get_dynamic_fields(field):
            if field.name == 'user':
                return (field.name, self.get_dynamic_username(), field.get_internal_type())
            else:
                return (field.name, field.value_from_object(self), field.get_internal_type())
        return [get_dynamic_fields(field) for field in self.__class__._meta.fields]
