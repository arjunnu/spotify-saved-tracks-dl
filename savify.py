import urllib2
import json
import re
import subprocess

#TODO: Remove the text between braces for any keyword. It is just noise, supposed to be more information, but misleading youtube
#TODO: From the track name, delete text that is after a hyphen (-). This text is misleading the search

#FIXME: Ideally, all spotify songs should be available on youtube. If something is missing, items[0] in youtube search json response is missing (Essentially 0 items in the response). Revisit all those songs. Probably due to above issue.
"""
  "href" : "https://api.spotify.com/v1/me/tracks?offset=0&limit=50",
  "items" : [ {
    "added_at" : "2016-03-12T14:42:16Z",
    "track" : {
      "album" : {
        "album_type" : "album",
        "available_markets" : [ "CA", "MX", "US" ],
        "external_urls" : {
          "spotify" : "https://open.spotify.com/album/0x3uUHhj8bCoM5Uzi5FNIv"
        },
        "href" : "https://api.spotify.com/v1/albums/0x3uUHhj8bCoM5Uzi5FNIv",
        "id" : "0x3uUHhj8bCoM5Uzi5FNIv",
        "images" : [ {
          "height" : 640,
          "url" : "https://i.scdn.co/image/e69cbed58994d20ac27f2e5f32487c3b39c451d5",
          "width" : 638
        }, {
          "height" : 300,
          "url" : "https://i.scdn.co/image/2d5684c584ae572e0be422f685eab8983c01f0b7",
          "width" : 299
        }, {
          "height" : 64,
          "url" : "https://i.scdn.co/image/e035a6099174b9042d55f1892f150166dea447fe",
          "width" : 64
        } ],
        "name" : "Tubthumper",
        "type" : "album",
        "uri" : "spotify:album:0x3uUHhj8bCoM5Uzi5FNIv"
      },
"""

keywords = []
next_url=""
total=0
auth="ENTER_YOUR_SPOTIFY_API_KEY_HERE"

def run_http_get(url,auth):
        req = urllib2.Request(url)#'https://api.spotify.com/v1/me/tracks?offset=0&limit=50')
        req.add_header('Accept', 'application/json')
        req.add_header('Authorization', 'Bearer '+auth)
        resp = urllib2.urlopen(req)
        content = resp.read()
        parsed_json = json.loads(content)
        #print parsed_json
	return parsed_json

def run_http_spotify(url,auth):
	parsed_json = run_http_get(url,auth)
	global next_url
	next_url=parsed_json["next"]
	global total
	total=parsed_json["total"]
	#print next_url
	#print total
	total_items = len(parsed_json["items"])
	#print "Total Items", total_items
	for i in range(0,total_items):
		keywordstr=""
		keywordstr = parsed_json["items"][i]["track"]["name"]
		artist_num = len(parsed_json["items"][i]["track"]["artists"])
		#for j in range(0,artist_num):
		#	keywordstr+="+"
		#	keywordstr+=parsed_json["items"][i]["track"]["artists"][j]["name"]
		#
		#	We won't need multiple artist names to figure out youtube song. Just the first artist name would do.
		#	Multiple artists names make it difficult to find the song on youtube
		#
		keywordstr+="+"
		keywordstr+=parsed_json["items"][i]["track"]["artists"][0]["name"]
		anotherkeywordstr = re.sub(r'\([^)]*\)', '', keywordstr)
		newkeywordstr = anotherkeywordstr.replace(" ","+")
		keywordstr = newkeywordstr.replace("-","").encode('utf-8').strip()
		#print "Search String is:", keywordstr
		#keywords.append(unicode(keywordstr))
		keywords.append(keywordstr)
	
run_http_spotify('https://api.spotify.com/v1/me/tracks?offset=0&limit=50',auth)
#print "Next run", next_url
while not next_url is None:
	#print "Running", next_url
	run_http_spotify(next_url,auth)
print keywords

urls_to_download=[]

for keyword in keywords:
	ytget = 'https://www.googleapis.com/youtube/v3/search?part=snippet&q='+keyword+'+official&key=ENTER_YOUR_YOUTUBE_API_KEY_HERE'
	print "Running get on", ytget
        req = urllib2.Request(ytget)
        resp = urllib2.urlopen(req)
        content = resp.read()
        parsed_json = json.loads(content)
	if len(parsed_json["items"]) > 0:
        	videoId=parsed_json["items"][0]["id"]["videoId"]
		yturl='https://www.youtube.com/watch?v='+videoId
		urls_to_download.append(yturl)	
		print "Youtube url for ",keyword," is: ",yturl
	else:
		print "There was some issue with keyword:", keyword

for url in urls_to_download:
	#youtube-dl -x --audio-format mp3 https://www.youtube.com/watch?v=1w7OgIMMRc4
	subprocess.call(["youtube-dl", "-x", "--audio-format", "mp3", url])
	




