from enum import Enum
import uuid
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
    # identifier = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    learningPath = models.ManyToManyField('LearningPath', through='Gurukul_LearningPath')

    # class Meta:
    #     db_table = 'vish_classrooms'
    #     managed = False

    def __str__(self):
        return self.classroom_name


class Gurukul_LearningPath(models.Model):
    gurukul = models.ForeignKey(Classrooms,on_delete= models.CASCADE,related_name='gurukul_learningpaths')
    learningpath = models.ForeignKey('LearningPath',on_delete=models.CASCADE, related_name='learningpath_gurukuls')
    dateAdded = models.DateTimeField(default=datetime.datetime.now)


# class Set(models.Model):
#     set_id = models.IntegerField(primary_key=True)
#     type= models.CharField(max_length=100,default="generic")
#     title = models.CharField(max_length=100)
#     titleeng = models.CharField(max_length=100,default="Sanskrit") 
#     desc = models.CharField(max_length=500)
#     link = models.CharField(max_length=500,default="learn/sanskrit/")
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.title


class Feed(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=20)
    owner_class = models.ForeignKey(Classrooms, on_delete=models.CASCADE) 
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    generic_reference = GenericForeignKey('content_type', 'object_id')
    

    def __str__(self):
        return self.category
    # class Meta:
    #     db_table = 'vish_feed'
    #     managed = False

