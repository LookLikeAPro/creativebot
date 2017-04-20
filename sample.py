#!/home/y/bin/python
import tornado.ioloop
import tornado.web
import json
import urllib
import urllib2
import re
import string
import emoji
from random import randint
from random import shuffle
from PyDictionary import PyDictionary
dictionary=PyDictionary()

def createSuggList(options):
        retval = []
        alpha = ["a) ", "b) ", "c) ", "d) "]
        for i in range(len(options)):
                retval.append({"label":alpha[i] + options[i]})
        return retval

def createLyrics(artistName, req):
        #get tracks for artist
    url = "http://api.musixmatch.com/ws/1.1/track.search?q=" + urllib.quote(artistName) +\
            "&apikey=c5dbc5d126314b0288c30342a0b928cc&s_track_rating=desc&f_has_lyrics=1&page_size=10&f_lyrics_language=en"
    resp_json = json.loads(urllib2.urlopen(url).read())
    track_list = resp_json["message"]["body"]["track_list"]

    lyrics = []
    retryCount = 0
    while((not lyrics) and (retryCount < 5)):
        shuffle(track_list)
        track_data = track_list[0]["track"]["track_id"]

        #get lyrics
        url = "http://api.musixmatch.com/ws/1.1/track.lyrics.get?apikey=c5dbc5d126314b0288c30342a0b928cc&track_id=" + str(track_data)
        resp_json = json.loads(urllib2.urlopen(url).read())
        lyricsString = " ".join(resp_json["message"]["body"]["lyrics"]["lyrics_body"].splitlines()[-5:-3]).lower()
        exclude = set(string.punctuation)
        lyrics = "".join(ch for ch in lyricsString if ch not in exclude).split()
        retryCount += 1

    if(not lyrics):
            return {
                    "text": emoji.emojize(":multiple_musical_notes:") +\
                    " Oops, running into an issue, try again " + emoji.emojize(":multiple_musical_notes:"),
                    "renderFormat": "Text",
                    "suggestions": "Try " + artistName + " again"
            }
    missingWord = max(lyrics, key=len)
    lyrics = " ".join(lyrics).replace(missingWord, "_____")

    options = dictionary.synonym(missingWord) if dictionary.synonym(missingWord) is not None else []
    if(len(options) < 3):
        options += dictionary.antonym(missingWord) if dictionary.antonym(missingWord) is not None else []
    if(len(options) < 3):
        options += ["love", "emotions", "never", "honest", "tempted", "baby", "cautious"]

    shuffle(options)
    options.insert(0, missingWord)
    options = options[0:4]
    shuffle(options)
    req['userState']['answer'] = missingWord
    req['userState']['track'] = artistName + " " + track_list[0]["track"]["track_name"]
    return {
            "text": emoji.emojize(":multiple_musical_notes:") + " " +\
            lyrics + " " + emoji.emojize(":multiple_musical_notes:"),
            "renderFormat": "Text",
            "suggestions": createSuggList(options)
    }

def getGifResponse(query):
    queryParams = {"q" : query, "api_key" : "dc6zaTOxFJmzC", "rating" : "pg-13", "limit" : "10"}
    url = "https://api.giphy.com/v1/gifs/search?" + urllib.urlencode(queryParams)
    resp = urllib2.urlopen(url).read();
    resp_json = json.loads(resp)
    return resp_json["data"][randint(0,9)]["images"]["fixed_width"]["url"]

def text(txt):
    return { "text": str(txt),
             "renderFormat": "Text" }

cardTitle = ["0/10 My pet rock could have done better...",
             "1/10 Plants listen to music too, I suppose",
             "2/10 Seems like the backyard bunnies know more",
             "3/10 Perhaps you need to listen to more CDs from the past",
             "4/10 The backup singer could perform better",
             "5/10 You're becoming a little better than that one hit wonder",
             "6/10 Stepping into the shoes of a B-list popstar",
             "7/10 Look out the window of your world tour jet",
             "8/10 You've been nominated for a Grammy",
             "9/10 Gold records shine in your recording studio",
             "10/10 You did it! Music royalty is yours"]

cardImages = ["https://c5.staticflickr.com/9/8695/28429507820_ec39b807eb.jpg",
              "https://c8.staticflickr.com/9/8790/28635963671_fdfaed78d7.jpg",
              "https://c3.staticflickr.com/9/8062/28681270666_2aeb24767d.jpg",
              "https://c3.staticflickr.com/9/8612/28608187002_8721e1bbcf.jpg",
              "https://c1.staticflickr.com/9/8265/28681270576_0e49de6e98.jpg",
              "https://c2.staticflickr.com/8/7636/28635963561_cc050277c7.jpg",
              "https://c1.staticflickr.com/9/8707/28429507760_cf22cc8ef9.jpg",
              "https://c3.staticflickr.com/9/8804/28681270466_110159c9c2.jpg",
              "https://c1.staticflickr.com/9/8884/28608186872_ac7abcd665.jpg",
              "https://c8.staticflickr.com/9/8696/28635963471_6b34e93209.jpg",
              "https://c1.staticflickr.com/9/8822/28681270376_c425155ea3.jpg"]

