import shutil
from multirun_file_manager import *
import logging


def merger(queue, configurer):
    configurer( queue )
    logger = logging.getLogger()
    logger.info( "Merging Begins" )
    run_count = file_getruncount()
    if not os.path.exists( f"/root/Processed-Data/" ):  # Does the Directory already path exist?
        os.mkdir( f"/root/Processed-Data/" )  # Make directory path

    datafile = open( "/root/EmailParser/In-Process-JSONS/data.json", "r" )  # opening json file for reading
    final_data = json.load( datafile )  # Reads from file
    datafile.close()  # Closes File

    mcdatafile = open( "/root/EmailParser/In-Process-JSONS/message_content.json", "r" )  # opening json file for reading
    mc_data = json.load( mcdatafile )  # Reads from file
    mcdatafile.close()  # Closes File

    madatafile = open( "/root/EmailParser/In-Process-JSONS/message_attachments.json", "r" )  # opening json file for reading
    ma_data = json.load( madatafile )  # Reads from file
    madatafile.close()  # Closes File

    htmldatafile = open( "/root/EmailParser/In-Process-JSONS/MessageLinks.json", "r" )  # opening json file for reading
    html_data = json.load( htmldatafile )  # Reads from file
    htmldatafile.close()  # Closes File

    extra_linksfile = open( "/root/EmailParser/In-Process-JSONS/extra_links.json", "r" )  # opening json file for reading
    extra_links = json.load( extra_linksfile )  # Reads from file
    extra_linksfile.close()  # Closes File

    inbox_idsfile = open( "/root/EmailParser/In-Process-JSONS/inbox_ids.json", "r" )  # opening json file for reading
    inbox_ids = json.load( inbox_idsfile )  # Reads from file
    inbox_idsfile.close()  # Closes File

    datafile = open( "/root/EmailParser/In-Process-JSONS/inbox_vals.json", "r" )  # opening json file for reading
    inbox_vals = json.load( datafile )  # Reads from file
    datafile.close()
      # This tells us how many times this program has been run
    for i, inbox in enumerate( final_data ):  # Loops through final data dictionary
        links_added = 0
        name = final_data[i].get( "Name" )  # Pulls name of Inbox Owner
        '''This sections checks for and handles multiple runs.'''
        message_num = 1
        if run_count > 0:
            message_num = file_getcount( name )
        if name is None:  # Precaution to Skip final Total Count Dictionary
            pass
        else:
            final_data[i]["_id"] = inbox_ids[name]
            print( name )  # Used to keep track of progress
            for _, message in enumerate( inbox["Message List"] ):  # Loops through message list in inbox
                print( _ + message_num )  # Used to keep track of progress

                message["Content"]["Message Content"] = \
                    mc_data[name][f'Message Number {_ + message_num}:'][
                        "Content"]  # Adds Message to final data dictionary
                message["Content"]["Message Content Marked"] = \
                    mc_data[name][f'Message Number {_ + message_num}:'][
                        "Content Marked"]  # Adds Message to final data dictionary
                message["Content"]["Links"] = \
                    html_data[name][f'Message Number {_ + message_num}:'][
                        "Links"]  # Adds Message to final data dictionary

                for link in extra_links[name][f'Message Number {_ + message_num}:'].get( "Links" ):
                    x = link[:-3]
                    if link[:-3] not in ['jpeg', 'jpg', 'png', 'gif', 'tiff', 'psd', 'pdf', 'eps', 'ai', 'indd', 'raw']:
                        if link[:-3] not in ['mp4', 'mov', 'wmv', 'flv', 'avi', 'avchd', 'webm', 'mkv']:
                            if link not in message["Content"]["Links"].get( "Website" ):
                                message["Content"]["Links"]["Website"].append( link )
                            else:
                                message["Content"]["Links"]["Duplicates"]["Website"].append( link )
                                message["Content"]["Links"]["Duplicates"]["Website Count"] = \
                                message["Content"]["Links"]["Duplicates"].get( "Website Count" ) + 1
                        else:
                            if link not in message["Content"]["Links"].get( "Video" ):
                                message["Content"]["Links"]["Video"].append( link )
                            else:
                                message["Content"]["Links"]["Duplicates"]["Video"].append( link )
                                message["Content"]["Links"]["Duplicates"]["Video Count"] = message["Content"]["Links"][
                                                                                               "Duplicates"].get(
                                    "Video Count" ) + 1
                    else:
                        if link not in message["Content"]["Links"].get( "Image" ):
                            message["Content"]["Links"]["Image"].append( link )
                        else:
                            message["Content"]["Links"]["Duplicates"]["Image"].append( link )
                            message["Content"]["Links"]["Duplicates"]["Image Count"] = message["Content"]["Links"][
                                                                                           "Duplicates"].get(
                                "Image Count" ) + 1

                message["Content"]["Has Attachment"] = ma_data[name].get( f'Message Number {_ + message_num}:' )
                if ma_data[name].get(f'Message Number {_ + message_num}:'):
                    message["Content"]["Attachment Name"] = ma_data[name].get( f'Message Number {_ + message_num} Attachment Name:' )
        if name != "None":
            if not os.path.exists( f"/root/Processed-Data/{name}" ):  # Does the Directory already path exist?
                os.mkdir( f"/root/Processed-Data/{name}" )  # Make directory path
    print( "Writing to final files" )
    logger.info( "Writing to final files" )

    for dicts in final_data:
        name = dicts.get( "Name" )  # Pulls name of Inbox Owner
        print( name )
        if name is None:  # Precaution to Skip final Total Count Dictionary
            datafile = open( f"/root/Processed-Data/totals.json", "w" )  # opening json file for writing
            json.dump( dicts, datafile, indent=4, separators=(',', ': ') )  # printing data in nice format to file
            datafile.close()  # Closing File
        else:
            print( "Inbox Info" )
            if run_count > 1:
                message_num = dicts.get("Number Of Messages") + message_num
            else:
                message_num = dicts.get("Number Of Messages") + 1

            inboxinfo = {
                "Name": dicts.get("Name"),
                "Inbox Number": dicts.get("Inbox Number"),
                "ID": dicts.get("_id"),
                "Number Of Messages": message_num
            }

            if not os.path.exists( f"/root/Processed-Data/{name}" ):  # Does the Directory already path exist?
                os.mkdir( f"/root/Processed-Data/{name}" )  # Make directory path

            filename = "/root/Processed-Data/" + name + "/" + name + "info" + ".json"
            with open( filename, "w" ) as datafile:  # opening json file for writing
                json.dump( inboxinfo, datafile, indent=4,
                           separators=(',', ': ') )  # printing data in nice format to file
                datafile.close()  # Closing File

            if not os.path.exists( f"/root/Processed-Data/{name}/Messages" ):  # Does the Directory already path exist?
                os.mkdir( f"/root/Processed-Data/{name}/Messages" )  # Make directory path

            messages = dicts.get( "Message List" )

            for m, message in enumerate( messages ):
                c = m
                message_num = 1
                message["_id"] = name + "." + dicts.get( "_id" ) + "." + str( message.get( "Number" ) )
                print( f"Message Number: {c + message_num}" )
                if run_count > 0:
                    message_num = file_getcount( name )
                filename = f"/root/Processed-Data/" + name + "/Messages/" + name + ".MessageNumber" + str( c + message_num ) + ".json"
                with open( filename, "w" ) as datafile:  # opening json file for writing
                    json.dump( message, datafile, indent=4,
                               separators=(',', ': ') )  # printing data in nice format to file
                    datafile.close()  # Closing File
        try:
            os.rmdir( f"/root/Processed-Data//None" )
        except:
            pass
        ex = os.path.exists( f"/root/Processed-Data/{name}/Attachments" )
        e2 = os.path.exists( f"In-Process-Attachments/{name}" )
        if ex is False and e2 is True:  # Does the Directory already path exist?
            os.mkdir( f"/root/Processed-Data/{name}/Attachments" )  # Make directory path
            if name != "None" or None:
                for entry in sorted( os.scandir( f"/root/EmailParser/In-Process-Attachments/{name}" ),
                                     key=lambda e: e.name ):  # This is looping through each file in the directory above
                    file_str = str( entry.name )
                    if name != "None" or None:
                        origpath = f"/root/EmailParser/In-Process-Attachments/{name}/" + file_str
                        dstpath = f"/root/Processed-Data/{name}/Attachments/" + file_str
                        shutil.move( origpath, dstpath )

    for entry in sorted( os.scandir( f"/root/Processed-Data/" ), key=lambda e: e.name ):
        name = str( entry.name )
        if (name != "Totals") and (name != "totals.json"):
            num_messages = len( os.listdir( f"/root/Processed-Data/{name}/Messages" ) )
            orig_num_messages = 0
            if run_count > 0:
                orig_num_messages = inbox_vals.get( name )
            new_num_messages = num_messages + orig_num_messages

            inbox_vals[name] = new_num_messages
    run_count = inbox_vals.get( "Run Count" )
    new_run_count = run_count + 1
    inbox_vals["Run Count"] = new_run_count

    datafile = open( "/root/EmailParser/In-Process-JSONS/inbox_vals.json", "w" )  # opening json file for reading
    json.dump( inbox_vals, datafile, indent=4 )
    datafile.close()
    logger.info( "Parsing Complete." )