class Students(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    classroom=models.ManyToManyField(Classrooms)
    class_color = models.CharField(max_length=50)

    # class Meta: 
    #     db_table = 'vish_students'

class Teachers(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    classroom=models.ManyToManyField(Classrooms)
    class_color = models.CharField(max_length=50, default='#FFE8EE')

 #   class Meta:
#         db_table = 'vish_teachers'
#         managed = False


## Base model for assignments, quiz and test with minor filed changes in each.

# class Assignments(models.Model):
#     assignment_name=models.CharField(max_length=500)
#     classroom_id=models.ForeignKey(Classrooms,on_delete=models.CASCADE)
#     due_date=models.DateField()
#     due_time=models.TimeField(default=timezone.now)
#     posted_date=models.DateField(auto_now_add=True)
#     instructions=models.TextField()
#     vedicdata = models.CharField(max_length=1000, default='Sanskrit')
#     total_marks=models.IntegerField(default=100)
#     assgn_embedimg = models.ImageField(null=True, blank=True, upload_to="assgnimg/")
#     assgn_embeddocument = models.FileField(null=True, blank=True,upload_to="assgndocuments/")
#     assgn_embedyturl = models.JSONField( blank=True,default=dict)
#     assgn_embedurl = models.JSONField( blank=True,default=dict)
#     # module_id = models.ForeignKey(Classmodule,on_delete=models.CASCADE) 

#     def __str__(self):
#         return self.assignment_name
    
#     class Meta:
#         db_table = 'vish_assignments'
#         managed = False


class QnA(models.Model):
    content = models.JSONField(null=True,default=dict)
    timestamp = models.DateTimeField(auto_now=True)
    total_marks = models.IntegerField(default=25)
    classroom = models.ForeignKey(Classrooms,on_delete=models.CASCADE)
    creator = models.ForeignKey(Teachers,on_delete=models.CASCADE)
    
    #  class Meta:
    #      db_table = 'vish_qna'
    #      managed = False


# ####   Appy throttling to avoid spamming by students
class Announcements(models.Model):
    classroom = models.ForeignKey(Classrooms,on_delete=models.CASCADE)
    creator = models.ForeignKey(User,on_delete=models.CASCADE)
    announcements = models.CharField(max_length=150,default="Reminder to clear backlogs")
    timestamp = models.DateTimeField(auto_now=True, auto_now_add=False)

#     class Meta:
#         db_table = 'vish_announcements'
#         managed = False

# class Submission_base(models.Model):
#     student_id=models.ForeignKey(Students,on_delete=models.CASCADE)
#     submitted_date=models.DateField(auto_now_add=True)
#     submitted_time=models.TimeField(auto_now_add=True)
#     submitted_on_time=models.BooleanField(default=True)
#     marks_alloted=models.IntegerField(default=0)

#     class Meta:
#         abstract = True

# class Submissions(Submission_base):
#     assignment_id=models.ForeignKey(Assignments,on_delete=models.CASCADE)
#     submission_file = models.FileField(upload_to='gurukul/documents')
#     write_up = HTMLField(max_length=800,default="Please be lenient")

#     class Meta:
#         db_table = 'vish_submissions'
#         managed = False


# class Material(models.Model):
#     material_name=models.CharField(max_length=500)
#     classroom_id=models.ForeignKey(Classrooms,on_delete=models.CASCADE)
#     prepared_date=models.DateField()
#     prepared_time=models.TimeField(default=datetime.time(10,10))
#     posted_date=models.DateField(auto_now_add=True)
#     material_instructions=models.TextField()
#     material_grammardata = models.ForeignKey(Set,on_delete=models.CASCADE)
#     material_vedicdata = models.JSONField()
#     material_embedimg = models.ImageField(null=True, blank=True, upload_to="materialimg/")
#     material_embeddocument = models.FileField(null=True, blank=True,upload_to="materialdocuments/")
#     material_embedyturl = models.JSONField()
#     material_embedurl = models.JSONField()
#     module_id = models.ForeignKey(Classmodule,on_delete=models.CASCADE) 


#     def __str__(self):
#         return self.material_name
    
#     class Meta:
#         db_table = 'vish_material'
#         managed = False
'''

Shloka Resources

'''

class Shloka(models.Model):
    mapping = models.JSONField()
    audio = models.FileField(upload_to='audios/')
    media_url = models.URLField()
    link = models.URLField()
    document = models.FileField(upload_to='module/') # check as if w ewant multipple
    quiz_date = models.DateTimeField(default=datetime.datetime.now)
    # questions = models.JSONField()  # for 5 types of question



'''

Practice Resources

'''

class PracticeResources(models.Model):
    title = models.CharField(max_length=20)
    marks = models.IntegerField()
    due_date = models.TimeField()
    due_time = models.TimeField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    identifier = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    published = models.BooleanField(default=False)


    class Meta:
        abstract = True


class Test(PracticeResources):
    description = models.CharField(max_length=60)
    duration = models.TimeField(default=30)

class Assignment(PracticeResources):

    class AssignmentType(Enum):
        AUDIO = "A"
        FILE = "F"
        TEXT = "T"
        
    remarks = models.CharField(max_length=30)
    type = models.CharField(
        max_length=1,
        choices=[(status.value, status.name.capitalize()) for status in AssignmentType],
        default=AssignmentType.AUDIO.value
    )
#   attachments = models.FileField()


class Quiz(PracticeResources):
    remarks = models.CharField(max_length=20)
    # questions = models.JSONField()
 #      {
 #         'type': (mcq, parajumbles, true/false, matrix) , 'question': '' , 'options': {}, 'answer': 
 #       }
 


'''

Teaching Resources

'''

class TeachingResources(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=60)
    tags = models.CharField(max_length = 10)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    identifier = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    published = models.BooleanField(default=False)

    
    class Meta:
        abstract = True



class Module(TeachingResources):
    image = models.ImageField(null=True, blank=True, upload_to="module")

    shloka = models.ManyToManyField(
        Shloka,
        through = 'Module_Shloka',
        related_name = 'modules'
    )



class StudyMaterial(TeachingResources):
    image = models.ImageField(null=True, blank=True, upload_to="studyMaterial/")


class LearningPath_settings(models.Model):
    pathRestrictions = models.JSONField()
    certsBadge = models.JSONField()
    timeLimit = models.JSONField()
    contentSensitivity = models.JSONField()


class LearningPath(TeachingResources):

    class Stage(Enum):
        BEGINNER = "B"
        INTERMEDIATE = "I"
        ADVANCED = "A"
        

    image = models.ImageField(null=True, blank=True, upload_to="learningPath/")
    # duration = models.TimeField(default = datetime.datetime.now)
    duration_in_months = models.IntegerField(null=True, blank=True, default=None)
    above_age = models.IntegerField(default = 6)
    prerequisites = models.CharField(default = "Need a basic understanding of sanskrit")
    settings = models.ForeignKey(LearningPath_settings,on_delete=models.CASCADE)


    module = models.ManyToManyField(
        Module,
        through = 'LearningPath_Module',
        )
    
    studyMaterial = models.ManyToManyField(
        StudyMaterial, 
        through='LearningPath_StudyMaterial',
    )

    assignment = models.ManyToManyField(
        Assignment,
        through = 'LearningPath_Assignment',
    )

    quiz = models.ManyToManyField(
        Quiz,
        through = 'LearningPath_Quiz',
    )

    test = models.ManyToManyField(
        Test,
        through = 'LearningPath_Test',
    )

    

class LearningPath_Module(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='module_learningpaths')
    learningPath = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name= 'learningpath_modules')
    order = models.PositiveIntegerField()  # Extra field to maintain order

    class Meta:
        unique_together = ('module', 'learningPath')  # Ensure uniqueness for each pair
        ordering = ['order']



class LearningPath_StudyMaterial(models.Model):
    learningPath = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='learningpath_studymaterials')
    studyMaterial = models.ForeignKey(StudyMaterial, on_delete=models.CASCADE, related_name='studymaterial_learningpaths')
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ('learningPath', 'studyMaterial')
        ordering = ['order']
        
            
