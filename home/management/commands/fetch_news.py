from django.core.management.base import BaseCommand
from newsapi import NewsApiClient
from newspaper import Article
from datetime import datetime
from home.models import News, Category
from decouple import config

class Command(BaseCommand):
    help = 'Fetch news articles and store in DB'

    def handle(self, *args, **kwargs):
        print("Starting fetch_news command...")

        newsapi = NewsApiClient(api_key=config('NEWS_API_KEY'))
        categories = Category.objects.all()
        print(f"Found {categories.count()} categories.")

        for idx, cat in enumerate(categories):
            print(f"Processing category {idx + 1}/{categories.count()}: {cat.name}")

            keywords = cat.keywords.split(',')
            query = " OR ".join(keywords)
            print(f"Query: {query}")

            try:
                response = newsapi.get_everything(
                    q=query,
                    language="en",
                    sort_by="publishedAt",
                    sources="ign,polygon,techcrunch,the-verge,entertainment-weekly,hollywood-reporter,new-scientist,national-geographic,scientific-american,ars-technica,anime-news-network"
                )
                print(f"Fetched {len(response.get('articles', []))} articles from NewsAPI.")
            except Exception as e:
                print(f"Error fetching from NewsAPI: {e}")
                continue

            articles = response.get("articles", [])

            for article_idx, a in enumerate(articles):
                print(f"Processing article {article_idx + 1}/{len(articles)}")

                try:
                    article_url = a.get("url")
                    article = Article(article_url)
                    article.download()
                    article.parse()
                    full_content = article.text

                    News.objects.get_or_create(
                        url=a["url"],
                        defaults={
                            'title': a.get("title"),
                            'description': a.get("description"),
                            'image_url': a.get("urlToImage"),
                            'author': a.get("author"),
                            'content': full_content,
                            'published_date': datetime.fromisoformat(a["publishedAt"].replace('Z', '+00:00')),
                            'category': cat,
                        }
                    )
                except Exception as e:
                    print(f"Error processing article: {e}")
 
        print("Finished fetch_news command.")