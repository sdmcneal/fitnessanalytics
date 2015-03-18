from django.db import models

# Create your models here.
class UAUser(models.Model):
    display_name = models.CharField(max_length=200)
    user_id = models.IntegerField(default=0)
    def __str__(self):
        return self.display_name

