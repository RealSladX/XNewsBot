import tweepy

consumer_key = 'YOUR_API_KEY'
consumer_secret = 'YOUR_API_SECRET_KEY'
access_token = 'YOUR_ACCESS_TOKEN'
access_token_secret = 'YOUR_ACCESS_TOKEN_SECRET'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

try:
    api.update_status('Hello, world!')
    print('Tweet successfully sent!')
except Exception as e:
    print('Error:', e)
