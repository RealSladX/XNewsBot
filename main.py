from crawler import crawl_tech_news
from curator import curate_articles
from approval import send_approval_email, send_test_email
import json
import tweepy
import time
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import requests

def extract_keywords(text):
    """Extract relevant keywords from text using NLTK."""
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text.lower())
    # Filter out stopwords, punctuation, and short words
    keywords = [word for word in tokens if word.isalnum() and word not in stop_words and len(word) > 3]
    # Return top 3 keywords (or fewer if not enough)
    return keywords[:3]

def search_image(keywords, api_key):
    """Search for an image on Pixabay using keywords."""
    if not api_key:
        print("Pixabay API key not found in .env")
        return None

    query = '+'.join(keywords)
    url = f"https://pixabay.com/api/?key={api_key}&q={query}&image_type=photo&per_page=3"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get('hits'):
            # Return the URL of the first image (highest relevance)
            return data['hits'][0]['webformatURL']
        else:
            print(f"No images found for keywords: {keywords}")
            return None
    except requests.RequestException as e:
        print(f"Error searching Pixabay: {e}")
        return None
def download_image(image_url, filename='temp_image.jpg'):
    """Download an image from a URL and save it locally."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(image_url, headers=headers, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Downloaded image to {filename}")
            return filename
        else:
            print(f"Failed to download image from {image_url}: Status {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None
# Download NLTK data for keyword extraction

with open('config.json', 'r') as f:
    config = json.load(f)


if __name__ == "__main__":
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('punkt')
        nltk.download('punkt_tab')
        nltk.download('stopwords')
    count = 0

    while(count < 5):
        res = crawl_tech_news()
        top = curate_articles(res)
        print(top)
        # send_approval_email(top, 'imsladx@gmail.com')
        auth = tweepy.OAuth1UserHandler(
            config['x_api_credentials']['consumer_key'],
            config['x_api_credentials']['consumer_secret'],
            config['x_api_credentials']['access_token'],
            config['x_api_credentials']['access_token_secret']
        )

        api = tweepy.API(auth)

        client = tweepy.Client(
            consumer_key=config['x_api_credentials']['consumer_key'],
            consumer_secret=config['x_api_credentials']['consumer_secret'],
            access_token=config['x_api_credentials']['access_token'],
            access_token_secret=config['x_api_credentials']['access_token_secret']
        )

        post=top[0]['title']
        media_ids = []
            # Extract keywords from article title and summary
        text = f"{post}"
        keywords = extract_keywords(text)
        print(f"Keywords for image search: {keywords}")

        # Search for an image using keywords
        image_url = search_image(keywords, config['pixabay_api_key'])
        if image_url:
            # Download the image
            filename = download_image(image_url)
            if filename:
                try:
                    # Upload image using v1.1 API
                    media = api.media_upload(filename)
                    media_ids = [media.media_id]
                    print(f"Uploaded image, media_id: {media.media_id}")
                    print(f"Deleted temporary file {filename}")
                except tweepy.TweepyException as e:
                    print(f"Error uploading media: {e} (Status: {e.response.status_code if e.response else 'Unknown'})")


        try:
            response = client.create_tweet(text=post, media_ids=media_ids if media_ids else None)
            print(f"Posted to X: {post} (Tweet ID: {response.data['id']})")
        except tweepy.TweepyException as e:
            if e.response.status_code == 429:
                retry_after = int(e.response.headers.get('retry-after', 60))
                print(f"Rate limit hit. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                response = client.create_tweet(text=post)
                print(f"Posted to X after retry: {post}")
            else:
                print(f"Error posting to X: {e} (Status: {e.response.status_code if e.response else 'Unknown'})")
        time.sleep(300)
