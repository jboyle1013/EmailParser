import shutil
import os




def filereplacer():
    dir_name = "//email-analysis-data/processed-emails"
    dest_name = "//email-analysis-data/new-emails"
    for folder in sorted(os.scandir(dir_name), key=lambda e: e.name):
        f_str = str(folder.name)  # Turns the name of the folder to a string
        dirpath = dir_name + "/" + f_str
        for file in sorted(os.scandir(dirpath), key=lambda e: e.name):
            file_str = str(file.name)  # Turns the name of the file to a string
            fd_path = dest_name + "/" + f_str + "/"
            fopath = dirpath + "/" + file_str
            try:
                shutil.move(fopath, fd_path)
            except:
                pass


def filereplacerbackup():
    dir_name = "/root/email-analysis-data/backup-storage/new-emails"
    dest_name = "//email-analysis-data/new-emails"
    for folder in sorted(os.scandir(dir_name), key=lambda e: e.name):
        f_str = str(folder.name)  # Turns the name of the folder to a string
        dirpath = dir_name + "/" + f_str
        for file in sorted(os.scandir(dirpath), key=lambda e: e.name):
            file_str = str(file.name)  # Turns the name of the file to a string
            fd_path = dest_name + "/" + f_str + "/"
            fopath = dirpath + "/" + file_str
            try:
                shutil.copy(fopath, fd_path)
            except:
                pass


def repfiles():
    filereplacer()
    filereplacerbackup()

if __name__ == "__main__":
    repfiles()