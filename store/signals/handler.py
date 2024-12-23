from store.models import Customer
from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver

#the function is called signal handler
@receiver(post_save,sender=settings.AUTH_USER_MODEL)
def create_customer_for_new_user(sender,**kwargs):
    if kwargs['created']:
        Customer.objects.create(user=kwargs['instance'])