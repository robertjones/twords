from flask import Flask, render_template, request, redirect, url_for
import os
import string
import re
import random
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


@app.route('/<joined_screen_names>')
def results(joined_screen_names, num_words=3):
    # TODO: combine into a single or fewer Twitter API calls
    screen_names = joined_screen_names.split('+')[:20]
    people = []
    bad_names = []
    for screen_name in screen_names:
        try:
            phrases, num_tweets = common_phrases_in_tweets(screen_name)
            user = twitter.lookup_user(screen_name=screen_name)[0]
            person = {}
            person['name'] = user['name']
            person['description'] = user['description']
            person['profile_image_url'] = user['profile_image_url'
                                               ].replace("_normal", "_400x400")
            person['screen_name'] = screen_name
            person['num_tweets'] = num_tweets
            person['phrases'] = [{'text': p[1], 'freq': p[0]} for p in phrases]
            people.append(person)
        except:
            bad_names.append(screen_name)
    at_screen_names = ["@" + person['screen_name'] for person in people]
    max_freq = max(int(phrase['freq']) for phrase in person['phrases'])
    return render_template('output.html', people=people, num_words=num_words,
                           num_people=max(len(people), 4), max_freq=max_freq,
                           at_screen_names=at_screen_names, 
                           bad_names=bad_names)


@app.route('/', methods=['POST'])
def movealong():
    # TODO: Make a more general parser
    names = request.form['screen_names'] \
                   .replace('@', '').replace(' ', '').replace('\n', '') \
                   .replace('\r', '').split(',')
    return redirect("/" + "+".join(names[:20]))


@app.route('/')
def home():
    brit_politicians = ['david_cameron', 'nick_clegg', 'ed_miliband']
    us_pop = ['katyperry', 'justinbieber', 'britneyspears']
    brit_news = ['mailonline', 'guardian', 'thesunnewspaper']
    tech_cos = ['google', 'twitter', 'facebook']
    bank = [brit_politicians, us_pop, brit_news]
    selection = random.choice(bank)
    return redirect("/" + "+".join(selection))


if __name__ == '__main__':
    app.run(debug=True)