class LearningPath_Quiz(models.Model):
    learningPath = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='learningpath_quizs')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='quiz_learningpaths')
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ('learningPath' , 'quiz')
        ordering = ['order']

class LearningPath_Assignment(models.Model):
    learningPath = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='learningpath_assignments')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='assignment_learningpaths')
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ('learningPath', 'assignment')
        ordering = ['order']

class LearningPath_Test(models.Model):
    learningPath = models.ForeignKey(LearningPath, on_delete = models.CASCADE, related_name='learningpath_tests')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='test_learningpaths')
    order = models.PositiveIntegerField()

    class Meta: 
        unique_together = ('learningPath', 'test')
        ordering = ['order']


class Module_Shloka(models.Model):
    module = models.ForeignKey(Module, on_delete = models.CASCADE, related_name='module_shlokas')
    shloka = models.ForeignKey(Shloka, on_delete = models.CASCADE, related_name='shloka_modules')
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ('module', 'shloka')
        ordering = ['order']


class RecentActivity(models.Model):

    class Category(Enum):
        JOINED = "J"
        MODULE = "M"
        QUIZ = "Q"
        ASSIGNMENT = "A"
        TEST = "T"
        STARTED = "S"
        PRACTICE = "P"
        LEARNINGPATH = "L"
        DAKSHINA = "D"
        DANAM = "Da"

        
    content = models.CharField()   # the statement to be passsed onto the front end
    gurukul = models.ForeignKey(Classrooms, on_delete=models.CASCADE) # to be used to filter according to the  gurukula
    owner = models.ForeignKey(User, null=True, on_delete=models.CASCADE)   # for student activity display name for teacher activity keep it null
    category = models.CharField(
        max_length=3,
        choices=[(status.value, status.name.capitalize()) for status in Category])    # to be given as either enum or string to be used for grouping 
    date = models.DateField(default=datetime.datetime.now)   # 


class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    content  = models.CharField()
    object = models.CharField()
    timestamp = models.DateTimeField()



class LearningPathProgress(models.Model):

    class Status(Enum):
        INPROGRESS = "I"
        COMPLETED = "C"

    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    learningpath = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    progress = models.JSONField(default=dict)
    status = models.CharField(
        max_length=2,
        choices = [(status.value, status.name.capitalize()) for status in Status])
    dateofcompletion = models.DateTimeField(default=None, null=True)
    danam = models.IntegerField(default=None, null=True)


class SubmissionMeta(models.Model):
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=datetime.datetime.now)
    grade = models.CharField(default= None, null = True)
    learningpath = models.ForeignKey(LearningPath, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class AssignmentSubmission(SubmissionMeta):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    file = models.FileField(upload_to="files/submission")
    # grade = models.CharField(default=None, null=True)


class TestSubmission(SubmissionMeta):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    submission = models.JSONField()


class QuizSubmission(SubmissionMeta):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    submission = models.JSONField()
