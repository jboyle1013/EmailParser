from emailparser import emailparser
from bouncer import makebatches
import sys, getopt

# This is the function that the cron job will use to start the parser. It has no arguments.
def startbycron(tf):

    makebatches(tf)



if __name__ == "__main__":
    startbycron(False)
