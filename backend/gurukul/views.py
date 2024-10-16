from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import ClassroomsSerializer
import logging
from .models import Teachers, Students, Classmodule, Classrooms, Assignments, Feed, Material
from .serializers import TeachersSerializer, StudentsSerializer, ClassroomsSerializer
from itertools import chain

logger = logging.getLogger('gurukul')


@api_view(['GET'])
def home(request):
    # logger.info("Reached the home view",request)
    print("home")
    ## for teacher
    #print(request.user.id)
    teachers = Teachers.objects.filter(teacher_id_id = 2)
    # print(list(teachers.values('classroom_id_id')))
    classes = Classrooms.objects.filter(pk__in = teachers)
    # logger.info(classes.values())
    classes = list(classes.values())
    # print("reached here",classes)
    return Response(classes) 


@api_view(['GET'])
def schedule(request):
    print("schedule")
    return Response({'message': 'Show schedule'}) 
 


@api_view(['GET'])
def class_details(request):
    # logic for sending class details + students enrolled count
    serializer = ClassroomsSerializer
    return Response()


@api_view(['GET'])
def class_feed(request,id):
    classroom = Classrooms.objects.filter(pk=id)
    try: 
        assignments = Assignments.objects.filter(classroom_id = id)
    except Exception as e:
        assignments = None

    try:
        students = Students.objects.filter(classroom_id = id)
    except Exception as e:
        students = None

    try:
        material = Material.objects.filter(classroom_id = id)
    except Exception as e:
        material = None    

    try:
        feed = Feed.objects.filter(owner_class=id).order_by('-timestamp')
    except Exception as e:
        feed = None

    feed2 = Feed.objects.all()
    unique_dates = set(item.timestamp.date() for item in feed2)

    teachers = Teachers.objects.filter(classroom_id = id)
    class_data = teachers.values()
    teacher_mapping = Teachers.objects.filter(teacher_id=id).select_related('classroom_id')
    student_mapping = Students.objects.filter(student_id=id).select_related('classroom_id')
    # mappings = chain(teacher_mapping,student_mapping)
    mappings = {'classroom': list(classroom.values()), 'feed': list(feed.values())}
    print(mappings)
    
    # result = {'classroom':classroom,'assignments':assignments,'students':students,'teachers':teachers,"material":material,"mappings":mappings,'feed':feed, "unique_dates": unique_dates,'classdata':class_data,'invitedata':classroom}
    return Response(mappings)


    return 


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
    return

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