from StringIO import StringIO
import re
import webbrowser
import sys

import requests
from twitpic import twitpic2 as twitpic
import tweepy
import Image

import sneaky

TWITPIC_KEY = "58821aa6805fadbb0dd3bbf2bb4b1191"
SNEAKY_URL = "https://github.com/zwass/Sneaky"
TWITPIC_FULL_URL = "http://twitpic.com/show/full/%s"
CONSUMER_KEY =	"HiFrPctMe7uMZI8k1jaeQ"
CONSUMER_SECRET = "3cK8vi4eujgteK3MbKvhcIwCtgNR79ICq56cto5oyvI"

class TwitPicUploadException(Exception):
    """Raised when uploading to TwitPic fails"""
    pass

class TwitterPoster():
    """Posts images as tweets to Twitter"""
    def __init__(self):
        """Setup auth with Twitter and TwitPic

        Using OAuth allows us to do this without having any access to the
        user's credentials."""
        #first OAuth with twitter
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        try:
            webbrowser.open_new_tab(auth.get_authorization_url())
        except tweepy.TweepError:
            print "Error! Failed to get request token."

        verifier = raw_input("Auth PIN: ")
        auth.get_access_token(verifier)
        #at this point, we are done with OAuth

        api = tweepy.API(auth)
        self.twitter = api

        secret = api.auth.access_token.secret
        key = api.auth.access_token.key

        #create the twitpic client using the Twitter OAuth keys
        self.twitpic = twitpic.TwitPicOAuthClient(
            consumer_key = CONSUMER_KEY,
            consumer_secret = CONSUMER_SECRET,
            access_token = "oauth_token=%s&oauth_token_secret=%s"  % (key, secret),
            service_key = TWITPIC_KEY)

    def post_image(self, message, filename):
        """Post an image to TwitPic, with corresponding tweet to Twitter"""
        #first twitpic
        params = {'message': message,
                  'media': filename}
        try:
            response = self.twitpic.create("upload", params)
            img_url = response['url']
        except:
            raise TwitPicUploadException()
        #now twitter
        status = "%s %s" % (message, img_url)
        self.twitter.update_status(status)

class TwitterGetter():
    """Gets images from Twitter and TwitPic for decoding"""
    def __init__(self):
        """Set up our twitter api"""
        self.twitter = tweepy.API()

    def get_image_urls(self, username):
        """Retrieves URLs for the TwitPic images in the user's last 20 tweets"""
        statuses = self.twitter.user_timeline(screen_name=username)
        urls = []
        for tweet in statuses:
            #only look if Sneaky posted this tweet
            if tweet.source_url != SNEAKY_URL:
                continue
            match = re.search("http://[^ ]+", tweet.text)
            if match:
                urls.append(match.group(0))
        return urls

    def get_twitpic_img(self, url):
        """Given a twitpic url, return a PIL Image"""
        #first check if this link redirects to twitpic
        r = requests.get(url)
        if r.url.find("twitpic.com") == -1:
            return None
        img_id = r.url.split("/")[-1]
        full_url = TWITPIC_FULL_URL % (img_id)
        return Image.open(StringIO(requests.get(full_url).content))


if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        print "Missing args. Do you want to 'read' or 'post'?"
        exit()

    if args[1] == "post":
        if len(args) < 4:
            print "Usage: %s post <message_text_file> <image_file>" % (args[0])
            exit()
        try:
            intxt = open(args[2]).read()
        except:
            print "Invalid input text"
        try:
            inimg = Image.open(args[3])
        except:
            print "Invalid input image"
        #encode the image
        encoder = sneaky.ImgEncoder(inimg)
        encoder.encode(intxt, True)
        encoder.save("tmp_for_twitter.png")

        try:
            poster = TwitterPoster()
        except:
            print "Error authorizing with Twitter"
            exit()
        poster.post_image("A secret message:", "tmp_for_twitter.png")

    elif args[1] == "read":
        if len(args) < 3:
            print "Usage: %s read <twitter_username>" % (args[0])
            exit()
        getter = TwitterGetter()
        img_urls = getter.get_image_urls(args[2])
        if len(img_urls) == 0:
            print "No messages to be read"
            exit()
        for url in img_urls:
            raw_input("Next message (Enter to continue):")
            try:
                img = getter.get_twitpic_img(url)
                decoder = sneaky.ImgEncoder(img)
                print decoder.decode(None, True)
            except:
                print "Failed to read message"
    else:
        print "Choose 'read' or 'post'"