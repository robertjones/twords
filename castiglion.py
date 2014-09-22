from flask import Flask, render_template, request
import os, string, re
from twython import Twython
app = Flask(__name__)


APP_KEY = os.environ['APP_KEY']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']

twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)

def remove_punctuation(s):
    regex1 = re.compile('[%s]' % re.escape(string.punctuation))
    regex2 = re.compile('[%s]' % re.escape("\n"))
    s2 = regex1.sub('', s)
    return regex2.sub(' ', s2)


def clean(s):
    return remove_punctuation(s).casefold()


def list_phrases(words, num):
    return set(" ".join(words[i:i+num]) for i in range(len(words))
               if len(words[i:i+num]) == num)


def count_phrases(phrases, text):
    return set(map(lambda p: (text.count(p), p), phrases))


def text_to_counted_phrases(text, num_words):
    words = clean(text).split()
    phrases = list_phrases(words, num_words)
    return sorted(count_phrases(phrases, " ".join(words)), reverse=True)

def printable_only(text):
	return "".join([c for c in text if c in string.printable])

def common_phrases_in_tweets(screen_name):
	tweets = twitter.get_user_timeline(screen_name=screen_name, count=200, include_rts=False, include_entities=False)
	tweet_text = "".join([printable_only(tweet['text']) for tweet in tweets])
	return text_to_counted_phrases(tweet_text, 3)[:10]

@app.route('/')
def app_page():
    return str(common_phrases_in_tweets("robjones"))

if __name__ == '__main__':
    app.run(debug=True)