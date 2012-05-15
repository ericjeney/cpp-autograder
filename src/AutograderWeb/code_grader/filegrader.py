from AutograderWeb.code_grader.models import Submission, Quiz
from AutograderWeb.settings import BASE_DIR, OS
from datetime import datetime
from subprocess import Popen
import filecmp
import os
import random
import string
import threading
import time

# Checks to see if there's a blank line at the end of the file.
def check_for_blank_line(path):
    try:
        out = open(path, "r")
        lines = out.readlines()
        out.close()
        newOut = open(path[0:-3]+"txt", "w")
        lines[-1] = lines[-1].rstrip("\n")
        lines[-1] = lines[-1].rstrip("\r")
        for line in lines:
            newOut.write(line)
        newOut.close()
        return True
    except:
        return False

# Strips any newlines and puts them back in to make everything a bit more
# consistent between Windows / Unix
def strip(path):
    out = open(path, "r")
    lines = out.readlines()
    out.close()
    newOut = open(path[0:-3]+"txt", "w")
    for line in lines:
        line = line.rstrip("\n")
        line = line.rstrip("\r")
        newOut.write(line + "\n")
    newOut.close()

def create_directory(path):
    try:
        os.mkdir(BASE_DIR + path)
    except:
        None

def save_file(path, file):
    destination = open(path, 'wb+')
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()
    check_for_blank_line(path)

# Adds a new quiz entry to the system
def process_quiz(testcases, answers, title, password):
    create_directory("tcs/")
    create_directory("sub/")
    create_directory("ans/")
    
    while True:
        testcases_path = BASE_DIR + "tcs/" + randomString(10) + ".txt"
        if not os.path.exists(testcases_path):
            break
    
    while True:
        answers_path = BASE_DIR + "ans/" + randomString(10) + ".txt"
        if not os.path.exists(answers_path):
            break
    
    save_file(testcases_path, testcases)
    save_file(answers_path, answers)
    
    strip(testcases_path);
    strip(answers_path);

    Quiz(title=title, answer=answers_path, testcases=testcases_path, password=password).save()

def randomString(length):
    return "".join(random.sample(string.letters+string.digits, length))

# The class that actually grades all of the files
class FileGrader(threading.Thread):
    randomness = None
    
    def __init__(self, f, s, q):
        threading.Thread.__init__(self)
        self.file = f
        self.student = s
        self.quiz = q
    
    def run(self):
        primary = BASE_DIR + "sub/"
        self.randomness = randomString(15)
        path = primary + self.randomness + ".cpp"
        while(os.path.exists(path)):     
            self.randomness = randomString(15)
            path = primary + self.randomness + ".cpp"

        # Grab the quiz data and set the user's status to 'Submitted'
        q = Quiz.objects.get(id=self.quiz)
        submission = Submission(student=self.student, time=datetime.now(), status="Submitted", randomness=self.randomness, file=path, quiz=q, didPass = False, didFail = False)
        submission.save()
        
        # Write the file to disk
        destination = open(path, 'wb+')
        for chunk in self.file.chunks():
            destination.write(chunk)
        destination.close()
        
        if OS == "UNIX":
            p = Popen(["g++", "-o" + path[0:-3]+"exe", path])
        else:
            p = Popen(["compile.bat", "C:\\Program Files (x86)\\Microsoft Visual Studio 9.0\\VC\\bin", path, path[0:-3] + "exe"])
        self.watch_process(p, 1, 20)
        
        # Checks to see if it actually compiled successfully
        if os.path.exists(path[0:-3] + "exe"):
            submission.status = "Compiled"
            submission.save()
            
            p = Popen([path[0:-3] + "exe", q.testcases, path[0:-3]+"txt"])
            
            submission.status = "Running"
            submission.save()

            ti = datetime.now().microsecond
            print datetime.now().microsecond
            bo = self.watch_process(p, 0.01, 2000)
            print datetime.now().microsecond
            ti = datetime.now().microsecond - ti
            ti = ti / 10
            
            # Record how long it took to execute the program
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
            # It must not have compiled
            p = Popen([])
            
            submission.status = "Failed to Compile"
            submission.didPass = False
        
        submission.save()

# Watches a given process to ensure that it doesn't take too long to complete
def watch_process(p, wait, runs):
    index = 0
    while index < runs:
        if p.poll() != None:
            break
        else:
            time.sleep(wait)
            index += 1
    else:
        p.kill()
        return False
        
    return True
