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
    path('gurukul/<int:id>', views.class_details, name='gurukul-details'),
    path('gurukul/<int:id>/feed', views.class_feed, name='class-feed'),
    path('gurukul/<int:id>/learning', views.class_learnings, name='class-learning'),
    path('gurukul/<int:id>/schedule', views.class_schedule, name='class-schedule'),

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
