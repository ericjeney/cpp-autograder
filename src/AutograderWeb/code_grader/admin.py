from AutograderWeb.code_grader.models import Submission, Quiz
from django.contrib import admin

class QuizAdmin(admin.ModelAdmin):
    list_display = ('title',)

admin.site.register(Submission)
admin.site.register(Quiz)