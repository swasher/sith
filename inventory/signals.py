from django.db.models.signals import post_delete
from django.dispatch import receiver
from cloudinary.uploader import destroy
from .models import Image


@receiver(post_delete, sender=Image)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Deletes file from cloudinary
    when corresponding `Image` object is deleted.
    """
    destroy(instance.picture.public_id)