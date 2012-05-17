C++ Autograder
=============

This is a simple Django application that automatically grades file I/O based C++ Quizzes in the introductory programming class at my high school.

The quizzes essentially require taking a set of inputs (in a file), performing some computations, and then writing a set of outputs to another file.

This application allows an instructor to create new quizzes with a given input file and expected output file.  Students may then submit their .cpp files to the application, which compiles them, executes them, and then compares their output with the expected file.  The result of this comparison is then added to an administrative interface for the instructor.
