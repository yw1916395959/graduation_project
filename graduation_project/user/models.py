from django.db import models


# Create your models here.

class User(models.Model):
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=100)
    user_password = models.CharField(max_length=255)


class Task(models.Model):
    task_id = models.IntegerField()
    task_name = models.CharField(max_length=100)
    task_type = models.IntegerField()
    task_status = models.IntegerField()
    task_detail = models.CharField(max_length=255)
    create_time = models.DateTimeField()
    start_time = models.DateTimeField()
    finish_time = models.DateTimeField()


