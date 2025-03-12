from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import ClassroomsSerializer
from rest_framework.generics import GenericAPIView, mixins
from rest_framework import status
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
import logging
from .models import Teachers, Students,Classrooms, Feed, QnA, Announcements, LearningPath, Module, Assignment, Test, Quiz, StudyMaterial, AssignmentSubmission, RecentActivity, UserNotification, LearningPathProgress, Gurukul_LearningPath, TestSubmission, QuizSubmission
# Material, Classmodule, Assignments,
from .serializers import TeachersSerializer, StudentsSerializer, ClassroomsSerializer, ClassroomsDetailSerializer, FeedSerializer, QnASerializer, AnnouncementSerializer, LearningPathSerializer, LearningPathDetailSerializer, AssignmentsSerializer, TestSerializer, QuizSerlializer, ModuleSerializer, StudyMaterialSerializer, ModuleDetailSerializer, AssignmentSubmissionSerializer, GurukulActivitySerializer, NotificationSerializer, AssignmentSubmissionDetailSerializer, LearningPathProgressSerializer, TestSubmissionSerializer, TestSubmissionDetailSerializer, QuizSubmissionSerializer, QuizSubmissionOverviewSerializer, QuizSubmissionDetailSerializer
from itertools import chain
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.contrib.contenttypes.models import ContentType
from .permissions import IsGurukulStudent, IsGurukulTeacher, HasAccessToGurukul, method_permission, IsOwner
import datetime
from datetime import timedelta
from django.utils import timezone
import json
from .utility.NotificationUtility import NotificationUtility
from .signals.CreateNotification import notificationSignal

logger = logging.getLogger('gurukul')


@api_view(['GET'])
def home(request):
    # logger.info("Reached the home view",request)
    print("home")
    ## for teacher
    #print(request.user.id)
    teachers = Teachers.objects.get(pk=2)
    print(teachers.values())
    # print(list(teachers.values('classroom_id_id')))
    classes = teachers.classroom.filter(teachers)
    # logger.info(classes.values())
    classes = list(classes.values())
    # print("reached here",classes)
    print(classes)
    return Response(classes) 



class GurukulView(GenericAPIView, 
              mixins.ListModelMixin, 
              mixins.CreateModelMixin):
    
    permission_classes = [IsAuthenticated]
    queryset = None
    serializer_class = ClassroomsSerializer

    def get_queryset(self):
        context = self.request.headers.get('context')  
        user = self.request.user
        if context == "student":
            student = Students.objects.get(user = user)
            queryset = student.classroom.all()
        else:
            teacher = Teachers.objects.get(user = user)
            queryset =  teacher.classroom.all()
        return queryset

    
    def get(self, request, *args, **kwargs):
        # queryset = self.get_queryset()
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
        # Use atomic transaction (Either executes completely or rolls back to initial state)
            with transaction.atomic():

                # response = self.create(request, *args, **kwargs)
                serializer = self.get_serializer(data = request.data)
                serializer.is_valid(raise_exception=True)
                class_instance = serializer.save()   

                
                teacher, created = Teachers.objects.get_or_create(user=self.request.user)
                teacher.classroom.add(class_instance)

        
                return Response(serializer.data,status=status.HTTP_201_CREATED )

        except Exception as e:
            # Handle the exception if needed
            return Response(
                {"detail": "An error occurred: {}".format(str(e))},
                status=status.HTTP_400_BAD_REQUEST
            )




# For retrieving, updating, and deleting
class GurukulDetailView(GenericAPIView,
                            mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin, 
                            mixins.DestroyModelMixin):
    
    permission_classes = [IsAuthenticated,HasAccessToGurukul]
    #create another permission class for checking access to the class
    queryset = Classrooms.objects.all()
    serializer_class = ClassroomsSerializer
    lookup_field = 'id' 

    def get_object(self):
        return super().get_object()

    def get(self, request, *args, **kwargs):
        # to fetch all the details about the gurukul i.e feed, 
        # can be made into entirely another View.
        # print("returning gurukul's base page")
        return super().retrieve(request, *args, **kwargs)

    @method_permission(IsGurukulTeacher)
    def put(self, request, *args, **kwargs):
        # to make some changes in the gurukul fields
        return self.update(request, *args, **kwargs)

    @method_permission(IsGurukulTeacher)
    def delete(self, request, *args, **kwargs):
        # Notify all students
        return self.destroy(request, *args, **kwargs)
    


class JoinGurukul(GenericAPIView):

    permission_classes = [IsAuthenticated]

    def post(self, *args, **kwargs):
        print("entered post call")
        class_code = self.request.data.get('class_code')
        gurukul = Classrooms.objects.get(class_code = class_code)
        teacher = Teachers.objects.get(user=self.request.user)
        if teacher.classroom.filter(id=gurukul.id).exists():
            return Response("Cannot join as a student into your own gurukul", status=status.HTTP_400_BAD_REQUEST)
        student, created = Students.objects.get_or_create(user = self.request.user)
        if not student.classroom.filter(id=gurukul.id).exists():
            student.classroom.add(gurukul)

    ####### Create a signal to create an object in the recentactivity db

            return Response(f"Added to classroom {gurukul.classroom_name}", status=status.HTTP_201_CREATED)
        else:
            return Response("Already added to this class" , status=status.HTTP_302_FOUND)
    

