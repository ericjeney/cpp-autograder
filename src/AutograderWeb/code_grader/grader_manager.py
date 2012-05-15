from AutograderWeb.code_grader.filegrader import randomString, \
    check_for_blank_line, strip, watch_process
from AutograderWeb.code_grader.models import Quiz, Submission
from AutograderWeb.settings import BASE_DIR, OS
from datetime import datetime
from subprocess import Popen, STDOUT
import Queue
import filecmp
import os
import threading

def gradeCpp(submission):
    path = submission.file
    q = submission.quiz
    
    compileOutput = open(path[0:-3]+"comp", "wb+")
    
    if OS == "UNIX":
        p = Popen(["g++", "-o" + path[0:-3]+"exe", path], stderr=compileOutput)
    else:
        p = Popen(["compile.bat", "C:\\Program Files (x86)\\Microsoft Visual Studio 9.0\\VC\\bin", path, path[0:-3] + "exe"], stdout=compileOutput)
    
    watch_process(p, 1, 20)
        
    if os.path.exists(path[0:-3] + "exe"):
        submission.status = "Compiled"
        submission.save()
        
        p = Popen([path[0:-3] + "exe", q.testcases, path[0:-3]+"txt"])
            
        submission.status = "Running"
        submission.save()

        ti = datetime.now().microsecond
        bo = watch_process(p, 0.01, 2000)
        ti = datetime.now().microsecond - ti
        ti = ti / 10
        submission.runtime = ti
        
        
        if not bo:
            submission.status = "Hangs"
            submission.didPass = False
            submission.save()
            return
            
        if(os.path.exists(path[0:-3]+"txt")):
            submission.status = "Executed"
            submission.save()
            
            empty = not check_for_blank_line(path[0:-3]+"txt")
            if not empty:
                strip(path[0:-3]+"txt")
                print "Here's the Info"
                print path[0:-3]+"txt"
                print q.answer
                if filecmp.cmp(path[0:-3]+"txt", q.answer, False):
                    submission.status = "PASS"
                    submission.didPass = True
                else:
                    submission.status = "FAIL"
                    submission.didFail = True
                    submission.didPass = False
            else:
                submission.status = "Empty Output File"
                submission.didPass = False
        else:
            submission.status = "No Output File"
            submission.didPass = False
    else:
        submission.status = "Failed to Compile"
        submission.didPass = False 
        return False       
    
    return True
    submission.save()

def determineClassName(path):
    file = open(path)
    for line in file.readlines():
        pos = line.find("public class ")
        if pos >= 0:
            name = line[pos + 13:].strip()
            pos = line.find(" ")
            
            if pos >= 0:
                name = name[0:pos]
                
            pos = line.find("{")
            
            if pos >= 0:
                name = name[0:pos]
                
            print "Name ::: " +  name
            return name
    return None

def gradeJava(submission):
    path = submission.file
    quiz = submission.quiz
    
    name = determineClassName(path)
    
    if name == None:
        submission.status = "No Class"
        submission.didPass = False
        return
    
    

class GraderWatch(threading.Thread):
    queue = Queue.Queue(maxsize = 0)
    
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        submission = GraderWatch.queue.get(block=True, timeout= None)
        
        compiled = gradeCpp(submission)
        
        if not compiled:
            gradeJava(submission)
    
    @classmethod        
    def addSubmission(cls, f, s, q):
        primary = BASE_DIR + "sub/"
        name = f.name
        print "Important: " + name[-4:0]
        if name[-4:0] == "java":
            type = "java"
        else:
            type = "cpp"
        
        randomness = randomString(15)
        path = primary + randomness + ".cpp"
        while os.path.exists(path):     
            randomness = randomString(15)
            path = primary + randomness + ".cpp"

        q = Quiz.objects.get(id=q)
        submission = Submission(student=s, time=datetime.now(), status="Submitted", randomness=randomness, 
                                file=path, quiz=q, didPass = False, didFail = False, type=type, name=name, graded=False)
        submission.save()
        
        destination = open(path, 'wb+')
        for chunk in f.chunks():
            destination.write(chunk)
        destination.close()
        
        GraderWatch.queue.put(submission)
        return randomness
        
        