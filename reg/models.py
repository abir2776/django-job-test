from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class subPlan(models.Model):
    title = models.CharField(max_length=150)
    price = models.IntegerField()
    detail_text = models.TextField(max_length=500,default="This is description")

    def __str__(self):
        return self.title

#to track users subscriptins
class usersSub(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    subP=models.OneToOneField(subPlan,on_delete=models.CASCADE)
    subscribeY=models.IntegerField()
    subscribeM=models.IntegerField()
    subscribeD=models.IntegerField()

    def __str__(self):
        return self.subP.title
