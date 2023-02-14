import json
import os
import random
import string


def file_reset(directory):
    inbox_vals_list = {"Run Count": 0}

    for entry in sorted( os.scandir( directory ),
                         key=lambda e: e.name ):  # This is looping through each file in the directory above

        '''These line are for getting the Inbox Identifier from the filename'''
        file_str = str( entry.name )
        n_str = file_str.split( "." )[0]
        if "INBOX" not in n_str:
            name = n_str.split( "_" )[0]
        else:
            name = file_str.split( "." )[1]
        '''This is where the number is set'''
        num = 1
        inbox_vals_list[name] = num

    datafile = open( "/home/kali/Documents/EmailParser/In-Process-JSONS/inbox_vals.json", "w", encoding="utf-8" )  # opening json file for writing
    json.dump( inbox_vals_list, datafile, indent=4 )  # printing data in nice format to file
    datafile.close()  # closing file


def file_getcount(inbox):
    '''These lines read in the values.'''
    datafile = open( "/home/kali/Documents/EmailParser/In-Process-JSONS/inbox_vals.json", "r", encoding="utf-8" )
    inbox_sizes = json.load( datafile )
    datafile.close()
    if inbox in inbox_sizes.keys():  # Was the inbox in the last run?
        inbox_size = inbox_sizes.get( inbox )
        return inbox_size + 1  # Pull size and increase for next message

    else:
        return 1  # Set as empty


def file_getruncount():
    '''This function returns the number of times the parser has run.'''

    datafile = open( "/home/kali/Documents/EmailParser/In-Process-JSONS/inbox_vals.json", "r", encoding="utf-8" )
    inbox_sizes = json.load( datafile )
    datafile.close()

    return inbox_sizes.get( "Run Count" )


def file_idgen(directory):
    inbox_id_list = {}

    for entry in sorted( os.scandir( directory ),
                         key=lambda e: e.name ):  # This is looping through each file in the directory above

        '''These line are for getting the Inbox Identifier from the filename'''
        file_str = str( entry.name )
        n_str = file_str.split( "." )[0]
        if "INBOX" not in n_str:
            name = n_str.split( "_" )[0]
        else:
            name = file_str.split( "." )[1]
        '''This is where the number is set'''
        id = ''.join( random.choice( string.ascii_uppercase +
                                     string.ascii_lowercase + string.digits ) for _ in range( 8 ) )
        if id not in inbox_id_list.items():
            inbox_id_list[name] = id
        else:
            id = ''.join( random.choice( string.ascii_uppercase +
                                         string.ascii_lowercase + string.digits ) for _ in range( 8 ) )
            while id in inbox_id_list.items():
                id = ''.join( random.choice( string.ascii_uppercase +
                                             string.ascii_lowercase + string.digits ) for _ in range( 8 ) )
            inbox_id_list[name] = id

    datafile = open( "/home/kali/Documents/EmailParser/In-Process-JSONS/inbox_ids.json", "w", encoding="utf-8" )  # opening json file for writing
    json.dump( inbox_id_list, datafile, indent=4 )  # printing data in nice format to file
    datafile.close()  # closing file
