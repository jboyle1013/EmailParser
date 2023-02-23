import json
import mailbox
import os
import re
from email.parser import BytesParser
from email.policy import default
from bs4 import BeautifulSoup
from bs4.element import Comment
from multirun_file_manager import *
from Logs.listener import *


""" For efficiency reasons, we are using multiprocessing to speed up the parsing process. Yes, I am aware that 
`   I am printing to file instead of returning a value. It is the easiest method I have found for returning values 
    while multiprocessing. """


def message_content_loop(directory, queue, configurer):
    configurer( queue )
    logger = logging.getLogger()

    mdict = {}  # Holds all the Message Contents
    ldict = {}

    run_num = file_getruncount()
    for i, entry in enumerate(sorted(os.scandir(directory), key=lambda e: e.name)):  # This is looping through each file in the directory above
        file_str = str(entry.name)  # Turns the name of the entry to a string
        filepath = directory + "/"  # Adds slash  to end of directory name
        file_name = filepath + file_str + "/" # Adds the folder to the filename so it can be read in the right location

        print( file_str )  # Used to keep track of progress

        p = "\t\t" + file_str  # Print value for keeping track of progress
        print( p )  # Print Statement for keeping track of progress

        name = file_str

        mb = mailbox.Maildir( file_name, factory=BytesParser( policy=default ).parse )  # Reading in mbox file
        mblen = len( mb )  # number of messages
        '''This sections checks for and handles multiple runs.'''
        if mblen == 0 and run_num == 0:
            message_num = 0
        elif run_num > 0:
            message_num = file_getcount( name )
        else:
            message_num = 1  # I'm manually starting the count at 1 for readability
        mdict[name] = {}  # Setting up dictionary format
        ms_dict = {}
        extra_links = {}

        if mblen == 0:
            logger.error(f"Inbox {name} is Empty. Content Parsing Cannot Run.")
        elif mblen >= 50000:
            logger.error( f"Inbox {name} is too large. Content Parsing Cannot Run." )
        else:
            logger.info(f"Content Process is working in Directory {name}")

            successful = False  # Part of precautionary measure for empty inboxes
            _ = 0  # Also part of precautionary measure for empty inboxes
            for _, message in enumerate( mb ):  # Loops through messages in inbox
                q = f"\t\t{_+message_num}"  # Print value for keeping track of progress
                print( q )  # Print Statement for keeping track of progress
                successful, text = content_puller( _, message, message_num )  # Runs the Content Puller method
                if successful:
                    unitext = text.encode( "ascii", "ignore" )
                    text = unitext.decode()

                    pattern = re.compile( '(http[s]?://[^\s]+)' )
                    pattern1 = re.compile( '(HTTP[S]?://[^\s]+)' )
                    pattern2 = re.compile( '&([^\s]+)' )
                    pattern3 = re.compile( '(\(http[s]?://[^\s]+)' )

                    links = re.findall( pattern, text)
                    if len(re.findall( pattern1, text )) > 0:
                        links.append(re.findall( pattern1, text ))
                    if len(re.findall( pattern2, text )) > 0:
                        links.append(re.findall( pattern2, text ))
                    if len(re.findall( pattern3, text )) > 0:
                        links.append(re.findall( pattern3, text ))
                    if len(links) > 0:
                        logger.debug(f"Extra Links found in Message Number {_ + message_num} in Inbox {name}")
                    text2 = text

                    text2 = pattern.sub( ' (LINK) ', text2 )
                    text2 = pattern1.sub( ' (LINK) ', text2 )
                    text2 = pattern2.sub( ' (LINK) ', text2 )
                    text2 = pattern3.sub( ' (LINK) ', text2 )

                    text = pattern.sub( '', text )
                    text = pattern1.sub( '', text )
                    text = pattern2.sub( '', text )
                    text = pattern3.sub( '', text )

                    text = text.replace( "( )", "" )
                    num = _ + message_num
                    ms_dict[f"Message Number {_ + message_num}:"] = {"Content": text, "Content Marked": text2}

                    extra_links[f"Message Number {_ + message_num}:"] = {"Links": links}
            if not successful:  # If message exists and is pulled:

                logger.error(f"Content Parsing Unsuccessful for Message Number {_ + message_num} in Inbox {name}")
                ms_dict[f"Message Number {_ + message_num}:"] = {"Content": ""}  # Adding Blank value to dictionary
            mdict[name] = ms_dict
            ldict[name] = extra_links


    datafile = open( "/root/EmailParser/In-Process-JSONS/message_content.json", "w", encoding="utf-8" )  # opening json file for writing
    json.dump( mdict, datafile, indent=4,
               separators=(',', ': ') )  # printing data in nice format to file
    datafile.close()  # Closing File

    datafile = open( "/root/EmailParser/In-Process-JSONS/extra_links.json", "w", encoding="utf-8" )  # opening json file for writing
    json.dump( ldict, datafile, indent=4,
               separators=(',', ': ') )  # printing data in nice format to file
    datafile.close()  # Closing File
    logger.info( ("Content Parsing Complete") )


def tag_visible(element):
    """ This removes the tags I don't want. """

    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]', 'a', 'img']:
        return False
    if isinstance( element, Comment ):
        return False
    return True


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


def content_puller(_, message, message_num):
    """
    :param _: Count/Message Number
    :param message: Message object to be parsed
    :param message_num: Count/Message Number
    :return: it returns the updated Dictionary of Values
    """

    successful = False
    q = f"\t\t{_ + message_num}"  # Print value for keeping track of progress
    print( q )  # Print Statement for keeping track of progress
    body = ""  # Part of precautionary measure for empty inboxes

    if message.is_multipart():  # Starting parse process for multipart Message
        for part in message.walk():  # Built in method for going through multipart methods
            ctype = part.get_content_type()  # Gets content type of Message
            cdispo = part.get( 'Content-Disposition' )  # Checks for attatchment


            # skip any text/plain (txt) attachments
            if (ctype == 'text/plain' or ctype == 'text/html') and 'attachment' not in str(cdispo):
                body = part.get_payload( decode=True )  # Decodes email body into format
                successful = True  # Did it work?
    # not multipart - i.e. plain text,
    else:
        body = message.get_payload( decode=True )  # Decodes email body into format
        successful = True  # Did it work?

    texts = text_from_html( body )  # Cleans Up Body

    return successful, texts  # Returns final Values
