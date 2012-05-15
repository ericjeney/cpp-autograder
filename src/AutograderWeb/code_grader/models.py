from django.db import models
import datetime
import random
import string

# Create your models here.

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    answer = models.CharField(max_length=200)
    testcases = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    random = models.CharField(max_length=10, blank=True, editable=False)
    
    def save(self):
        if not self.id:
            while True:
                st = "".join(random.sample(string.letters+string.digits, 10))
                if Quiz.objects.filter(random__exact=st).count() == 0:
                    self.random = st
                    break
        super(Quiz, self).save()
    
    def __unicode__(self):
        return self.title
                    

class Submission(models.Model):
    quiz = models.ForeignKey(Quiz)
    student = models.CharField(max_length=100)
    time = models.DateTimeField()
    
    graded = models.BooleanField(default=False)
    status = models.CharField(max_length=20)
    file = models.CharField(max_length=200)
    didPass = models.BooleanField(blank=True)
    didFail = models.BooleanField(default=False)
    runtime = models.IntegerField(default=0)
    
    randomness = models.CharField(max_length=20)
    type = models.CharField(max_length=4)
    name = models.CharField(max_length=50)
    
    def save(self):
        if not self.id:
            self.time = datetime.datetime.now()
        super(Submission, self).save()