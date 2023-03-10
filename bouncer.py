import shutil
from emailparser import *
# The purpose of these functions is to control how many emails enter the parser at any given time

def makebatches(tf):
    cleartempfolder()
    directory = "//email-analysis-data/new-emails"
    folder_names = [f.name for f in os.scandir(directory) if f.is_dir()]
    # sort the folder names in alphabetical order
    folder_names.sort()
    sublists = {
        "a-g" : [],
        "h-n" : [],
        "o-u" : [],
        "v-z" : [],
    }

    for name in folder_names:
        first_letter = name[0].lower()
        if first_letter < 'a' or first_letter > 'z':
            continue
        if first_letter <= 'g':
            sublist_key = 'a-g'
        elif first_letter <= 'n':
            sublist_key = 'h-n'
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
                try:
                    shutil.move(origpath, distpath)
                except:
                    print("Moving Files Not Allowed from //email-analysis-data/new-emails/")
                    shutil.copy(origpath, distpath)

        emailparser(tf)

        for names in sublists.get(list):
            distpath = "/root/email-analysis-data/new-emails" + "/" + names + "/new/"
            for file in sorted(os.scandir(distpath), key=lambda e: e.name):
                ndistpath = f"//email-analysis-data/processed-emails/{names}/"
                if not os.path.exists( ndistpath ):  # Does the Directory already path exist?
                    os.mkdir( ndistpath)  # Make directory path
                file_str = str(file.name)  # Turns the name of the entry to a string
                norigpath = distpath + file_str
                shutil.move(norigpath, ndistpath)

            dir_name = directory + "/" + names
            fsetup = "/root/email-analysis-data/new-emails" + "/" + names + "/"
            foptions = ["new", "cur", "temp"]
            shutil.rmtree(fsetup)
            

            try:
                shutil.rmtree(dir_name)  # remove directory path
            except:
                print("Deleting Files Not allowed from //email-analysis-data/new-emails/")
                continue

def cleartempfolder():
    dir_name = "//email-analysis-data/processed-emails"
    for folder in sorted(os.scandir(dir_name), key=lambda e: e.name):
        f_str = str(folder.name)  # Turns the name of the folder to a string
        dirpath = dir_name + "/" + f_str
        shutil.rmtree(dirpath)
