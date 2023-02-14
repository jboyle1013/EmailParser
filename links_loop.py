import mailbox
from email.parser import BytesParser
from email.policy import default
from bs4 import BeautifulSoup
from Logs.listener import *
from multirun_file_manager import *


def links_loop(directory, queue, configurer):

    configurer(queue)
    logger = logging.getLogger()
    msg_dict = {}  # Holds list of messages in inbox

    total_message_num = 0  # total number of messages in database
    run_num = file_getruncount()  # This tells us how many times this program has been run
    for entry in sorted( os.scandir( directory ),
                        key=lambda e: e.name ):  # This is looping through each file in the directory above

        file_str = str(entry.name)  # Turns the name of the entry to a string
        filepath = directory + "/"  # Adds slash  to end of directory name
        file_name = filepath + file_str + "/" # Adds the folder to the filename so it can be read in the right location

        print( file_str )  # Used to keep track of progress
        print( p )  # Used to keep track of progress
        name = file_str

        mb = mailbox.maildir( file_name, factory=BytesParser( policy=default ).parse )  # Reading in mbox file
        mblen = len( mb )  # number of messages

        '''This sections checks for and handles multiple runs.'''

        if mblen == 0 and run_num == 0:
            message_num = 0
        elif run_num > 0:
            message_num = file_getcount( name )
        else:
            message_num = 1  # I'm manually starting the count at 1 for readability
        msg_dict[name] = {}
        ms_dict = {}
        if mblen == 0:
            logger.error(f"Inbox {name} is Empty. Links Parsing Cannot Run.")
        elif mblen >= 50000:
            logger.error( f"Inbox {name} is too large. Links Parsing Cannot Run." )
        else:
            logger.info(f"Links Process is working in Directory {name}")
            for _, message in enumerate( mb ):  # Loops through messages in inbox

                linkdict = {"Website": [],
                            "Image": []}

                q = "\t\t\t\t" + str( _ + message_num )
                print( q )  # Used to keep track of progress

                successful, linkdict = content_puller( _, message, name, linkdict )  # Runs the Content Puller method
                ms_dict[f"Message Number {_ + message_num}:"] = {"Links": linkdict}

                if not successful:  # If message exists and is pulled:
                    ms_dict[f"Message Number {_ + message_num}:"] = {"Links": ""}  # Adding Blank value to dictionary
                    logger.error(f"No content returned from Message Number {_ + message_num} in Inbox {name}")
                msg_dict[name] = ms_dict

                total_message_num = total_message_num + 1
                # keeping track of number of messages

                msg_dict[name][f"Message Number {_+message_num}:"] = {"Links": linkdict}


        datafile = open( "In-Process-JSONS/MessageLinks.json", "w", encoding="utf-8" )  # opening json file for writing
        json.dump( msg_dict, datafile, indent=4 )  # printing data in nice format to file
        datafile.close()  # closing file

    logger.info( ("Link Parsing Complete") )


def links_from_html(body):
    """
    :param body: It inputs the raw Message.
    :return: It returns the plaintext with no HTML.
    """
    linkdict = {"Website": [],
                "Image": [],
                "Video": [],
                "Duplicates": {"Website Count": 0,
                               "Image Count": 0,
                               "Video Count": 0,
                               "Website": [],
                               "Image": [],
                               "Video": [],
                               }
                }

    soup = BeautifulSoup( body, 'html.parser' )

    for link in soup.find_all( 'a' ):
        l = link.get( 'href' )
        try:
            c = link.contents[0]
        except IndexError:
            c = ""
        if l != "#":
            if l not in linkdict["Website"]:
                if 'video' not in c:
                    linkdict["Website"].append(l)
                elif 'video' in c:
                    linkdict["Video"].append(l)

            else:
                linkdict["Duplicates"]["Website"].append( l )
                linkdict["Duplicates"]["Website Count"] = linkdict["Duplicates"].get("Website Count") + 1

    for link in soup.find_all( 'img' ):
        if link not in linkdict["Image"]:
            linkdict["Image"].append( link.get( 'src' ) )
        else:
            linkdict["Duplicates"]["Image"].append( l )
            linkdict["Duplicates"]["Image Count"] = linkdict["Duplicates"].get( "Image Count" ) + 1
    for link in soup.find_all( 'video' ):

        linkdict["Video"].append( link.get( 'src' ) )

    return linkdict


def content_puller(_, message, name, mdict):
    """
    :param _: Count/Message Number
    :param message: Message object to be parsed
    :param name: Name of Inbox Owner
    :param mdict: Dictionary of values
    :return: it returns the updated Dictionary of Values
    """

    successful = False
    # Print Statement for keeping track of progress
    body = ""  # Part of precautionary measure for empty inboxes

    if message.is_multipart():  # Starting parse process for multipart Message
        for part in message.walk():  # Built in method for going through multipart methods
            ctype = part.get_content_type()  # Gets content type of Message
            cdispo = str( part.get( 'Content-Disposition' ) )  # Checks for attatchment

            # skip any text/plain (txt) attachments
            if ctype == 'text/html' and 'attachment' not in cdispo:
                body = part.get_payload( decode=True )  # Decodes email body into format
                successful = True  # Did it work?
                break
    # not multipart - i.e. plain text, no attachments, keeping fingers crossed
    else:
        body = message.get_payload( decode=True )  # Decodes email body into format
        successful = True  # Did it work?

    if body == '':
        successful = False
    linkdict = links_from_html( body )  # Cleans Up Body

    return successful, linkdict  # Returns final Values


def text_from_html(body):
    """
    :param body: It inputs the raw Message.
    :return: It returns the plaintext with no HTML.
    """

    soup = BeautifulSoup( body, 'html.parser' )
    # kill all script and style elements
    for script in soup( ['style', 'script', 'head', 'title', 'meta', '[document]', 'a', 'img'] ):
        script = script.extract()  # rip it out
        t = script

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split( "  " ))
    # drop blank lines
    text = '\n'.join( chunk for chunk in chunks if chunk )
    return text