class LeaveGurukulView(GenericAPIView):

    permission_classes = [IsAuthenticated, HasAccessToGurukul]

    def post(self, *args, **kwargs):
        class_id = kwargs.get('id')
        confirmation = self.request.data.get('confirmation', False)
        user = self.request.user
        teacher = Teachers.objects.get(user = user)
        student = Students.objects.get(user = user)
        gurukul = Classrooms.objects.get(id = class_id)
        
        if not confirmation:

            if teacher.classroom.filter(id = gurukul.id).exists():
                return Response(
                    {"message": "If you leave your gurukul it would be inaccessible for everyone", "reconfiration_required": True },
                    status=status.HTTP_200_OK)
            elif student.classroom.filter(id = gurukul.id).exists():
                return Response(
                    {"message": "Are you sure you want to leave gurukul, all your progress will be lost", "confirmation_required": True},
                    status=status.HTTP_200_OK
                )
        else:        
            if teacher.classroom.filter(id = gurukul.id).exists():
                teacher.classroom.remove(gurukul)
            
            elif student.classroom.filter(id = gurukul.id).exists():
                student.classroom.remove(gurukul)
            
            return Response(
                {"message": "You left the gurukul"},
                status=status.HTTP_200_OK
            )



class FeedView(GenericAPIView, 
               mixins.ListModelMixin,
               mixins.CreateModelMixin,
               mixins.DestroyModelMixin):
    
    permission_classes = [IsAuthenticated, HasAccessToGurukul]
    queryset = Feed.objects.all()
    serializer_class = FeedSerializer

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(owner_class = self.kwargs.get('id'))
    
    def get(self, *args, **kwargs):
        query_set = self.get_queryset()
        return self.list(self.request, *args, **kwargs)

    

class QuestionView(GenericAPIView, 
               mixins.ListModelMixin,
               mixins.CreateModelMixin,
               mixins.RetrieveModelMixin,
               mixins.UpdateModelMixin,
               mixins.DestroyModelMixin):
    
    permission_classes = [IsAuthenticated, HasAccessToGurukul]
    queryset = QnA.objects.all()
    serializer_class = QnASerializer

    def get_object(self):
        return super().get_object()


    @method_permission(IsGurukulTeacher)
    def post(self, *args, **kwargs):  
        try:
        # Use atomic transaction (Either executes completely or rolls back to initial state)
            with transaction.atomic():
                id = kwargs.get('id')
                classroom = Classrooms.objects.get(pk = id)
                context = {'request': self.request, 'classroom_obj' : classroom}
                # response = self.create(request, *args, **kwargs)
                serializer = self.get_serializer(data = self.request.data, context= context)
                serializer.is_valid(raise_exception=True)
                class_instance = serializer.save()   


                content_type = ContentType.objects.get_for_model(QnA)
                feed_instance = Feed.objects.create(
                    timestamp = datetime.datetime.now(),
                    category = "Question",
                    owner_class = classroom,
                    content_type = content_type,
                    object_id = class_instance.id
                )
                notificationSignal.send(sender=None, data={'user': self.request.user, 'view': "Question"})
                return Response(serializer.data,status=status.HTTP_201_CREATED )

        except Exception as e:
            # Handle the exception if needed
            return Response(
                {"detail": "An error occurred: {}".format(str(e))},
                status=status.HTTP_400_BAD_REQUEST
            )

    
    @method_permission(IsGurukulTeacher)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @method_permission(IsGurukulTeacher)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    


class AnnouncementView(GenericAPIView, 
               mixins.ListModelMixin,
               mixins.CreateModelMixin,
               mixins.RetrieveModelMixin,
               mixins.DestroyModelMixin):
    
    permission_classes = [IsAuthenticated, HasAccessToGurukul]
    queryset = Announcements.objects.all()
    serializer_class = AnnouncementSerializer

    def get_object(self):
        return super().get_object()
    
    def post(self, *args, **kwargs):  
        try:
        # Use atomic transaction (Either executes completely or rolls back to initial state)
            with transaction.atomic():
                id = kwargs.get('id')
                classroom = Classrooms.objects.get(pk = id)
                context = {'request': self.request, 'classroom_obj' : classroom}
                # response = self.create(request, *args, **kwargs)
                serializer = self.get_serializer(data = self.request.data, context= context)
                serializer.is_valid(raise_exception=True)
                class_instance = serializer.save()   


                content_type = ContentType.objects.get_for_model(Announcements)
                feed_instance = Feed.objects.create(
                    timestamp = datetime.datetime.now(),
                    category = "Announcements",
                    owner_class = classroom,
                    content_type = content_type,
                    object_id = class_instance.id
                )
                notificationSignal.send(sender=None, data={'user': self.request.user, 'view': "Announcement"})
                return Response(serializer.data,status=status.HTTP_201_CREATED )

        except Exception as e:
            # Handle the exception if needed
            return Response(
                {"detail": "An error occurred: {}".format(str(e))},
                status=status.HTTP_400_BAD_REQUEST
            )



