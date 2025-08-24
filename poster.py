import tweepy
from google import genai
import requests


def generate_post_text(prompt_text, gen_api_key_):
    client = genai.Client(api_key=gen_api_key_)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Explain this article summary in an engaging X post (under 280 chars): {prompt_text}.",
    )
    return response.text


def search_image(keywords, api_key):
    """Search for an image on Pixabay using keywords."""
    if not api_key:
        print("Pixabay API key not found in .env")
        return None

    query = "+".join(keywords)
    url = (
        f"https://pixabay.com/api/?key={api_key}&q={query}&image_type=photo&per_page=3"
    )
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("hits"):
            # Return the URL of the first image (highest relevance)
            return data["hits"][0]["webformatURL"]
        else:
            print(f"No images found for keywords: {keywords}")
            return None
    except requests.RequestException as e:
        print(f"Error searching Pixabay: {e}")
        return None


def download_image(image_url, filename="temp_image.jpg"):
    """Download an image from a URL and save it locally."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(image_url, headers=headers, stream=True)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Downloaded image to {filename}")
            return filename
        else:
            print(
                f"Failed to download image from {image_url}: Status {response.status_code}"
            )
            return None
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None


def post_to_x(
    keys,
):
    client = tweepy.Client(
        consumer_key=keys[0],
        consumer_secret=keys[1],
        access_token=keys[2],
        access_token_secret=keys[3],
    )
    media_ids = []
    # Extract keywords from article title and summary
    # Search for an image using keywords
    image_url = search_image(keywords, config["pixabay_api_key"])
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
                print(
                    f"Error uploading media: {e} (Status: {e.response.status_code if e.response else 'Unknown'})"
                )

    try:
        response = client.create_tweet(
            text=post, media_ids=media_ids if media_ids else None
        )
        print(f"Posted to X: {post} (Tweet ID: {response.data['id']})")
    except tweepy.TweepyException as e:
        if e.response.status_code == 429:
            retry_after = int(e.response.headers.get("retry-after", 60))
            print(f"Rate limit hit. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            response = client.create_tweet(text=post)
            print(f"Posted to X after retry: {post}")
        else:
            print(
                f"Error posting to X: {e} (Status: {e.response.status_code if e.response else 'Unknown'})"
            )
