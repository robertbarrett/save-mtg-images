import json, requests, os, re, datetime
 
def getValidFilenames(s): #makes a "good" filename to save the file (removes spaces and slashes, etc).
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)
 
def checkDir(dir_path): #checks if the directory for the set already exists. If not it creates it.
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
 
def writeFile(url, file_path): #checks if the file already exists. If not it downloads the image and creates the file.
    if not os.path.isfile(file_path):
        r = requests.get(url)
        open(file_path, 'wb').write(r.content)
        #print("Written file: " + file_path + " at: " + str(datetime.datetime.now()))
    else:
        print("Skipping file: " + file_path + "  (already exists) at: " + str(datetime.datetime.now()))
 
def getAllCardsData(): #downloads the current all-cards.json file to memory, doesn't save it to a file. This part takes a while.
    request_url = requests.get('https://api.scryfall.com/bulk-data')
    request_data = requests.get(request_url.json()['data'][2]['download_uri'])
    print("Card Data JSON processing finished at: " + str(datetime.datetime.now()))
    return request_data.json()

def getWantedSetData(passedSteTypes):
    request = requests.get('https://api.scryfall.com/sets/')
    wantedSets={}
    for set in request.json()['data']:
        if set['set_type'] in passedSteTypes:
            if 'printed_size' in set.keys():
                count=set['printed_size']
            else:
                count=set['card_count']
            wantedSets[set['code']]={'name': set['name'], 'released_at': set['released_at'], 'card_count': count}
    return wantedSets
 
start=datetime.datetime.now()
print("Writing files to " + os.path.join(os.getcwd(), "art"))
 
wantedSets=getWantedSetData(['core', 'expansion', 'funny', 'draft_innovation', 'alchemy'])
allCards=getAllCardsData()
print("Starting at: " + str(start))
numCards=len(allCards)
currentTime=start

for index, card in enumerate(allCards):
    if index % 1000 == 0 and index > 0:
        currentChunkTime=datetime.datetime.now()-currentTime
        currentTime=datetime.datetime.now()
        percentDone=round((index/numCards*100),2)
        timeLeft=((currentTime-start)/percentDone)*(100-percentDone)
        print(str(index) + " of " + str(numCards) + " done. Last chunk: " + str(currentChunkTime) + ". " + str(percentDone) + "% complete. Time left: " + str(timeLeft))
    try:
        if card['lang'] == 'en' and card['set'] in wantedSets.keys():
            if card['collector_number'].isdigit():
                if int(card['collector_number']) <=wantedSets[card['set']]['card_count']:
                    dir_path="art\\" + wantedSets[card['set']]['released_at'] + '_'+ getValidFilenames(card['set_name']) + '\\'
                    checkDir(dir_path)
                    if 'image_uris' in card:
                        writeFile(card['image_uris']['large'],dir_path + card['collector_number'] + "_" + getValidFilenames(card['name']) + '.jpg')
                    elif 'card_faces' in card: #if it's a twosided card, writes both sides
                        cardFileName=card['collector_number'] + "_" + getValidFilenames(card['card_faces'][0]['name']) + '_side1.jpg'
                        writeFile(card['card_faces'][0]['image_uris']['large'],dir_path + cardFileName)
                        for side_number in range(len(card['card_faces'])-1):
                            cardFilename=card['collector_number'] + "_" + getValidFilenames(card['card_faces'][0]['name'] + '_side'+str(side_number+2)+'_' + card['card_faces'][side_number+1]['name']) + '.jpg'
                            writeFile(card['card_faces'][side_number+1]['image_uris']['large'],dir_path + cardFilename)
                    else:
                        print("Weird card found. Doesn't match single sided or double sided test.")
                        print(card)
 
    except Exception as e:
        print(card['name'])
        print(e)


                    
end=datetime.datetime.now()
print("Finished at " + str(end) + ". Elapsed time: " + str(end-start))
