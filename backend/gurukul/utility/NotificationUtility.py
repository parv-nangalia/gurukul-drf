from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta
from ..models import LearningPathProgress, Students, LearningPath, Gurukul_LearningPath

class NotificationUtility:

    @staticmethod
    def checkDanam(request):
        '''
            Checks on every render call if the 5 days have passed then creates a db entry 
        '''
        pending_danam = []
        student = Students.objects.get(user = request.user )
        progress_list = LearningPathProgress.objects.filter(student = student)
        now = datetime.now()
        five_days_ago = now - timedelta(days=5)
        for progress in progress_list:
            if progress.status == LearningPathProgress.Status.COMPLETED and progress.dateofcompletion < five_days_ago:
                if progress.danam == None:
                    attr = {
                        'content' : "Danam",
                        'object' : progress.learningpath.name,
                        'timestamp' : progress.dateofcompletion,
                    }
                    pending_danam.append(attr)
        return pending_danam


    @staticmethod
    def checkExpiry(request):
        '''
            Checks on every render call if any enrolled learningpath is expiring within 10 days
        '''
        getting_expired = []
        Student = Students.objects.get(user = request.user)
        now = datetime.now().replace(tzinfo=timezone.utc)
        # learning_paths = LearningPath.objects.filter(learningpath_gurukuls__gurkul=gurukul)
        classrooms = Student.classroom.prefetch_related('learningPath').all()
        for classroom in classrooms:
            for learningpath in classroom.learningPath.all():
                through_model = Gurukul_LearningPath.objects.filter(learningpath=learningpath).first()
                UploadedDate = through_model.dateAdded
                expiryDate = UploadedDate + relativedelta(months=learningpath.duration_in_months)
                time_to_expire = relativedelta(expiryDate, now)
                print(time_to_expire)
                if time_to_expire.months <= 1:
                    attr = {
                        'object': learningpath.name,
                        'content': "Expiry",
                        'timestamp': time_to_expire,
                    }
                    getting_expired.append(attr)
        return getting_expired
                
