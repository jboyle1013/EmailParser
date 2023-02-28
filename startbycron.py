from emailparser import emailparser
from bouncer import makebatches

def startbycron():
    makebatches(False)



if __name__ == "__main__":
    startbycron()
