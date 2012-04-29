import webbrowser

from twitpic import twitpic2 as twitpic
import tweepy

CONSUMER_KEY =	"HiFrPctMe7uMZI8k1jaeQ"
CONSUMER_SECRET = "3cK8vi4eujgteK3MbKvhcIwCtgNR79ICq56cto5oyvI"

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
try:
    webbrowser.open_new_tab(auth.get_authorization_url())
except tweepy.TweepError:
    print "Error! Failed to get request token."

verifier = raw_input("Auth PIN: ")
auth.get_access_token(verifier)

api = tweepy.API(auth)

secret = api.auth.access_token.secret
key = api.auth.access_token.key

twitpic_key = "58821aa6805fadbb0dd3bbf2bb4b1191"

twitpic = twitpic.TwitPicOAuthClient(
    consumer_key = CONSUMER_KEY,
    consumer_secret = CONSUMER_SECRET,
    access_token = "oauth_token=%s&oauth_token_secret=%s"  % (key, secret),
    service_key = twitpic_key
)

params = {'message': "test test",
          'media': "test.bmp"}

print twitpic.create("upload", params)