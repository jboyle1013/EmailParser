import os
import shutil
from emailparser import *
# The purpose of these functions is to control how many emails enter the parser at any given time
# This code will be used to run the

def makebatchest(tf):
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


def makebatches(tf):
    directory = "/root/email-analysis-data/btest/new-emails"
    folder_names = [f.name for f in os.scandir(directory) if f.is_dir()]
    # sort the folder names in alphabetical order
    folder_names.sort()
    sublists = {
        "a-g" : [],
        "h-p" : [],
        "q-u" : [],
        "v-z" : [],
    }

    for name in folder_names:
        first_letter = name[0].lower()
        if first_letter < 'a' or first_letter > 'z':
            continue
        if first_letter <= 'g':
            sublist_key = 'a-g'
        elif first_letter <= 'p':
            sublist_key = 'h-p'
        elif first_letter <= 'u':
            sublist_key = 'o-u'
        else:
            sublist_key = 'v-z'
        if sublist_key not in sublists:
            sublists[sublist_key] = []
        sublists[sublist_key].append(name)

    for list in sublists.keys():
        print(f"Inboxes {list} being parsed:")
        for names in sublists.get(list):
            dir_name = directory + "/" + names
            fsetup = "/root/email-analysis-data/new-emails" + "/" + names + "/"
            if not os.path.exists( fsetup ):  # Does the Directory already path exist?
                os.mkdir( fsetup)  # Make directory path
            foptions = ["new", "cur", "temp"]
            for opt in foptions:
                fpath = fsetup + opt + "/"
                if not os.path.exists( fpath ): # Does the Directory already path exist?
                    os.mkdir( fpath)  # Make directory path
            distpath = "/root/email-analysis-data/new-emails" + "/" + names + "/new/"
            for file in sorted(os.scandir(dir_name), key=lambda e: e.name):
                file_str = str(file.name)  # Turns the name of the entry to a string
                origpath = dir_name + "/" + file_str
                shutil.move(origpath, distpath)
        emailparser(tf)
        for names in sublists.get(list):
            distpath = "/root/email-analysis-data/new-emails" + "/" + names + "/new/"
            for file in sorted(os.scandir(distpath), key=lambda e: e.name):
                ndistpath = f"/root/email-analysis-data/btest/processed-emails/{names}/"
                if not os.path.exists( ndistpath ):  # Does the Directory already path exist?
                    os.mkdir( ndistpath)  # Make directory path
                file_str = str(file.name)  # Turns the name of the entry to a string
                norigpath = distpath + file_str
                shutil.move(norigpath, ndistpath)

            fsetup = "/root/email-analysis-data/new-emails" + "/" + names + "/"
            foptions = ["new", "cur", "temp"]
            for opt in foptions:
                fpath = fsetup + opt + "/"
                if os.path.exists( fpath ): # Does the Directory already path exist?
                    os.rmdir( fpath)  # remove directory path
            if os.path.exists( fsetup ): # Does the Directory already path exist?
                os.rmdir( fsetup)  # remove directory path