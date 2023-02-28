from emailparser import emailparser
from bouncer import makebatches

def startbycron(tf):
    makebatches(tf)



if __name__ == "__main__":
    startbycron()