class AnnouncementsDetailView(GenericAPIView, 
                                mixins.RetrieveModelMixin,
                                mixins.UpdateModelMixin,
                                mixins.DestroyModelMixin):
    
    permission_classes = [IsAuthenticated, HasAccessToGurukul]
    queryset = Announcements.objects.all()
    serializer_class = AnnouncementSerializer
    lookup_field = 'id'

    # def get_object(self):
    #     return super().get_object()
    
    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    # @method_permission()   create a new method for object owner
    @method_permission(IsOwner)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    # @method_permission()   create a new method for object owner
    @method_permission(IsOwner)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    


# class GurkulActivityView(GenericAPIView, 
#                      mixins.ListModelMixin,
#                      ):
    
#     permission_classes = [IsAuthenticated, HasAccessToGurukul]
    
#     def list(self, request, *args, **kwargs):
#         return super().list(request, *args, **kwargs)
    


class LearningPathView(GenericAPIView,
                   mixins.ListModelMixin,
                   mixins.CreateModelMixin
                   ):
    
    permission_classes = [IsAuthenticated]
    serializer_class = LearningPathSerializer
    queryset = LearningPath.objects.all()


    def get_queryset(self, *args, **kwargs):
        # gurukul = Classrooms.objects.get(pk = self.kwargs.get('id'))
        return self.queryset.filter(creator = self.request.user)
        # return self.queryset.filter( = self.kwargs.get('id'))
        

    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        try:
        # Use atomic transaction (Either executes completely or rolls back to initial state)
            with transaction.atomic():
                context = {'request': self.request}
                # expecting data as a list of Dicts 

                serializer = self.get_serializer(data = request.data, context = context)
                serializer.is_valid(raise_exception=True)
                class_instance = serializer.save()   
        
                return Response(serializer.data,status=status.HTTP_201_CREATED )
        except Exception as e:
            # Handle the exception if needed
            return Response(
                {"detail": "An error occurred: {}".format(str(e))},
                status=status.HTTP_400_BAD_REQUEST
            )


    

