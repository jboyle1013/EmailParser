def header_dict_parser(jdict, message):
    hdict = {"Date": [], "Received": [], "Subject": [], "From": [], "To": [],
             "DKIM-signature": [], "Message-ID": [], "Mime-Version": [], "Content-Type" : message.get_content_type(),
             "All Others": {}}  # This dict holds individual header values
    keyvalslist = ["date", "received", "subject", "from", "to", "dkim-signature", "message-id", "mime-version", "content-type" ]
    for item in message.items():  # goes through headers and add then to hdict
        if item[0].lower() == "date":
            hdict["Date"]= item[1]
        elif item[0].lower() == "received":
            hdict["Received"].append(item[1])
        elif item[0].lower() == "subject":
            hdict["Subject"] = item[1]
        elif item[0].lower() == "from":
            hdict["From"] = item[1]
        elif item[0].lower() == "to":
            hdict["To"] = item[1]
        elif item[0].lower() == "dkim-signature":
            hdict["DKIM-signature"] = item[1]
        elif item[0].lower() == "message-id":
            hdict["Message-ID"] = item[1]
        elif item[0].lower() == "mime-version":
            hdict["Mime-Version"] = item[1]
        else:
            if message.is_multipart():  # Starting parse process for multipart Message
                for part in message.walk():
                    for header in part.items():
                        if header[0].lower() not in keyvalslist:
                            val = hdict["All Others"].get( header[0] )

                            if header[0] not in hdict["All Others"].keys():
                                hdict["All Others"][header[0]] = [header[1]]
                            elif header[1] not in hdict["All Others"].get(header[0]):
                                test = header[1] in val
                                hdict["All Others"][header[0]].append(header[1])


    return hdict
