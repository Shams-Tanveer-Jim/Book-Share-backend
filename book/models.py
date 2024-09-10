from django.db import models
from django.forms import ValidationError
from account.models import User
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver

class Author(models.Model):
    name = models.CharField(max_length=256,null=False,blank=False)
    bio =  models.CharField(max_length=1024,null=True,blank=True,default='')
    date_of_birth = models.DateField()
    date_of_death = models.DateField(null=True,blank=True)
    image = models.ImageField(upload_to='authors/',null=True,blank=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=256,null=False,blank=False,unique=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self) :
        return self.name
    
class Publisher(models.Model):
    name = models.CharField(max_length=256,null=False,blank=False,unique=True)
    address = models.TextField()
    website = models.URLField()

    def __str__(self):
        return self.name

class Book(models.Model):
    name = models.CharField(max_length=512,null=False,blank=False)
    author = models.ManyToManyField(Author,blank=True,related_name='books')
    category = models.ManyToManyField(Category,blank=True,related_name='books')
    publisher = models.ForeignKey(Publisher,on_delete=models.CASCADE,blank=True,null=True,related_name='books')
    unit = models.IntegerField()
    summary = models.TextField()
    publication_date = models.DateField()
    language = models.CharField(max_length=50)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name}------{self.unit}'
    
class BookImage(models.Model):
    book= models.ForeignKey(Book,related_name='image', on_delete=models.CASCADE)
    image = models.ImageField(upload_to="books/",blank=True)

    def __str__(self):
        return f'{self.book.name}-{self.image}'
    

class BookTransaction(models.Model):

    TRANSACTION_CHOICES = [
        ('Borrow', 'Borrow'),
        ('Return', 'Return'),
        ('Request', 'Request'),
    ]
    book= models.ForeignKey(Book, on_delete=models.CASCADE,related_name='book')
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='user')
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_CHOICES,
        default='Borrow'
    )
    transaction_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(blank=True,null=True)

    _is_updated = False 

    @property
    def is_updated(self):
        return self._is_updated

    @is_updated.setter
    def is_updated(self, value):
        self._is_updated = value


@receiver(pre_save,sender=BookTransaction)
def return_request_check(sender,instance, **kwargs):
    try:
        old_instance = BookTransaction.objects.get(id=instance.id)
        if old_instance.transaction_type != instance.transaction_type:
            instance.is_updated = True
            if old_instance.transaction_type == 'Borrow':
                if instance.transaction_type == 'Request':
                    raise ValidationError("You have already borrowed the book")
            elif old_instance.transaction_type == 'Request':
                if instance.transaction_type == 'Return':
                    raise ValidationError("You need to borrow the book before return")
            elif old_instance.transaction_type == 'Return':
                raise ValidationError('You cannot perform any task on returned book')
        else:
            instance.is_updated = False   
    except BookTransaction.DoesNotExist:
        return None

@receiver(post_save, sender=BookTransaction)
def update_book_unit_on_request(sender,created, instance, **kwargs):
    if created:
        if instance.transaction_type == 'Request':
            instance.due_date = None
            instance.save()
        elif instance.transaction_type == 'Borrow' and instance.is_updated:
            instance.book.unit -=1
            if instance.book.unit ==0:
                instance.book.is_availble= False
            instance.book.save()       
        elif instance.transaction_type == 'Return' :
            instance.delete()
            raise ValidationError('You Need to Borrow Before Return')
    else:
        if instance.transaction_type == 'Request' and instance.due_date is not None:
            instance.due_date = None
            instance.save()
        elif instance.transaction_type == 'Borrow' and instance.is_updated:
            instance.book.unit -=1
            if instance.book.unit ==0:
                instance.book.is_availble= False
            instance.book.save()
        elif instance.transaction_type == 'Return' and instance.is_updated:
            instance.book.unit +=1
            instance.book.save()
        