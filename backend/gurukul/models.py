from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from tinymce.models import HTMLField 
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
import datetime
from django.utils import timezone
from django.conf import settings


# Create your models here.
class Classrooms(models.Model):
    classroom_name=models.CharField(max_length=100)
    classroom_subject=models.CharField(max_length=100,default='Vedic Education')
    classroom_language=models.CharField(max_length=100,default='English/Hindi')
    section = models.CharField(max_length=100,default='Third Year')
    class_code = models.CharField(max_length = 10,default='0000000')

    class Meta:
        db_table = 'vish_classrooms'
        managed = False

    def __str__(self):
        return self.classroom_name


class Set(models.Model):
    set_id = models.IntegerField(primary_key=True)
    type= models.CharField(max_length=100,default="generic")
    title = models.CharField(max_length=100)
    titleeng = models.CharField(max_length=100,default="Sanskrit") 
    desc = models.CharField(max_length=500)
    link = models.CharField(max_length=500,default="learn/sanskrit/")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title



class Classmodule(models.Model):
    module_name = models.CharField(max_length=100,null=False)
    classroom = models.ForeignKey(Classrooms,on_delete=models.CASCADE)

    class Meta:
        db_table = 'vish_classmodule'
        managed = False



class Feed(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=20)
    owner_class = models.ForeignKey(Classrooms,on_delete=models.CASCADE) 
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    generic_reference = GenericForeignKey('content_type', 'object_id')

    class Meta:
        db_table = 'vish_feed'
        managed = False

class Students(models.Model):
    student_id=models.ForeignKey(User,on_delete=models.CASCADE)
    classroom_id=models.ForeignKey(Classrooms,on_delete=models.CASCADE)
    class_color = models.CharField(max_length=50)

    class Meta: 
        db_table = 'vish_students'

class Teachers(models.Model):
    teacher_id=models.ForeignKey(User,on_delete=models.CASCADE)
    classroom_id=models.ForeignKey(Classrooms,on_delete=models.CASCADE)
    class_color = models.CharField(max_length=50)

    class Meta:
        db_table = 'vish_teachers'
        managed = False

class Assignments(models.Model):
    assignment_name=models.CharField(max_length=500)
    classroom_id=models.ForeignKey(Classrooms,on_delete=models.CASCADE)
    due_date=models.DateField()
    due_time=models.TimeField(default=timezone.now)
    posted_date=models.DateField(auto_now_add=True)
    instructions=models.TextField()
    vedicdata = models.CharField(max_length=1000, default='Sanskrit')
    total_marks=models.IntegerField(default=100)
    assgn_embedimg = models.ImageField(null=True, blank=True, upload_to="assgnimg/")
    assgn_embeddocument = models.FileField(null=True, blank=True,upload_to="assgndocuments/")
    assgn_embedyturl = models.JSONField( blank=True,default=dict)
    assgn_embedurl = models.JSONField( blank=True,default=dict)
    module_id = models.ForeignKey(Classmodule,on_delete=models.CASCADE) 

    def __str__(self):
        return self.assignment_name
    
    class Meta:
        db_table = 'vish_assignments'
        managed = False


class QnA(models.Model):
    classroom_id = models.ForeignKey(Classrooms,on_delete=models.CASCADE)
    Content = models.JSONField(null=True,default=dict)
    timestamp = models.DateTimeField(auto_now=True)
    total_marks = models.IntegerField(default=25)
    module_id = models.ForeignKey(Classmodule,on_delete=models.CASCADE) 

    class Meta:
        db_table = 'vish_qna'
        managed = False


class Announcements(models.Model):
    clasroom_id = models.ForeignKey(Classrooms,on_delete=models.CASCADE)
    creater = models.ForeignKey(User,on_delete=models.CASCADE)
    announcements = models.CharField(max_length=150,default="Submit Assignment")
    timestamp = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        db_table = 'vish_announcements'
        managed = False

class Submission_base(models.Model):
    student_id=models.ForeignKey(Students,on_delete=models.CASCADE)
    submitted_date=models.DateField(auto_now_add=True)
    submitted_time=models.TimeField(auto_now_add=True)
    submitted_on_time=models.BooleanField(default=True)
    marks_alloted=models.IntegerField(default=0)

    class Meta:
        abstract = True

class Submissions(Submission_base):
    assignment_id=models.ForeignKey(Assignments,on_delete=models.CASCADE)
    submission_file = models.FileField(upload_to='gurukul/documents')
    write_up = HTMLField(max_length=800,default="Please be lenient")

    class Meta:
        db_table = 'vish_submissions'
        managed = False

class QSubmissions(Submission_base):
    question_id=models.ForeignKey(QnA,on_delete=models.CASCADE)
    write_up = HTMLField(max_length=800,default="Please be lenient")
    option = models.JSONField(null=True,default=dict)

    class Meta:
        db_table = 'vish_qsubmissions'
        managed = False


class Material(models.Model):
    material_name=models.CharField(max_length=500)
    classroom_id=models.ForeignKey(Classrooms,on_delete=models.CASCADE)
    prepared_date=models.DateField()
    prepared_time=models.TimeField(default=datetime.time(10,10))
    posted_date=models.DateField(auto_now_add=True)
    material_instructions=models.TextField()
    material_grammardata = models.ForeignKey(Set,on_delete=models.CASCADE)
    material_vedicdata = models.JSONField()
    material_embedimg = models.ImageField(null=True, blank=True, upload_to="materialimg/")
    material_embeddocument = models.FileField(null=True, blank=True,upload_to="materialdocuments/")
    material_embedyturl = models.JSONField()
    material_embedurl = models.JSONField()
    module_id = models.ForeignKey(Classmodule,on_delete=models.CASCADE) 


    def __str__(self):
        return self.material_name
    
    class Meta:
        db_table = 'vish_material'
        managed = False
