from dotenv import load_dotenv
import os
import base64
from requests import post
from requests import get
import json
import urllib.parse
import webbrowser

load_dotenv()

# spotify stuffs
clientId = os.getenv("CLIENT_ID")
clientSecret = os.getenv("CLIENT_SECRET")
authUrl = "https://accounts.spotify.com/authorize"
tokenUrl = "https://accounts.spotify.com/api/token"
apiBaseUrl = "https://api.spotify.com/v1/"

# youtube stuffs
clientId2 = os.getenv("CLIENT_ID2")
clientSecret2 = os.getenv("CLIENT_SECRET2")
authUrl2 = "https://accounts.google.com/o/oauth2/v2/auth"
apiKey = os.getenv("API_KEY")

def getAuth():
    apiScope = "playlist-read-private"
    apiParams = {
        "client_id": clientId,
        "response_type": "code",
        "scope": apiScope,
        "redirect_uri": "https://google.com",
        "show_dialog": False
    }
    authQuery = f"{authUrl}?{urllib.parse.urlencode(apiParams)}"
    result = get(authQuery)
    if result.history:
        webbrowser.open(result.url, new=0, autoraise=True)
    else:
        print("Request was not redirected")

def getToken(code):
    authString = clientId + ":" + clientSecret
    authBytes = authString.encode("utf-8")
    authBase64 = str(base64.b64encode(authBytes), "utf-8")
    url = tokenUrl
    headers = {
        "Authorization": "Basic " + authBase64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "code": code,
        "redirect_uri": "https://google.com",
        "grant_type": "authorization_code"
    }
    result = post(url, headers=headers, data=data)
    jsonResult = json.loads(result.content)
    token = jsonResult["access_token"]
    return token

def getAuth2():
    apiScope = "https://www.googleapis.com/auth/youtubepartner"
    apiParams = {
        "client_id": clientId2,
        "redirect_uri": "https://google.com",
        "response_type": "token",
        "scope": apiScope
    }
    authQuery = f"{authUrl2}?{urllib.parse.urlencode(apiParams)}"
    result = get(authQuery)
    if result.history:
        webbrowser.open(result.history[0].url)
    else:
        print("Request was not redirected")

def getAuthHeader(token):
    return {"Authorization": "Bearer " + token}

def searchArtist(token, artistName):
    url = "https://api.spotify.com/v1/search"
    headers = getAuthHeader(token)
    query = f"?q={artistName}&type=artist&limit=1"
    queryUrl = url + query
    result = get(queryUrl, headers=headers)
    jsonResult = json.loads(result.content)
    print(jsonResult)

def getPlaylist(token, playlistId):
    url = "https://api.spotify.com/v1/playlists/"
    headers = getAuthHeader(token)
    queryUrl = url + playlistId
    result = get(queryUrl, headers=headers)
    jsonResult = result.json()
    return jsonResult

def addPlaylist(code, playlistId, videoId):
    url = "https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails,id,snippet,status"
    headers = getAuthHeader(code)
    body={
        "snippet": {
            "playlistId": playlistId,
            "position": 0,
            "resourceId": {
                "kind": "youtube#video",
                "videoId": videoId
            }
        }
    }
    result = post(url=url, headers=headers, json=body)

def searchSong(songStr):
    url = f"https://www.googleapis.com/youtube/v3/search?key={apiKey}&q={songStr}&type=video&maxResults=1&part=snippet"
    result = get(url)
    # now get the video id
    toReturn = (json.loads(result.text))["items"][0]["id"]["videoId"]
    return toReturn


def main():
    print("Hello World!")
    playListNameArray = []
    playListIdArray = []

    print("Input the Spotify playlist id:")
    spotifyPlaylistId = input()
    print("Input the Youtube playlist id:")
    youtubePlaylistId = input()

    # get the playlist from spotify
    getAuth()
    print("Paste the redirected google.com url:")
    inputCode = input()
    # now extract the code from the google link
    inputCode = inputCode[29:]
    # print()
    # print(inputCode)

    print("Getting the spotify playlist.")
    playList = getPlaylist(getToken(inputCode), spotifyPlaylistId)

    # create the array for the search terms for youtube
    for item in playList["items"]["items"]:
        artistStr = ""
        count = 0
        for artist in item["item"]["artists"]:
            if count == 0:
                artistStr = artistStr + ' ' + artist["name"]
            else:
                artistStr = artistStr + ', ' + artist["name"]
            count = count + 1
        playListNameArray.append(item["item"]["name"] + artistStr)
        # playListNameArray.append(item["item"]["name"] + artistStr + " \"topic\"")
    
    print()
    print(playListNameArray)
    print()
    
    # search the songs then add them into an array of youtube video ids
    for str in playListNameArray:
        playListIdArray.append(searchSong(str))
    print("Done.")

    # add the songs into youtube playlist
    inputCode = None
    getAuth2()
    print("Paste the redirected google.com url:")
    inputCode = input()
    # now extract the code from the google link
    tokenIndex = inputCode.find("token=")
    tokenEndIndex = inputCode.find("&token_type")
    inputCode = inputCode[tokenIndex+6:-(len(inputCode)-tokenEndIndex)]
    # print()
    # print(inputCode)

    print("Adding the songs into Youtube playlist.")
    for id in playListIdArray:
        addPlaylist(inputCode, youtubePlaylistId, id)
    print("Done.")
        




if __name__ == "__main__":
    main()
