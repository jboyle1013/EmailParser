import os
import shutil
from emailparser import *
# The purpose of these functions is to control how many emails enter the parser at any given time
# This code will be used to run the

def makebatches(tf):
    directory = "//email-analysis-data/new-emails"
    folder_names = [f.name for f in os.scandir(directory) if f.is_dir()]
    # sort the folder names in alphabetical order
    folder_names.sort()
    for name in folder_names:
        dir_name = directory + "/" + name
        distpath = "/root/email-analysis-data/new-emails" + "/" + name + "/new/"
        for file in sorted(os.scandir(directory), key=lambda e: e.name):
            file_str = str(file.name)  # Turns the name of the entry to a string
            origpath = dir_name + "/" + file_str
            shutil.move(origpath, distpath)
        emailparser(tf)
        for file in sorted(os.scandir(distpath), key=lambda e: e.name):
            ndistpath = f"//email-analysis-data/ processed-emails/{name}/"
            if not os.path.exists( ndistpath ):  # Does the Directory already path exist?
                os.mkdir( ndistpath)  # Make directory path
            file_str = str(file.name)  # Turns the name of the entry to a string
            norigpath = distpath + file_str
            shutil.move(norigpath, ndistpath)


