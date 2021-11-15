from django.db import models
import uuid
# Create your models here.
class Video(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    title = models.TextField()
    description = models.TextField()
    thumbnail = models.URLField()
    date = models.DateField(null=True)
    width = models.IntegerField(null=True)
    height = models.IntegerField(null=True)
    category = models.TextField(null=True)

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name_plural = 'Videos'