class LearningPathDetailView(GenericAPIView,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin
                   ):
    
    permission_classes = [ IsAuthenticated ]
    queryset = LearningPath.objects.all()
    serializer_class = LearningPathDetailSerializer
    lookup_field = 'id'


    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @method_permission(IsOwner)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    

    @method_permission(IsOwner)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class PublishLearningPath(GenericAPIView):

    permission_classes = [IsAuthenticated]

    def post(self, *args, **kwargs):
        try:
            print("entered  call")
            
            gurukul = self.request.data.get('gurukul')
            gurukul_obj = Classrooms.objects.get(id = gurukul)
            learningpath = self.request.data.get('learningpath')
            learningpath_obj =  LearningPath.objects.get(id = learningpath)
            # if learningpath_obj.creator != self.request.user:
            #     return Response({"detail": "You are not the owner of this learningPath"},
            #                     status=status.HTTP_400_BAD_REQUEST)

            if Gurukul_LearningPath.objects.filter(gurukul = gurukul, learningpath = learningpath_obj).exists():
                return Response({"detail": "This learningpath is already published in this gurukul"},
                                status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                Gurukul_LearningPath.objects.create(
                    gurukul = gurukul_obj,
                    learningpath = learningpath_obj
                )
                notificationSignal.send(sender=None,data={'user': self.request.user, 'view': "LearningPath", 'object': learningpath_obj.name })
                return Response({"detail": "Learning Path is successfully added to the {}".format(gurukul_obj.classroom_name)},
                                status=status.HTTP_201_CREATED
                                )
        except Exception as e:
            return Response(
                {"detail": "An error occurred: {}".format(str(e))},
                status=status.HTTP_400_BAD_REQUEST
            )


class ModuleView(GenericAPIView,
             mixins.ListModelMixin,
             mixins.CreateModelMixin):
    
    permission_classes = [IsAuthenticated]
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(creator = self.request.user)
        # return self.queryset.filter( = self.kwargs.get('id'))

    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    

    # The context sent from the backend should be off a teacher to be able to create an entry
    def post(self, request, *args, **kwargs):
        try:
        # Use atomic transaction (Either executes completely or rolls back to initial state)
            with transaction.atomic():

                data = request.data.copy()
 
                try:
                    serializer = self.get_serializer(data = data)
                except Exception as e:
                    print(e)
                # print(serializer.initial_data['shloka'], type(serializer.initial_data['shloka']))
                try:
                    serializer.is_valid(raise_exception=True)
                except Exception as e:
                    print("Validation Error:", serializer.errors)
                class_instance = serializer.save()   
                print(class_instance)
                return Response(serializer.data,status=status.HTTP_201_CREATED )

        except Exception as e:
            # Handle the exception if needed
            return Response(
                {"detail": "An error occurred: {}".format(str(e))},
                status=status.HTTP_400_BAD_REQUEST
            )



class ModuleDetailView(GenericAPIView,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin):
    
    permission_classes = [IsAuthenticated]
    queryset = Module.objects.all()
    serializer_class = ModuleDetailSerializer
    lookup_field = 'id'
    

    # def get_object(self):
    #     return super().get_object()
    
    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @method_permission(IsOwner)
    def update(self, request, *args, **kwargs):
        module = self.get_object
        if module.published == True:
            response = {"Details": "This module is already published and part of learning Path"}
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        else:
            return super().update(request, *args, **kwargs)
    
    @method_permission(IsOwner)
    def destroy(self, request, *args, **kwargs):
        module = self.get_object
        if module.published == True:
            response = {"Details": "This module is already published and part of learning Path"}
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        else:
            return super().destroy(request, *args, **kwargs)



class StudyMaterialView(GenericAPIView,
             mixins.ListModelMixin,
             mixins.CreateModelMixin):
    
    permission_classes = [IsAuthenticated]
    queryset = StudyMaterial.objects.all()
    serializer_class = StudyMaterialSerializer

    def get_queryset(self, *args, **kwargs):
        # teacher = Teachers.objects.get(user = self.request.user)
        return self.queryset.filter(creator = self.request.user)
        # return self.queryset.filter( = self.kwargs.get('id'))
    
    
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    
    # The context sent from the backend should be off a teacher to be able to create an entry
    def post(self, request, *args, **kwargs):
        try:
        # Use atomic transaction (Either executes completely or rolls back to initial state)
            with transaction.atomic():

                # response = self.create(request, *args, **kwargs)
                serializer = self.get_serializer(data = request.data)
                serializer.is_valid(raise_exception=True)
                class_instance = serializer.save()   

                # teacher, created = Teachers.objects.get_or_create(user=self.request.user)
                # teacher.classroom.add(class_instance)
        
                return Response(serializer.data,status=status.HTTP_201_CREATED )

        except Exception as e:
            # Handle the exception if needed
            return Response(
                {"detail": "An error occurred: {}".format(str(e))},
                status=status.HTTP_400_BAD_REQUEST
            )


class StudyMaterialDetailView(GenericAPIView,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin):
    
    permission_classes = [IsAuthenticated, HasAccessToGurukul]
    queryset = StudyMaterial.objects.all()

    def get_object(self):
        return super().get_object()


    
class TestView(GenericAPIView,
             mixins.ListModelMixin,
             mixins.CreateModelMixin):
    
    permission_classes = [IsAuthenticated]
    queryset = Test.objects.all()
    serializer_class = TestSerializer

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(creator = self.request.user)
        # return self.queryset.filter( = self.kwargs.get('id'))
    
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    

    # The context sent from the backend should be off a teacher to be able to create an entry
    def post(self, request, *args, **kwargs):
        try:
        # Use atomic transaction (Either executes completely or rolls back to initial state)
            with transaction.atomic():

                # response = self.create(request, *args, **kwargs)
                serializer = self.get_serializer(data = request.data)
                serializer.is_valid(raise_exception=True)
                class_instance = serializer.save()   

                # teacher, created = Teachers.objects.get_or_create(user=self.request.user)
                # teacher.classroom.add(class_instance)
        
                return Response(serializer.data,status=status.HTTP_201_CREATED )

        except Exception as e:
            # Handle the exception if needed
            return Response(
                {"detail": "An error occurred: {}".format(str(e))},
                status=status.HTTP_400_BAD_REQUEST
            )



class TestDetailView(GenericAPIView,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin):
    
    permission_classes = [IsAuthenticated, HasAccessToGurukul]
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    lookup_field = 'id'
    
    def get_object(self):
        return super().get_object()

    def get(self, request, *args, **kwargs):
        return self.get_object()

    @method_permission(IsOwner)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @method_permission(IsOwner)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)



class TestSubmissionView(GenericAPIView,
                         mixins.ListModelMixin,
                         mixins.CreateModelMixin):
    
    permission_classes = [IsAuthenticated]
    queryset = TestSubmission.objects.all()
    serializer_class = TestSubmissionSerializer
    

    def get_queryset(self):
        assignment = self.kwargs.get('assignment_id') 
        return self.queryset.filter(assignment = assignment)
    
    # can add get_serializer_context in the view for this 
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        context['test'] = Assignment.objects.get(id = self.kwargs.get('test_id'))
        context['learningpath'] = LearningPath.objects.get(id = self.kwargs.get('learningpath_id'))
        return context
    

    def get(self, request, *args, **kwargs):
        self.queryset = self.get_queryset()
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
        # Use atomic transaction (Either executes completely or rolls back to initial state)
            with transaction.atomic():
                #context = {'request': self.request, 'assignment_id': kwargs.get('assignment_id'), 'learningpath_id': kwargs.get('learningpath_id')}
                # expecting data as a list of Dicts 

                serializer = self.get_serializer(data = request.data)
                serializer.is_valid(raise_exception=True)
                class_instance = serializer.save()   
        
                return Response(serializer.data,status=status.HTTP_201_CREATED )

        except Exception as e:
            # Handle the exception if needed
            return Response(
                {"detail": "An error occurred: {}".format(str(e))},
                status=status.HTTP_400_BAD_REQUEST
            )
        

