from crawler import curate_tech_news, parse_article
from approval import send_approval_email, send_test_email
import json
import nltk
from poster import generate_post_text, search_image, download_image
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# Download NLTK data for keyword extraction
plt.rcParams["font.family"] = 'FiraCode Nerd Font'
with open('config.json', 'r') as f:
    config = json.load(f)


x_keys = [config['x_api_credentials']['consumer_key'],
        config['x_api_credentials']['consumer_secret'],
        config['x_api_credentials']['access_token'],
        config['x_api_credentials']['access_token_secret']]

rss_urls = ["https://www.defensenews.com/arc/outboundfeeds/rss/category/unmanned/?outputType=xml", "https://www.technologyreview.com/feed/", "https://www.wired.com/feed/tag/ai/latest/rss" ,"https://www.techmeme.com/feed.xml", "https://techcrunch.com/feed/", "https://www.theverge.com/rss/index.xml", "https://spectrum.ieee.org/customfeeds/feed/all-topics/rss", "https://breakingdefense.com/full-rss-feed/?v=2","https://feeds.feedburner.com/venturebeat/SZYF", "https://www.twz.com/feed" ]
tech_keywords = ['AI', 'blockchain', 'quantum', 'VR', 'AR', 'robotics', 'LLM', 'military', 'unmanned', 'drone', 'autonomous', 'breakthrough', 'cryptocurrency', 'billion', 'trillion', 'machine', 'deep', 'algorithm', 'learning', 'arrested', 'disaster', 'security', 'risk', 'danger', 'warfare', 'advanced', 'advancement', 'discover', 'streamer', 'youtuber', 'director', 'president', 'auto', 'robot']

if __name__ == "__main__":
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('punkt')
        nltk.download('punkt_tab')
        nltk.download('stopwords')
    res = curate_tech_news(rss_urls, tech_keywords)
    top = []
    for r in res:
        fig, ax = plt.subplots(layout='tight')
        r['post_text'] = generate_post_text(r['summary'], config['genai_key'])
        img_path = download_image(r['img'])
        ax.text(-1.5, 1.2, r['post_text'], fontsize=14, wrap=True)
        if img_path:
            image = plt.imread(img_path)
            ax.imshow(image)
        else:
            try:
                image_url = search_image(r['keywords'], config['pixabay_api_key'])
            except Exception as e:
                print(f"{e}")
            else:
                image_path = download_image(image_url)
                if image_path:
                    image = plt.imread(image_path)
                    ax.imshow(image)
        plt.show()
        top.append(r)
    # while(count < 5):
    #     res = crawl_tech_news()
    #     top = curate_articles(res)
    #     print(top)
    #     # send_approval_email(top, 'imsladx@gmail.com')
    #
    #     post=top[0]['title']
    #     
    #     time.sleep(300)
