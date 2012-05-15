# Create your views here.

from AutograderWeb.code_grader.filegrader import FileGrader, process_quiz
from AutograderWeb.code_grader.forms import CreateQuizForm, UploadFileForm, \
    ViewQuizForm
from AutograderWeb.code_grader.grader_manager import GraderWatch
from AutograderWeb.code_grader.models import Quiz, Submission
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
import string


def index(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            fg = GraderWatch.addSubmission(request.FILES['file'], form.cleaned_data['name'], form.cleaned_data['quiz'])
            
            #fg = FileGrader(request.FILES['file'], form.cleaned_data['name'], form.cleaned_data['quiz'])
            #fg.start()
            #while fg.randomness == None:
            #    None
            return render_to_response('code_grader/success.html', {'title': Quiz.objects.get(id=form.cleaned_data['quiz']).title, 'id': fg})
    else:
        form = UploadFileForm()
    return render_to_response('code_grader/upload.html', {'form': form})

def new_quiz(request):
    if request.method == 'POST':
        form = CreateQuizForm(request.POST, request.FILES)
        if form.is_valid():
            process_quiz(request.FILES['testcases'], request.FILES['answers'], form.cleaned_data['title'], form.cleaned_data['password'])
            return HttpResponseRedirect('/upload/')
    else:
        form = CreateQuizForm()
    return render_to_response('code_grader/add_quiz.html', {'form': form})

def view_results(request):
    if request.method == 'POST':
        form = ViewQuizForm(request.POST)
        
        if form.is_valid():
            quiz = Quiz.objects.get(id=form.cleaned_data['quiz'])

            if quiz.password == form.cleaned_data['password']:
                submissions = Submission.objects.filter(quiz=quiz).iterator()
                return render_to_response('code_grader/view_quiz.html', {'submissions': submissions, 'quiz': quiz.title})
    else:
        form = ViewQuizForm()
    return render_to_response('code_grader/view_password.html', {'form': form})

def display(request):
    if request.method == 'GET':
        try:
            id = request.GET['submission']
            if id != None:
                sub = Submission.objects.get(randomness=id)
                lines = open(sub.file).readlines()
                secondLines = ()
                for line in lines:
                    secondLines += (line.replace("\t", u'\xa0\xa0\xa0\xa0\xa0'),)
                if(sub != None):
                    return render_to_response('code_grader/display_file.html', {'file': secondLines, 'name': sub.student})
        except:
            None
    else:
        return render_to_response('code_grader/error_file.html')

def status(request):
    if request.method == 'POST':
        try:
            id = request.POST['submission']
            if id != None:
                sub = Submission.objects.get(randomness=id)
                return render_to_response('code_grader/status_file.html', {'text': sub.status})
        except:
            print "Error"
    return render_to_response("code_grader/status_file.html", {'text': 'Bad ID: ' + id})