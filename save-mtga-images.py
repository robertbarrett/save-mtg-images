import json, requests, os, re, datetime
 
def get_valid_filename(s): #makes a "good" filename to save the file (removes spaces and slashes, etc).
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)
 
def checkdir(dir_path): #checks if the directory for the set already exists. If not it creates it.
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
 
def writefile(url, file_path): #checks if the file already exists. If not it downloads the image and creates the file.
    if not os.path.isfile(file_path):
        r = requests.get(url)
        open(file_path, 'wb').write(r.content)
        #print("Written file: " + file_path + " at: " + str(datetime.datetime.now()))
    else:
        print("Skipping file: " + file_path + "  (already exists) at: " + str(datetime.datetime.now()))
 
def getallcardsdata(): #downloads the current all-cards.json file to memory, doesn't save it to a file. This part takes a while.
    request_url = requests.get('https://api.scryfall.com/bulk-data')
    request_data = requests.get(request_url.json()['data'][3]['download_uri'])
    print("Card Data JSON processing finished at: " + str(datetime.datetime.now()))
    return request_data.json()
 
start=datetime.datetime.now()
print("Writing files to " + os.path.join(os.getcwd(), "art"))
 
print("Starting at: " + str(start))
setDates={}
for card in getallcardsdata(): #reads each card in the all-cards file
    if card['lang'] == 'en' and card['set_type'] in ['core', 'expansion', 'funny', 'draft_innovation', 'alchemy']: 
            #checks if it's an english card. checks if it's a standard set (or un set).
            #see all set types: https://scryfall.com/docs/api/sets
        if card['set'] not in list(setDates.keys()):
            request = requests.get('https://api.scryfall.com/sets/'+card['set'])
            setDates[card['set']]=request.json()['released_at']

        dir_path="art\\" + setDates[card['set']] + '_'+ get_valid_filename(card['set_name']) + '\\'
        checkdir(dir_path) #creates the set directory if it doesn't already exist
        if 'image_uris' in card: #if it's a regular card, writes the file
            writefile(card['image_uris']['large'],dir_path + card['collector_number'] + "_" + get_valid_filename(card['name']) + '.jpg')
            
        else: #if it's a twosided card, writes both sides
            if card['type_line'] != 'Card // Card': 
                #if the type is not "Card // Card" (scryfall has a weird cases where both sides are the same that act weird, ignoring these). 
                #Unfortunately now I can't remember what this check avoids, or what these cards are. TODO: look into this, see if there's a better way.
                writefile(card['card_faces'][0]['image_uris']['large'],dir_path + card['collector_number'] + "_" + get_valid_filename(card['card_faces'][0]['name']) + '_side1.jpg')
                for side_number in range(len(card['card_faces'])-1):
                  writefile(card['card_faces'][side_number+1]['image_uris']['large'],dir_path + card['collector_number'] + "_" + get_valid_filename(card['card_faces'][0]['name']) + '_side'+str(side_number+2)+'_' + card['card_faces'][side_number+1]['name'] + '.jpg')
            else:
                print(str(card))
                    
end=datetime.datetime.now()
print("Finished at " + str(end) + ". Elapsed time: " + str(end-start))
