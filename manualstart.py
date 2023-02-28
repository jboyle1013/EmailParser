from emailparser import emailparser
from bouncer import makebatches
import sys, getopt


# This is the function for manually starting the parser.
# This one takes a boolean argument. If it is true, run the program to reset the
# File counter. If it is false do not reset the counter.
# If you want to reset the counter for only one run, be sure to save the
# inbox_vals.json somewhere outside of the In-Process-Jsons folder
def manualstart(argv):
    tf = sys.argv[1]
    makebatches(tf)



if __name__ == "__main__":
    startbycron(sys.argv[1:])