class TestSubmissionDetailView(GenericAPIView,
                        mixins.UpdateModelMixin):

    permission_classes = [IsAuthenticated]
    serializer_class = TestSubmissionDetailSerializer
    lookup_field = 'submission_id'

    def get_object(self):
        """
        Override this method to fetch the object based on `submission_id` and validate `assignment_id`.
        """
        submission_id = self.kwargs.get('submission_id')

        # Ensure that the submission belongs to the correct assignment
        return get_object_or_404(
            AssignmentSubmission, 
            id=submission_id, 
        )


    def get_serializer_context(self):
        """
        Setting the context for the serializer to avoid sending through update view
        """
        return {'user': self.request.user, 'context': self.request.headers.get('context')}
    

    def put(self, request, *args, **kwargs):
        try:
        # Determine the serializer to use based on user type
            with transaction.atomic():
                instance = self.get_object()
                serializer = self.get_serializer(instance, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                assignment = Assignment.objects.get(id = self.kwargs.get('assignment_id'))
                if self.request.headers.get('context') == 'teacher':
                    notificationSignal.send(sender=None, data={'user': self.request.user, 'view': "Graded", 'object': assignment.title })
                return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle the exception if needed
            return Response(
                {"detail": "An error occurred: {}".format(str(e))},
                status=status.HTTP_400_BAD_REQUEST
            )



class TestOverviewView(GenericAPIView,
                       mixins.ListModelMixin,
                       mixins.RetrieveModelMixin):
    
    permission_classes = [IsAuthenticated]
    queryset = TestSubmission.objects.all()
    serializer_class = QuizSubmissionSerializer

    def get_serializer_context(self):
        return {'user': self.request.user, 'context': self.request.headers.get('context')}
        
    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class AssignmentView(GenericAPIView,
             mixins.ListModelMixin,
             mixins.CreateModelMixin):
    
    permission_classes = [IsAuthenticated]
    queryset = Assignment.objects.all()
    serializer_class = AssignmentsSerializer

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(creator = self.request.user)
        # return self.queryset.filter( = self.kwargs.get('id'))
    
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    

    # The context sent from the backend should be off a teacher to be able to create an entry
    def post(self, request, *args, **kwargs):
        try:
        # Use atomic transaction (Either executes completely or rolls back to initial state)
            with transaction.atomic():

                # response = self.create(request, *args, **kwargs)
                serializer = self.get_serializer(data = request.data)
                serializer.is_valid(raise_exception=True)
                class_instance = serializer.save()   

                # teacher, created = Teachers.objects.get_or_create(user=self.request.user)
                # teacher.classroom.add(class_instance)
        
                return Response(serializer.data,status=status.HTTP_201_CREATED )

        except Exception as e:
            # Handle the exception if needed
            return Response(
                {"detail": "An error occurred: {}".format(str(e))},
                status=status.HTTP_400_BAD_REQUEST
            )



class AssignmentDetailView(GenericAPIView,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin):
    
    permission_classes = [IsAuthenticated, HasAccessToGurukul]
    queryset = Assignment.objects.all()
    
    def get_object(self):
        return super().get_object()
    
    @method_permission(IsOwner)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @method_permission(IsOwner)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class AssignmentSubmissionView(GenericAPIView,
                           mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.DestroyModelMixin):
    
    
    permission_classes = [IsAuthenticated]
    serializer_class = AssignmentSubmissionSerializer
    queryset = AssignmentSubmission.objects.all()
    
    def get_queryset(self):
        assignment = self.kwargs.get('assignment_id') 
        return self.queryset.filter(assignment = assignment)
    
    # can add get_serializer_context in the view for this 
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        context['assignment'] = Assignment.objects.get(id = self.kwargs.get('assignment_id'))
        context['learningpath'] = LearningPath.objects.get(id = self.kwargs.get('learningpath_id'))
        return context
    

    def get(self, request, *args, **kwargs):
        self.queryset = self.get_queryset()
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
        # Use atomic transaction (Either executes completely or rolls back to initial state)
            with transaction.atomic():
                #context = {'request': self.request, 'assignment_id': kwargs.get('assignment_id'), 'learningpath_id': kwargs.get('learningpath_id')}
                # expecting data as a list of Dicts 

                serializer = self.get_serializer(data = request.data)
                serializer.is_valid(raise_exception=True)
                class_instance = serializer.save()   
        
                return Response(serializer.data,status=status.HTTP_201_CREATED )

        except Exception as e:
            # Handle the exception if needed
            return Response(
                {"detail": "An error occurred: {}".format(str(e))},
                status=status.HTTP_400_BAD_REQUEST
            )

        
class AssignmentSubmissionDetailView(GenericAPIView,
                        mixins.UpdateModelMixin):

    permission_classes = [IsAuthenticated]
    serializer_class = AssignmentSubmissionDetailSerializer
    lookup_field = 'submission_id'

    def get_object(self):
        """
        Override this method to fetch the object based on `submission_id` and validate `assignment_id`.
        """
        submission_id = self.kwargs.get('submission_id')

        # Ensure that the submission belongs to the correct assignment
        return get_object_or_404(
            AssignmentSubmission, 
            id=submission_id, 
        )


    def get_serializer_context(self):
        """
        Setting the context for the serializer to avoid sending through update view
        """
        return {'user': self.request.user, 'context': self.request.headers.get('context')}
    

    def put(self, request, *args, **kwargs):
        try:
        # Determine the serializer to use based on user type
            with transaction.atomic():
                instance = self.get_object()
                serializer = self.get_serializer(instance, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                assignment = Assignment.objects.get(id = self.kwargs.get('assignment_id'))
                if self.request.headers.get('context') == 'teacher':
                    notificationSignal.send(sender=None, data={'user': self.request.user, 'view': "Graded", 'object': assignment.title })
                return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle the exception if needed
            return Response(
                {"detail": "An error occurred: {}".format(str(e))},
                status=status.HTTP_400_BAD_REQUEST
            )


class QuizView(GenericAPIView,
             mixins.ListModelMixin,
             mixins.CreateModelMixin):
    
    permission_classes = [ IsAuthenticated ]
    queryset = Quiz.objects.all()
    serializer_class = QuizSerlializer

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(creator = self.request.user)
        # return self.queryset.filter( = self.kwargs.get('id'))

    
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    

    def post(self, request, *args, **kwargs):
        try:
        # Use atomic transaction (Either executes completely or rolls back to initial state)
            with transaction.atomic():

                # response = self.create(request, *args, **kwargs)
                serializer = self.get_serializer(data = request.data)
                serializer.is_valid(raise_exception=True)
                class_instance = serializer.save()   

                # teacher, created = Teachers.objects.get_or_create(user=self.request.user)
                # teacher.classroom.add(class_instance)
        
                return Response(serializer.data,status=status.HTTP_201_CREATED )

        except Exception as e:
            # Handle the exception if needed
            return Response(
                {"detail": "An error occurred: {}".format(str(e))},
                status=status.HTTP_400_BAD_REQUEST
            )



class QuizDetailView(GenericAPIView,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin):
    
    permission_classes = [IsAuthenticated, HasAccessToGurukul]
    queryset = Quiz.objects.all()
    serializer_class = QuizSubmissionSerializer

    def get_object(self):
        return super().get_object()
    
    @method_permission(IsOwner)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @method_permission(IsOwner)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)



class QuizSubmissionView(GenericAPIView,
                         mixins.CreateModelMixin):
    
    permission_classes = [IsAuthenticated]
    queryset = QuizSubmission.objects.all()
    serializer_class = QuizSubmissionSerializer


    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        context['context'] = self.request.headers.get('context')
        context['learningpath'] = LearningPath.objects.get(id = self.kwargs.get('learningpath_id'))
        context['quiz'] = Quiz.objects.get(id = self.kwargs.get('quiz_id'))
        return context
       
    
    def post(self, request, *args, **kwargs):
        try:
        # Use atomic transaction (Either executes completely or rolls back to initial state)
            with transaction.atomic():

                # response = self.create(request, *args, **kwargs)
                serializer = self.get_serializer(data = request.data)
                serializer.is_valid(raise_exception=True)
                class_instance = serializer.save()   

                # teacher, created = Teachers.objects.get_or_create(user=self.request.user)
                # teacher.classroom.add(class_instance)
        
                return Response(serializer.data,status=status.HTTP_201_CREATED )

        except Exception as e:
            # Handle the exception if needed
            return Response(
                {"detail": "An error occurred: {}".format(str(e))},
                status=status.HTTP_400_BAD_REQUEST
            )
        
class QuizSubmissionDetailView(GenericAPIView,
                               mixins.RetrieveModelMixin,
                               mixins.UpdateModelMixin):
    
    permission_classes = [IsAuthenticated]
    queryset = QuizSubmission.objects.all()
    serializer_class = QuizSubmissionDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['context'] = self.request.headers.get('context')

    def get_object(self):

        return get_object_or_404(
            QuizSubmission,
            id = self.kwargs.get('submission_id')
        )
    
    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class QuizOverviewView(GenericAPIView,
                       mixins.ListModelMixin,
                       mixins.RetrieveModelMixin):
    
    permission_classes = [IsAuthenticated]
    queryset = QuizSubmission.objects.all()
    serializer_class = QuizSubmissionOverviewSerializer

    def filter_queryset(self, queryset):
        return queryset.filter(quiz = self.kwargs.get('quiz_id'))

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] =  self.request.user 
        context['context'] = self.request.headers.get('context')
        return context
        
    
    def list(self, request, *args, **kwargs):
        # first need to get all the learningpaths where the test is posted.
        # need to get all the gurukuls based on those learningpaths.
        # need to get all the students submission based on that learningpaths.
        return super().list(request, *args, **kwargs)
    

    
    

