from django.conf.urls.defaults import *

# Comment out the next two lines to disable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^upload/$', 'code_grader.views.index'),
    (r'^display/$', 'code_grader.views.display'),
    (r'^new/$', 'code_grader.views.new_quiz'),
    (r'^view/$', 'code_grader.views.view_results'),
    (r'^status/$', 'code_grader.views.status'),
    (r'^admin/', include(admin.site.urls)),
)
