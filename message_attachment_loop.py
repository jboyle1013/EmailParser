import base64
import mailbox
from email.parser import BytesParser
from email.policy import default

from headertodict import header_dict_parser
from multirun_file_manager import *
from Logs.listener import *


""" For efficiency reasons, we are using multiprocessing to speed up the parsing process. Yes, I am aware that 
`   I am printing to file instead of returning a value. It is the easiest method I have found for returning values 
    while multiprocessing. """


def message_attachment_loop(directory, queue, configurer):

    configurer( queue )
    logger = logging.getLogger()
    mdict = {}  # Holds all the Message Contents
    run_num = file_getruncount()    # This tells us how many times this program has been run
    for entry in sorted( os.scandir( directory ),
                         key=lambda e: e.name ):  # This is looping through each file in the directory above

        file_str = str(entry.name)  # Turns the name of the entry to a string
        filepath = directory + "/"  # Adds slash  to end of directory name
        file_name = filepath + file_str + "/" # Adds the folder to the filename so it can be read in the right location

        print( file_str )  # Used to keep track of progress

        p = "\t\t\t\t\t\t" + file_str  # Print value for keeping track of progress
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

        if mblen == 0:
            logger.error(f"Inbox {name} is Empty. Attachment Parsing Cannot Run.")
        elif mblen >= 50000:
            logger.error( f"Inbox {name} is too large. Attachment Parsing Cannot Run." )
        else:
            logger.info(f"Attachments Process is working in Directory {name}")
            _ = 0  # Also part of precautionary measure for empty inboxes
            for _, message in enumerate( mb ):  # Loops through messages in inbox

                has_attachment, attachmentname = attachment_puller( _, name, message, message_num )  # Runs the Content Puller method

                ms_dict[f"Message Number {_ + message_num}:"] = has_attachment
                ms_dict[f"Message Number {_ + message_num} Attachment Name:"] = attachmentname
                if has_attachment == True:
                    logger.debug(f"Attachment Found in Message Number {_ + message_num} in Inbox {name}")
            mdict[name] = ms_dict


    datafile = open( "/root/EmailParser/In-Process-JSONS/message_attachments.json", "w",
                     encoding="utf-8" )  # opening json file for writing
    json.dump( mdict, datafile, indent=4,
               separators=(',', ': ') )  # printing data in nice format to file
    datafile.close()  # Closing File
    logger.info(("Attachment Parsing Complete"))


def attachment_puller(_, name, message, message_num):
    """
    :param _: Count/Message Number
    :param message: Message object to be parsed
    :param name: Name of Inbox Owner
    :return: it returns the updated Dictionary of Values
    """

    q = f"\t\t\t\t\t\t{_ + message_num}"  # Print value for keeping track of progress
    print( q )  # Print Statement for keeping track of progress
    cdispo = message.get( 'Content-Disposition' )  # Checks for attatchment
    if message.is_multipart():  # Starting parse process for multipart Message
        for part in message.walk():  # Built in method for going through multipart methods
            if cdispo != None:
                break
            cdispo = part.get( 'Content-Disposition' )  # Checks for attatchment
            if part.is_multipart() and 'attachment' not in str( cdispo ):
                for sub in part.walk():
                    cdispo = sub.get( 'Content-Disposition' )  # Checks for attatchment
                    if cdispo != None:
                        break
        if str( cdispo ) == "inline":
            try:
                attachmentorig = sub.get_payload()
                fname = inline_handler(attachmentorig, name, _, message_num)
                return True, fname

            except:
                attachmentorig = part.get_payload()
                fname = inline_handler( attachmentorig, name, _, message_num )
                return True, fname


        elif cdispo != None:
            att_origfilename = str( cdispo ).split( '"' )[1]
            filetype = att_origfilename.split( '.' )[1]
            if "eml" in filetype:
                attachment = sub.get_payload()
                fname = email_processor( _, attachment, name, att_origfilename, message_num )
                return True, fname
            else:
                attachment = sub.get_payload()

                fp = "/root/EmailParser/In-Process-Attachments/" + name + "/"
                if not os.path.exists( fp ):  # Does the Directory already path exist?
                    os.mkdir( fp )  # Make directory path

                att_filename = name + "." + f"MessageNumber{_ + message_num}" + "." + att_origfilename
                att_file_path = fp + att_filename

                with open( att_file_path, 'wb' ) as attachment_file:
                    decoded_attachment_data = decode_attachmet( attachment )
                    attachment_file.write( decoded_attachment_data )

            return True, att_filename
        else:
            return False, ""
    return False, ""


def email_processor(_, attachment, name, att_origfilename, message_num):
    fp = "/root/EmailParser/In-Process-Attachments/" + name + "/"
    if not os.path.exists( fp ):  # Does the Directory already path exist?
        os.mkdir( fp )  # Make directory path

    h = {}
    headers = header_dict_parser( h, attachment[0] )
    content = email_attachment_content( attachment[0] )
    full_content = {"Content:": content}

    message = {
        "Number:": f"Attachment {_ + message_num}",
        "Headers:": headers,
        "Content:": full_content
    }

    fp = "/root/EmailParser/In-Process-Attachments/" + name + "/"
    if not os.path.exists( fp ):  # Does the Directory already path exist?
        os.mkdir( fp )  # Make directory path

    att_filename = name + "." + f"MessageNumber{_ + message_num}" + "." + att_origfilename
    att_file_path = fp + att_filename + ".json"

    datafile = open( att_file_path, "w" )  # opening json file for writing
    json.dump( message, datafile, indent=4, separators=(',', ': ') )  # printing data in nice format to file
    datafile.close()  # Closing File
    return att_filename


def email_attachment_content(attachment):
    content = "Unrecoverable"
    if attachment.is_multipart():  # Starting parse process for multipart Message
        for part in attachment.walk():  # Built in method for going through multipart methods
            for header in part.items():
                if str( header[1] ) == "base64":
                    body = part.get_payload()
                    content = str( decode_attachmet( body ) )
    return content


def decode_attachmet(attachment):
    attachment = attachment.encode( 'utf-8' )
    decoded_attachment_data = base64.decodebytes( attachment )
    return decoded_attachment_data


def inline_handler(attachmentorig, name, _, message_num):

    att_origfilename = "inlineattachment.txt"
    try:
        unitext = attachmentorig.encode( "ascii", "ignore" )
        attachment = unitext.decode()
        att_origfilename = "inlineattachment.txt"
        fp = "/root/EmailParser/In-Process-Attachments/" + name + "/"
        if not os.path.exists( fp ):  # Does the Directory already path exist?
            os.mkdir( fp )  # Make directory path

        att_filename = name + "." + f"MessageNumber{_ + message_num}" + "." + att_origfilename
        att_file_path = fp + att_filename

        with open( att_file_path, 'w' ) as attachment_file:
            attachment_file.write( attachment )
    except AttributeError:
        attachment = attachmentorig
        att_filename = email_processor( _, attachment, name, att_origfilename, message_num )

    return att_filename