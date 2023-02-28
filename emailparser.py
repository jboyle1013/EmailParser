
from Logs.listener import *
from headers_loop import headers_loop
from links_loop import links_loop
from merger import merger
from message_content_loop import message_content_loop
from message_attachment_loop import message_attachment_loop
'''Even though this import is not being used right now, but do not delete it.
There are some necessary functions that are in this file that we want to make sure we 
have access to.'''
from multirun_file_manager import *


'''This is the main function of the parser. This parser will now support multiple runs. To turn that on remove
the file_reset function.'''

cd
def emailparser(tf):
    queue = multiprocessing.Queue(-1) # The queue and the listener are for allowing the parser to use one log file.
    listener = multiprocessing.Process(target=listener_process, args=(queue, listener_configurer))
    listener.start()
    # creating thread
    directory = "/root/email-analysis-data/new-emails"
    if tf:
        file_idgen(directory)
        file_reset(directory)
    p1 = multiprocessing.Process(target=headers_loop, args=(directory, queue, worker_configurer,)) # Header Parsing Process
    p2 = multiprocessing.Process(target=message_content_loop, args=(directory, queue, worker_configurer,))    # Content Parsing Process
    p3 = multiprocessing.Process(target=links_loop, args=(directory, queue, worker_configurer,))  # Links Parsing Process
    p4 = multiprocessing.Process( target=message_attachment_loop, args=(directory, queue, worker_configurer,) )  # Content Parsing Process

    p1.start()  # Begin Header Parsing
    p2.start()  # Begin Content Parsing
    p3.start()  # Begin Link Parsing
    p4.start()  # Begin Attachment Parsing

    p4.join()
    print( "Attachment Parsing Completed" )
    # wait until process 1 is finished
    p1.join()
    print("Header Parsing Completed")
    # wait until process 2 is finished
    p2.join()
    # wait until process 3 is finished
    print("Message Parsing Completed")
    p3.join()
    print("Link Parsing Completed")
    # wait until process 4 is finished

    # all processes finished
    print("All processes completed.")
    print("Merging begins.")
    merger(queue, worker_configurer)
    print("Files Merged. Parsing Completed.")
    listener.terminate()


if __name__ == "__main__":
    emailparser()