def imgCard(score, count):
    return { "renderFormat": "Card",
             "template": "pb_image_title_abstract",
             "data": {
               "title": cardTitle[score],
               "summary": "You now have " + str(count) + " fans!",
               "image": cardImages[score]
             },
             "suggestions": [
               {
                 "label": "Play again " + emoji.emojize(":microphone:")
               },
               {
                 "label": "Quit " + emoji.emojize(":sleepy_face:")
               }
             ]
           }

def gif(track, query, txt):
    gifpath = getGifResponse(query)
    return {
             "targetUrl": "https://search.yahoo.com/search?p=" + urllib.quote(re.sub(r'([^\s\w]|_)+', '', track)),
             "assetUrl": gifpath,
             "title": "",
             "renderFormat": "Gif",
             "suggestions": [
                {
                  "label": txt
                },
                {
                  "label": emoji.emojize(":microphone:") +" Another artist"
                },
                {
                  "label": "Quit " + emoji.emojize(":sleepy_face:")
                }
             ]
           }

def response(state, *cards):
    return { "clauses": [ dict([("card" + str(i+1), card) for i, card in enumerate(cards)]) ],
             "userState": state }

# class StartQuiz(tornado.web.RequestHandler):
#     def post(self, *args, **kwargs):
#         print "StartQuiz: %s" % self.request.uri
#         req = json.loads(self.request.body)
#         print "Post data: %s" % json.dumps(req, indent=4)
#         userState = req['userState']
#         artistSlot = req['knownSlots'].get('artist')
#         if artistSlot:
#             userState['artist'] = artistSlot
#             card = createLyrics(artistSlot, req)
#         else:
#             card = text("Pick an artist...")
#         if 'correct' not in userState or 'total' not in userState:
#             userState['correct'] = 0
#             userState['total'] = 0
#         if 'fansCount' not in userState:
#             userState['fansCount'] = 0
#         self.write(json.dumps(response(userState, card), indent=4))

# class StopQuiz(tornado.web.RequestHandler):
#     def post(self, *args, **kwargs):
#         print "StopQuiz: %s" % self.request.uri
#         req = json.loads(self.request.body)
#         print "Post data: %s" % json.dumps(req, indent=4)
#         userState = req['userState']
#         if not userState.get('artist'):
#             card = text(emoji.emojize(":unamused_face:").encode('utf-8') + " You aren't even playing...")
#         else:
#             userState['artist'] = ""
#             card = text(emoji.emojize(":crescent_moon:").encode('utf-8') + " Bye~")
#         userState['correct'] = 0
#         userState['total'] = 0
#         self.write(json.dumps(response(userState, card), indent=4))

class QuizAnswer(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        print "QuizAnswer: %s" % self.request.uri
        print(self.request.body)
        print("======================")
        req = json.loads(self.request.body)
        print "Post data: %s" % json.dumps(req, indent=4)
        userState = req['userState']
        userAnswer = req['userMessage']['utterance'].split()[1]
        if userAnswer == userState.get('answer'):
            userState['correct'] = int(userState['correct']) + 1
            card = gif(userState['track'], userState.get('artist') + " smile", emoji.emojize(":crown:") + " Yay! Play " + userState['artist'] + " again")
        else:
            card = gif(userState['track'], userState.get('artist') + " sad", emoji.emojize(":weary_face:") + " Darn. Try " + userState['artist'] + " again")
        userState['total'] = int(userState['total']) + 1
        if(userState['total'] >= 10):
            userState['fansCount'] = int(userState['fansCount']) + (2 ** int(userState['correct']));
            card = imgCard(int(userState['correct']), int(userState['fansCount']))
            userState['correct'] = 0
            userState['total'] = 0
        self.write(json.dumps(response(userState, card), indent=4))

# class PlaySong(tornado.web.RequestHandler):
#     def post(self, *args, **kwargs):
#         print "PlaySong: %s" % self.request.uri
#         req = json.loads(self.request.body)
#         print "Post data: %s" % json.dumps(req, indent=4)
#         userState = req['userState']
#         artistSlot = req['knownSlots'].get('artist')
#         if artistSlot:
#             card = text("https://www.youtube.com/results?q=" + urllib.quote(artistSlot) + "&sp=EgIQAw%253D%253D")
#         else:
#             card = text("You need an artist name to search on youtube")
#         self.write(json.dumps(response(userState, card), indent=4))

def make_app():
    return tornado.web.Application([
        # (r"/startQuiz", StartQuiz),
        # (r"/stopQuiz", StopQuiz),
        # (r"/playSong", PlaySong),
        (r"/.*", QuizAnswer),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
