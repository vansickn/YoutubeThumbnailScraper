from bs4 import BeautifulSoup
import requests
import json
import os

search = input("Write youtube search here: ")

# youtubeRequestLink = "https://www.youtube.com/results?search_query="


def buildLink():
    youtubeRequestLink = "https://www.youtube.com/results?search_query="
    for word in search.split(" "):
        youtubeRequestLink += word + "+"
    youtubeRequestLink = youtubeRequestLink[0:len(youtubeRequestLink)-1]

    return str(youtubeRequestLink)

# buildLink()


def callSoupGenerateJson():
    soup = BeautifulSoup(requests.get(
        buildLink(), timeout=(100, 1000)).text, 'html.parser')
    scripts = soup.findAll("script")
    j = None

    for s in scripts:
        index = str(s).find("{\"")
        # print(index)
        # print(str(s)[index+2:index+17])
        if index == 59:  # just by trial and error I know this to be the line which holds the data I need
            jsonString = (str(s)[index:]).replace(";</script>", "")
            j = json.loads(jsonString)
            # print(j)
            # print(str(s)[index:])
    return j


# callSoupGenerateJson()


def extractThumbnails():
    j = callSoupGenerateJson()
    jsonToVideoRenderers = (j["contents"]["twoColumnSearchResultsRenderer"][
        "primaryContents"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"])
    videoRendererList = []
    for i in range(1, len(jsonToVideoRenderers)):
        videoRendererList.append(jsonToVideoRenderers[i])
    # print(videoRendererList)
    # Write function for this

    thumbnailInformation = []

    for v in videoRendererList:
        thumbnailDict = {}

        try:
            thumbnailDict['LQ'] = v["videoRenderer"]["thumbnail"]["thumbnails"][0]["url"]
        except:
            thumbnailDict["LQ"] = None
        try:
            thumbnailDict["HQ"] = v["videoRenderer"]["thumbnail"]["thumbnails"][1]["url"]
        except:
            thumbnailDict["HQ"] = None
        try:
            thumbnailDict["Title"] = v["videoRenderer"]["title"]["runs"][0]["text"]
        except:
            thumbnailDict["Title"] = None

        thumbnailInformation.append(thumbnailDict)
        print(thumbnailDict)

    createFile(thumbnailInformation)


def createFile(thumbnailInformation):
    if not os.path.isdir("./" + search):
        os.makedirs("./" + search)
        for t in thumbnailInformation:
            if t['Title'] != None:
                print(t["Title"])
                os.makedirs("./" + search + "/"+t["Title"])
                response = requests.get(t["LQ"], stream=True)
                # print(response)
                with open('./' + search + '/' + t["Title"] + '/LQ.png', 'wb') as out_file:
                    out_file.write(response.content)
                if t['HQ'] != None:
                    with open('./' + search + '/' + t["Title"] + '/HQ.png', 'wb') as out_file:
                        out_file.write(response.content)
                del response


# ["sectionListRenderer"]["contents"]["itemSectionRenderer"]["contents"]
extractThumbnails()
