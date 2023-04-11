from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from authentication.models import User


class About(models.Model):
    content = models.TextField()
    is_verified = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='abouts_created')
    verified_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='abouts_verified', null=True, blank=True)
    verified_date = models.DateTimeField(null=True, blank=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    related_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.content

    def save(self, *args, **kwargs):
        self.content = self.content.strip()
        super(About, self).save(*args, **kwargs)

    def get_content_preview(self):
        return self.content[:50]

    def get_related_object(self):
        return self.related_object

    @staticmethod
    def create_about(content, creator, related_object):
        about = About.objects.create(content=content, created_by=creator, content_type=ContentType.objects.get_for_model(related_object), object_id=related_object.id)
        AboutRelationship.objects.create(about=about, content_type=ContentType.objects.get_for_model(related_object), object_id=related_object.id)
        return about

class AboutRelationship(models.Model):
    about = models.ForeignKey(About, on_delete=models.CASCADE, related_name='relationships')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    related_object = GenericForeignKey('content_type', 'object_id')

    @staticmethod
    def relate_to_model(model_class):
        ct = ContentType.objects.get_for_model(model_class)
        about = About.objects.create(content_type=ct, object_id=model_class.pk)
        AboutRelationship.objects.create(about=about, content_type=ct, object_id=model_class.pk)
        return about
