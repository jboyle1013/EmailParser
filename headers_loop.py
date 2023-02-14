import mailbox
from email.parser import BytesParser
from email.policy import default
from headertodict import header_dict_parser
from multirun_file_manager import *
from Logs.listener import *


def headers_loop(directory, queue, configurer):
    configurer(queue)
    logger = logging.getLogger()
    emails_list = []  # This is the final list of dicts to go into data.json
    num_inboxes = 1  # I'm manually starting the count at 1 for readability
    total_message_num = 0  # total number of messages in database
    total_inbox_num = 0  # total number of inboxes in database
    run_num = file_getruncount()    # This tells us how many times this program has been run
    for i, entry in enumerate(sorted(os.scandir(directory), key=lambda e: e.name)):  # This is looping through each file in the directory above
        file_str = str(entry.name)  # Turns the name of the entry to a string
        filepath = directory + "/"  # Adds slash  to end of directory name
        file_name = filepath + file_str + "/" # Adds the folder to the filename so it can be read in the right location

        print( file_str )  # Used to keep track of progress
        name = file_str

        mb = mailbox.maildir(file_name, factory=BytesParser(policy=default).parse)  # Reading in mbox file
        mblen = len(mb)  # number of messages
        '''This sections checks for and handles multiple runs.'''
        if mblen == 0 and run_num == 0:
            message_num = 0
        elif run_num > 0:
            message_num = file_getcount(name)
        else:
            message_num = 1  # I'm manually starting the count at 1 for readability
        msg_list = []  # Holds list of messages in inbox
        jdict = {}  # Holds individual email headers
        inboxdict = {}  # Holds inbox
        if mblen == 0:
            logger.error(f"Inbox {name} is Empty. Header Parsing Cannot Run.")
        elif mblen >= 50000:
            logger.error( f"Inbox {name} is too large. Header Parsing Cannot Run." )
        else:
            logger.info( f"Header Process is working in Directory {name}")
            final_num = 0
            for _, message in enumerate(mb):  # Loops through messages in inbox


                print(_ + message_num)  # Used to keep track of progress

                msg_list.append({"Number": _+message_num, "Headers": {}, "Content": {}})  # Creating empty dict

                jdict = header_dict_parser(jdict, message)  # Running Header Parser

                total_message_num = total_message_num + 1
                # keeping track of number of messages
                msg_list[_]["Headers"] = jdict  # adding message headers to list of messages in inbox

                jdict = {}  # clearing dict for next message
                final_num = _

        """ This section is making sure the dictionary is formatted properly """
        inboxdict["Name"] = name
        inboxdict["Inbox Number"] = num_inboxes  # Adding the inbox numver to inbox dict
        inboxdict["Number Of Messages"] = message_num - 1
        inboxdict["Message List"] = msg_list  # adding inbox messages to inboxdict
        emails_list.append(inboxdict)  # adding inbox to emails list
        num_inboxes = num_inboxes + 1  # keeping track of number of inboxes
        total_inbox_num = total_inbox_num + 1 # keeping track of total number of inboxes for totals dict


    # This is the current count of totals
    total = {
        "Total Number of Emails": total_message_num,
        "Total Number of Inboxes": total_inbox_num
    }



    emails_list.append(total)  # Adds totals to final data list
    datafile = open("In-Process-JSONS/data.json", "w", encoding="utf-8")  # opening json file for writing
    json.dump(emails_list, datafile, indent=4)  # printing data in nice format to file
    datafile.close()  # closing file
    logger.info( "Header Parsing Complete" )

