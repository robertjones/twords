from flask import Flask, render_template, request
import os
import string
import re
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
    tweets = twitter.get_user_timeline(screen_name=screen_name,
                                       count=200,
                                       include_rts=False,
                                       include_entities=False)
    tweet_text = "".join([printable_only(tweet['text']) for tweet in tweets])
    return (text_to_counted_phrases(tweet_text, 3)[:5], len(tweets))


@app.route('/<screen_name>')
def results(screen_name, num_words=3):
    phrases, num_tweets = common_phrases_in_tweets(screen_name)
    person = {}
    person['screen_name'] = screen_name
    person['num_tweets'] = num_tweets
    person['phrases'] = [{'text': p[1], 'freq': p[0]} for p in phrases]
    people = [person]
    return render_template('output.html', people=people, num_words=num_words, 
                           num_people=len(people))


@app.route('/')
def home():
    return "Enter a Twitter username after the '/' (e.g. '/twitter') \
    to find the most common phrases."


if __name__ == '__main__':
    app.run(debug=True)