class RecentActivityView(GenericAPIView,
                     mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin):
    
    permission_classes = [IsAuthenticated, HasAccessToGurukul]
    queryset = RecentActivity.objects.all()
    serializer_class = GurukulActivitySerializer


    def get_queryset(self,request, *args, **kwargs):
        return self.queryset.filter(gurukul = kwargs.get('id'))

    def get(self,request, *args, **kwargs):
        self.queryset = self.get_queryset(request, *args, **kwargs)
        return super().list(request, *args, **kwargs)

        
    def post(self, request, *args, **kwargs):
        try:
        # Use atomic transaction (Either executes completely or rolls back to initial state)
            with transaction.atomic():
                context = {'request': self.request, 'gurukul': kwargs.get('id')}
                # expecting data as a list of Dicts 

                serializer = self.get_serializer(data = request.data, context = context)
                serializer.is_valid(raise_exception=True)
                class_instance = serializer.save()   
        
                return Response(serializer.data,status=status.HTTP_201_CREATED )

        except Exception as e:
            # Handle the exception if needed
            return Response(
                {"detail": "An error occurred: {}".format(str(e))},
                status=status.HTTP_400_BAD_REQUEST
            )
        
 
class UserNotificationView(GenericAPIView, 
                           mixins.CreateModelMixin,
                           mixins.ListModelMixin):
    
    queryset = UserNotification.objects.all()
    permission_classes = [ IsAuthenticated ]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(user = self.request.user)
        now = datetime.datetime.now()
        five_days_ago = now - timedelta(days=5)
        return queryset.filter(timestamp__range=[five_days_ago, now]).order_by('-timestamp')

    
    # technically no external post calls in this
    # all internal calls for creating an entry in the user notification db.

    # Notifications will be static in the notification bar for a timeperiod

    # Important Notification (Missed Danam , Assignment) -> for this only need to send the date
    # Upcoming within 3 days (learningPath may expire)     
    # Teacher graded your assignment.      (create signal)  (complete)
    # Completion of a learningPath.       (Check with utsav as other functionalities are/can be sent as notification via email/phone)  
    # New learningPath has been added.     (create signal)   (complete)
    # Teacher posted an announcement or question     (create signal)    (complete)

    def utility(self, request):
        validated_data = {}
        validated_data['Danam'] = NotificationUtility.checkDanam(request)
        validated_data['Expiring'] = NotificationUtility.checkExpiry(request)
        return validated_data

                
    def get(self, request, *args, **kwargs):

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        additional_data = self.utility(request)
        return Response({
            'data': serializer.data,  # Serialized list of objects
            'additional_data': additional_data  # Separate additional data
        },status= status.HTTP_200_OK)
    

