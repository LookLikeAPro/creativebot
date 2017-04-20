from flask import Flask, request, jsonify
from utils.generation import generate
from utils.brainyquote import get_quotes_keyword
from utils.background import get_background
import re
import sys

def text(txt):
    return { "text": str(txt),
        "renderFormat": "Text" }

def twitter(user, text):
    links = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    tweet_card = {
        "renderFormat": "Card",
        "template": "pb_tweet_format",
        "data": {
            # "profileUrl": "https://twitter.com/profileClick",
            "verifiedImage": "https://s.yimg.com/mp/client/img/iconTwitterVerified10@3x-d4809aa221.png",
            # "postUrl": "https://twitter.com/latimesmovies/status/678646816905150464",
            "displayName": user,
            "profileImage": "https://twitter.com/{}/profile_image?size=normal".format(user),
            "body": text,
            "userId": "@"+user,
            "timestamp": "just now",
        }
    }
    # images dont really work?
    # if len(links) > 0:
    #     tweet_card["data"]["image"] = {
    #         "src": links[0],
    #         "width": 598,
    #         "height": 337
    #     }
    return tweet_card

def card(middle, bottom):
    return {
        "renderFormat": "Card",
        "template": "pb_image_overlay_text",
        "data": {
            "image": get_background(),
            # "top_caption": "61",
            "middle_caption": middle,
            "bottom_caption": bottom
        }
    }

def response(state, *cards):
    return { "clauses": [ dict([("card" + str(i+1), card) for i, card in enumerate(cards)]) ],
             "userState": state }

def parse_for_name(s):
    if sys.version_info >= (3, 0):
        return list(filter(lambda x: len(x)>=3, map(lambda x: x.strip(),  s.replace("\n", " ").replace(".", " ").split(" "))))[-1:][0]
    return filter(lambda x: len(x)>=3, map(lambda x: x.strip(),  s.replace("\n", " ").replace(".", " ").split(" ")))[-1:][0]

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def respond():
    # validate_token = request.args.get('validate.token')
    # encoded = request.headers['X-Yahoo-Signature']
    if not request.json:
        body_token = request.data.decode("utf-8")
        print(body_token)
        return body_token
    print(request.json)
    userState = request.json['userState']

    if request.json["intent"] == "sm.imitate_user":
        name = parse_for_name(request.json["userMessage"]["utterance"])
        trycount = 0
        meme = None
        while trycount < 3 and meme == None:
            meme, source = generate(name)
            trycount += 1
        if source == "twitter":
            return jsonify(response(userState, twitter(name, meme)))
        else:
            return jsonify(response(userState, text(meme)))
    elif request.json["intent"] == "sm.quote_user":
        name = parse_for_name(request.json["userMessage"]["utterance"])
        return jsonify(response(userState, card("\""+get_quotes_keyword(name)[0]+"\"", name)))
    else:
        return jsonify(response(userState, text("did not understand you")))

if __name__ == "__main__":
    app.run()
