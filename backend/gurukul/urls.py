from django.test import TestCase
from django.urls import path, re_path as url, include
from django.conf.urls.static import static
from . import views
from django.conf import settings
from django.views.static import serve


urlpatterns = [

    url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),

    path('', views.home, name='home'),
    path('schedule/', views.schedule, name='schedule'),
    path('notification/', views.UserNotificationView.as_view(), name='notification'),

    path('gurukul/', views.GurukulView.as_view(), name='gurukul'),
    path('gurukul/join/', views.JoinGurukul.as_view(), name='join-gurukul'),
    path('gurukul/<int:id>/', views.GurukulDetailView.as_view(), name='gurukul-details'),
    path('gurukul/<int:id>/leave/', views.LeaveGurukulView.as_view(), name='leave-gurukul'),
#   path('gurukul/<int:id>', views.class_details, name='gurukul-details'),
    path('gurukul/<int:id>/feed/', views.FeedView.as_view(), name='class-feed'),
    path('gurukul/<int:id>/learning/', views.class_learnings, name='class-learning'),
    path('gurukul/<int:id>/schedule/', views.class_schedule, name='class-schedule'),

    path('gurukul/<int:id>/question/', views.QuestionView.as_view(), name='class-question'),
    path('gurukul/<int:id>/question/<int:question_id>', views.QuestionView.as_view(), name='question-object'),
   
    path('gurukul/<int:id>/announcement/', views.AnnouncementView.as_view(), name= 'class-announcements'),
    path('gurukul/<int:id>/announcement/<int:announcement_id>/', views.AnnouncementsDetailView.as_view(), name='class-announcement-object'),
    
    path('gurukul/<int:id>/activity/', views.RecentActivityView.as_view(), name='gurukul-activity'),

    path('learningPath/', views.LearningPathView.as_view(), name='learning-path'),
    path('learningPath/publish/', views.PublishLearningPath.as_view(), name='publish-learningpath'),
    path('learningPath/<int:id>/', views.LearningPathDetailView.as_view(), name='learningPath_detail'),
    path('learningPath/<int:learningpath_id>/progress/', views.LearningPathProgressView.as_view(), name='learningpath-progress'),
    path('learingpPath/<int:learningpath_id>/complete/',views.LearningPathCompleteView.as_view(), name='learninpath-complete'),
    
    path('assignment/', views.AssignmentView.as_view(), name='assignment'),
    path('assignment/<int:assignment_id>/', views.AssignmentDetailView.as_view(), name='assignment_details'),
    path('learningPath/<int:learningpath_id>/assignment/<int:assignment_id>/submission/', views.AssignmentSubmissionView.as_view(), name='assignment-submission'),
    path('assignment/<int:assignment_id>/submission/<int:submission_id>/', views.AssignmentSubmissionDetailView.as_view(), name='submission-detail'),

#  gurukul.gyaandweep.com/gurukul/"guruk_uuid"/quiz/"quiz_uuid"
#  gurukul.gyaandweep.com/gurukul/""guruku_uuid/leaningpath/"ksabdks"/

    #js all the inside components
    #    gurukul.gyaandweep.com/learningpath/akjwdn/module/

#  gurukul.gyaandweep.com/gurukul/"guruk_uuid"/module/"module_uuid"/shloka/"shlokaa_uuid"



    path('quiz/', views.QuizView.as_view(), name='quiz'),
    path('quiz/<int:quiz_id>/', views.QuizDetailView.as_view(), name='quiz_detail'),
    path('leariningPath/<int:learningpath_id>/quiz/<int:quiz_id>/submission/', views.QuizSubmissionView.as_view(), name='quiz-overview'),
    path('quiz/<int:quiz_id>/overview', views.QuizOverviewView.as_view(), name='quiz-overview'),
    
    path('test/', views.TestView.as_view(), name='test'),
    path('test/<int:test_id>/', views.TestDetailView.as_view(), name='test_details'),
    path('leariningPath/<int:learningpath_id>/test/<int:test_id>/submission/', views.QuizSubmissionView.as_view(), name='quiz-overview'),
    path('test/<int:test_id>/overview/', views.TestOverviewView.as_view(), name='test-overview'),
    
    path('studyMaterial/', views.StudyMaterialView.as_view(), name='studymaterial'),
    path('studyMaterial/<int:studymaterial_id>/', views.StudyMaterialDetailView.as_view(), name='studymaterial_details'),

    path('module/', views.ModuleView.as_view(), name='modules'),
    path('module/<int:id>/', views.ModuleDetailView.as_view(), name = 'modules_details'),

    path('template/', views.template, name='guru-templates'),
    path('template/learningpaths', views.learningpathslist, name='guru-learningpaths'),
    path('template/modules', views.templatemoduleslist, name='guru-modules'),

    path('learning-paths', views.learningpaths, name='learning-paths'),
    path('modules', views.modules, name='modules'),
    path('sadhana', views.sadhana, name='sadhana'),
    path('digital-assets', views.digitalassets, name='digital-assets'),





] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# Create your tests here.



        #   <Route path="/gurukul/:name" element={<GurukulDetails />}>
        #     <Route index element={<Navigate to="feed" replace />} /> {/* Default redirect to /feed */}
        #     <Route path="feed" element={<GurukulFeed />} />
        #     <Route path="learning" element={<GurukulLearning />} />
        #     <Route path="students" element={<GurukulStudents />} />
        #   </Route>

        #   {/* Template */}
        #   <Route path="/template" element={<TemplatesPage />} >
        #     {/* <Route path="type" element={<Collections />} /> */}
        #     {/* <Route path=":module" element={<TemplatesPage />} /> */}
        #   </Route>

        #   <Route path="/template/:type" element={<Collections />} />

        #   {/* Teaching Resources */}
        #   <Route path="/learning-paths" element={<LearningPathPage />} />
        #   <Route path="/learning-path/:id" element={<LearningPathDetailsPage />} />
        #   <Route path="/modules" element={<ModulesPage />} />
        #   <Route path="/modules/:id" element={<ModuleDetailsPage />} />
        #   <Route path="/sadhana" element={<SadhanaPage />} />
        #   <Route path="/digital-assets" element={<DigitalAssetsPage />} />

        #   {/* Schedule Page */}
        #   <Route path="/schedule" element={<SchedulePage />} />

        #   {/* not found */}
        #   <Route path="*" element={<h1>Not Found</h1>} />
