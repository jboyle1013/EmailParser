# The purpose of these functions is to control how many emails enter the parser at any given time

def makebatches():
    directory = "//email-analysis-data/new-emails"
    for entry in sorted( os.scandir( directory ),
                         key=lambda e: e.name ):
