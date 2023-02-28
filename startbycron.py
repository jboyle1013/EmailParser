from emailparser import emailparser
from bouncer import makebatches
import sys, getopt

# This is the function that for the cron
def startbycron(tf):

    makebatches(tf)



if __name__ == "__main__":
    startbycron(False)
