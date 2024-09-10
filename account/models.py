from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin,Group
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserManager(BaseUserManager):
    def create_user(self, email, password=None,phone=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        
        user = self.model(email=email, **extra_fields)

        user.set_password(password)
        user.save()
        return user
    

    def create_superuser(self, email, password=None,phone=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role','ADMIN')
        print(extra_fields)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password,phone, **extra_fields)

class CustomUser(AbstractBaseUser,PermissionsMixin):

    class ROLE(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        ADMISTRATIVEADMIN = "ADMISTRATIVEADMIN", "AdminstrativeAdmin"
        USER = "USER", "User"


    phone = models.CharField(verbose_name=_("Phone"),  max_length=11)
    name = models.CharField(verbose_name=_("Name"), max_length=300, blank=True, null=True,default='')
    email = models.EmailField(verbose_name=_("Email"), unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    password = models.CharField(max_length=128) 
    role = models.CharField(max_length=20,choices=ROLE.choices,default=ROLE.ADMISTRATIVEADMIN)
    is_staff = models.BooleanField(
        _("Staff status"), default=False, help_text=_("Designates whether the user can log into this admin site.")
    )
    is_active = models.BooleanField(
        _("Active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. " "Unselect this instead of deleting accounts."
        ),
    )

    is_approved = models.BooleanField(
        _("Approved"),
        default=False,
        help_text=_("Designates whether this user has been approved by an admin."),
    )

    
    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    default_choice = ROLE.ADMISTRATIVEADMIN

    class Meta:
        ordering = ("name", "email")

    def __str__(self):
        return f'{self.name} - {self.email}'
    
    def save(self, *args, **kwargs):
        if not self.pk:
         
            self.role = self.default_choice
    
        return super().save(*args, **kwargs)



class User(CustomUser):
    default_choice = CustomUser.ROLE.USER
    class Meta:
        proxy = True


@receiver(post_save,sender= User)
def add_user_to_user_group(sender,created,instance,**kargs):
    
    if created:
        group, _ = Group.objects.get_or_create(name=instance.role)
        instance.groups.add(group)

@receiver(post_save,sender= CustomUser)
def add_custom_user_to_user_group(sender,created,instance,**kargs):
    
    if created:
        group, _ = Group.objects.get_or_create(name=instance.role)
        instance.groups.add(group)