#
#   This view needs to have two views 
#    one for teacher which will show the data for students progress accordingly for gurkul->learningpath in json format
#   for student 
##
class LearningPathProgressView(GenericAPIView,
                           mixins.ListModelMixin,
                           mixins.CreateModelMixin,
                           mixins.UpdateModelMixin
                            ):
    
    permission_classes = [IsAuthenticated]
    queryset = LearningPathProgress.objects.all()
    serializer_class = LearningPathProgressSerializer

    def get_object(self):
        learningpath_id = self.kwargs.get('learningpath_id')
        learningpath = LearningPath.objects.get(id = learningpath_id)
        student = Students.objects.get(user = self.request.user)

        return get_object_or_404(
            LearningPathProgress,
            student = student,
            learningpath = learningpath
        )
    

    def get_queryset(self):
        learningpath = self.kwargs.get('learningpath_id')
        context = self.request.headers.get('context')
        student = Students.objects.get(user = self.request.user)
        if context == 'teacher':
            return LearningPathProgress.objects.filter(learningpath = learningpath)
        else:
            return LearningPathProgress.objects.filter(learningpath = learningpath,
                                                       student = student
                                                       )
        
    

    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


    """
    for a teacher the overview tab should display all the gurukuls which have this 
    learningpath in it and correspondingly all the students in it and their corresponding progress

    request that a teacher can do is just querying the db for the student's progress.

    

    for a student the overview should only display his own progress in that particular learningpath

    requests that a student can make -> starting(post), progress on it(put), finishing it(put)

    """


    def post(self, request, *args, **kwargs):
        try:
        # Use atomic transaction (Either executes completely or rolls back to initial state)
            with transaction.atomic():
                context = {'request': self.request, 'learningpath': kwargs.get('learningpath_id')}
                # expecting data as a list of Dicts 

                serializer = self.get_serializer(data = request.data, context = context)
                serializer.is_valid(raise_exception=True)
                class_instance = serializer.save()   
        
                return Response(serializer.data,status=status.HTTP_201_CREATED )

        except Exception as e:
            # Handle the exception if needed
            return Response(
                {"detail": "An error occurred: {}".format(str(e))},
                status=status.HTTP_400_BAD_REQUEST
            )


    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    
class LearningPathCompleteView(GenericAPIView,
                               mixins.UpdateModelMixin):
    
    permission_classes = [IsAuthenticated]

    def get_object(self):
        learningpath = LearningPath.objects.get(id = self.kwargs.get('learningpath_id'))
        student = Students.objects.get(user = self.request.user)
        return get_object_or_404(
            LearningPathProgress,
            student = student,
            learningpath = learningpath
        )
    
    def put(self, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                learningpath = LearningPath.objects.get(id = self.kwargs.get('learningpath_id'))
                instance.status = LearningPathProgress.Status.COMPLETED.value
                instance.dateofcompletion = datetime.datetime.now()
                instance.save()
                notificationSignal.send(sender=None, data={'user': self.request.user, 'view': "Completed", 'object': learningpath.name })
            
        except Exception as e:
            return Response({"detail": "Getting an error while performing this action".format(str(e))},
                            status=status.HTTP_400_BAD_REQUEST)
        

        

# class LearningPathProgressDetailView(GenericAPIView,
#                                      mixins.UpdateModelMixin,
#                                      ):
    
#     permission_classes = [IsAuthenticated]
#     serializer_class = LearningPathProgressSerializer
#     queryset = LearningPathProgress.objects.all()
#     lookup_field = 'learningpath_id'

#     def get_object(self):

#         learningpath_id = self.kwargs.get('submission_id')
#         learningpath = LearningPath.objects.get(id = learningpath_id)
#         student = Students.objects.get(user = self.request.user)

#         return get_object_or_404(
#             LearningPathProgress,
#             student = student,
#             learningpath = learningpath
#         )


#     def update(self, request, *args, **kwargs):
#         return super().update(request, *args, **kwargs)

    # def post(self, request, *args, **kwargs):
    #     try:
    #     # Use atomic transaction (Either executes completely or rolls back to initial state)
    #         with transaction.atomic():
    #             context = {'request': self.request}
    #             # expecting data as a list of Dicts 

    #             serializer = self.get_serializer(data = request.data, context = context)
    #             serializer.is_valid(raise_exception=True)
    #             class_instance = serializer.save()   
        
    #             return Response(serializer.data,status=status.HTTP_201_CREATED )

    #     except Exception as e:
    #         # Handle the exception if needed
    #         return Response(
    #             {"detail": "An error occurred: {}".format(str(e))},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )




@api_view(['GET'])
def schedule(request):  
    print("schedule")
    return Response({'message': 'Show schedule'}) 
 


@api_view(['GET'])
def class_details(request):
    # logic for sending class details + students enrolled count
    serializer = ClassroomsSerializer
    return Response()


# @api_view(['GET'])
# def class_feed(request,id):
#     classroom = Classrooms.objects.filter(pk=id)
#     try: 
#         assignments = Assignments.objects.filter(classroom_id = id)
#     except Exception as e:
#         assignments = None

#     try:
#         students = Students.objects.filter(classroom_id = id)
#     except Exception as e:
#         students = None

#     try:
#         material = Material.objects.filter(classroom_id = id)
#     except Exception as e:
#         material = None    

#     try:
#         feed = Feed.objects.filter(owner_class=id).order_by('-timestamp')
#     except Exception as e:
#         feed = None

#     feed2 = Feed.objects.all()
#     unique_dates = set(item.timestamp.date() for item in feed2)

#     teachers = Teachers.objects.filter(classroom_id = id)
#     class_data = teachers.values()
#     teacher_mapping = Teachers.objects.filter(teacher_id=id).select_related('classroom_id')
#     student_mapping = Students.objects.filter(student_id=id).select_related('classroom_id')
#     # mappings = chain(teacher_mapping,student_mapping)
#     mappings = {'classroom': list(classroom.values()), 'feed': list(feed.values())}
#     print(mappings)
    
#     # result = {'classroom':classroom,'assignments':assignments,'students':students,'teachers':teachers,"material":material,"mappings":mappings,'feed':feed, "unique_dates": unique_dates,'classdata':class_data,'invitedata':classroom}
#     return Response(mappings)


#     return 


@api_view(['GET'])
def class_learnings(rquest):
    return 


@api_view(['GET'])
def class_schedule(request):
    return


@api_view(['GET'])
def template(request):
    return


@api_view(['GET'])
def learningpathslist(request):
    return Response()

@api_view(['GET'])
def templatemoduleslist(request):
    return

@api_view(['GET'])
def learningpaths(request):
    return 

@api_view(['GET'])
def modules(request):
    return

@api_view(['GET'])
def sadhana(request):
    return


@api_view(['GET'])
def digitalassets(request):
    return