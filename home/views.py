from django.shortcuts import render
from django.core.management.base import BaseCommand
from newsapi import NewsApiClient
from newsdataapi import NewsDataApiClient
from datetime import datetime, timezone
from django.utils.text import slugify
from newspaper import Article
import requests, time
from .models import News, Gamen, Tech, Animng, Science,Comic,Category
from django.db.models import Q

#For Fatch News From API and Store in Database
from django.core.management import call_command
from django.utils.timezone import now
from datetime import timedelta
from .models import FetchStatus
import threading
from decouple import config

newsapi = NewsApiClient(api_key=config('NEWS_API_KEY'))
api = NewsDataApiClient (apikey=config('NEWSDATA_API_KEY'))

def fetch_news_background():

    status = FetchStatus.objects.get(id=1)

    # STOP if already fetching
    if status.is_fetching:
        return

    # LOCK
    status.is_fetching = True
    status.save()

    try:
        call_command('fetch_news')

        # Delete old news
        call_command('delete_old_news')

        status.last_fetch = now()

    finally:
        # UNLOCK
        status.is_fetching = False
        status.save()

def index(request):
        # headlines = newsapi.get_everything(
        # sources="entertainment-weekly,ign,polygon,techcrunch,the-verge,wired,engadget,ars-technica,new-scientist,national-geographic,scientific-american",
        # language="en",
        # sort_by="publishedAt"
        # )
        # articles = headlines["articles"]

        # for a in articles:
        #         if a["title"] and a["urlToImage"]:
        #                 News.objects.get_or_create(
        #                 url=a["url"],
        #                 defaults={
        #                         'title': a["title"],
        #                         'description': a["description"],
        #                         'image_url': a["urlToImage"],
        #                         'author': a["author"],
        #                         'content': a["content"],
        #                         'published_date': datetime.fromisoformat(a["publishedAt"]),
        #                 }
        #                 )

        #Fatch news from database
        status, created = FetchStatus.objects.get_or_create(id=1)

        should_fetch = False

        if not status.last_fetch:
                should_fetch = True
        elif now() - status.last_fetch > timedelta(hours=12):
                should_fetch = True

        if should_fetch and not status.is_fetching:
                threading.Thread(
                        target=fetch_news_background,
                        daemon=True
                ).start()

        news = News.objects.all().order_by('-published_date')

        #othe
        news=News.objects.all().order_by('-published_date')

        news_data = [
                {
                "nid":n.nid,
                "title": n.title,
                "description": n.description,
                "url": n.url,
                "image": n.image_url,
                "author": n.author,
                "content": n.content,
                "time": n.published_date,
                "slug": slugify(n.title),
                }
                for n in news
        ]


        live_news = news_data[0] if news_data else None
        highlights = news_data[1:5]  
        top_stories = news_data[5:13] 
        latest = news_data[13:]  
        context = {
                "live_news": live_news,
                "highlights": highlights,
                "top_stories": top_stories,
                "latest": latest,
                "slug": slugify(live_news["title"]) if live_news else "",
        }
        return render (request,'../templates/index.html', context)

def news(request):
    # Get the category slug from query params (?category=gaming)
    selected_category = request.GET.get("category", "all")

    if selected_category == "all":
        news = News.objects.all().order_by('-published_date')
    else:
        # Match against Category model (case-insensitive)
        category_obj = Category.objects.filter(name__iexact=selected_category).first()
        if category_obj:
            news = News.objects.filter(category=category_obj).order_by('-published_date')
        else:
            news = News.objects.none()  # if invalid category

    # Convert queryset to list of dicts for template
    news_data = [
        {
        "nid": n.nid,
        "title": n.title,
        "description": n.description,
        "url": n.url,
        "image": n.image_url,
        "author": n.author,
        "content": n.content,
        "time": n.published_date,
        "slug": slugify(n.title),
        }
        for n in news
    ]

    live_news = news_data[0] if news_data else None
    highlights = news_data[1:5]
    latest = news_data[5:]

    context = {
        "category": selected_category,   # <-- use this in template
        "live_news": live_news,
        "highlights": highlights,
        "latest": latest,
    }
    return render(request, "news.html", context)

def list(request):
        # Pull articles (broad categories for features)
        headlines = newsapi.get_everything(
                q="gaming OR movies OR tv OR comics OR tech OR science OR anime OR manga",
                language="en",
                sort_by="publishedAt",  # not latest, more "feature-like"
                sources="ign,polygon,techcrunch,the-verge,wired,engadget,ars-technica,entertainment-weekly",
        )
        articles = headlines.get("articles", [])

        # Transform into usable dicts
        features_data = [
                {
                "title": a["title"],
                "description": a["description"],
                "url": a["url"],
                "image": a["urlToImage"],
                "author": a["author"],
                "time": datetime.fromisoformat(a["publishedAt"].replace("Z", "+00:00")),
                }
                for a in articles if a.get("title") and a.get("urlToImage")
        ]


        list_items = features_data

        context = {
                "list_items": list_items,
        }
        return render (request,'../templates/list.html',context)

def gaming(request):

        # # Keywords you want to allow
        # KEYWORDS = ["games","playstation", "xbox", "nintendo", "pc gaming", "esports", "vr"]

        # 

        # # Fetch articles (still from IGN + Polygon)
        # headlines = newsapi.get_everything(
        #         q="games OR 'playstation' OR 'xbox' OR 'nintendo' OR 'pc' 'gaming' OR 'esports' OR 'vr'",
        #         language="en",
        #         sort_by="publishedAt", 
        #         sources="ign,polygon,,engadget,the-verge",
        # )

        # # Filter only articles that contain keywords in title or description
        # articles = [
        #         a for a in headlines.get("articles", [])
        #         if any(
        #                 kw.lower() in (
        #                 (a.get("title") or "") + (a.get("description") or "")
        #                 ).lower()
        #                 for kw in KEYWORDS
        #         )
        # ]

        # for a in articles:
        #         News.objects.get_or_create(
        #                 url=a["url"],
        #                 defaults={
        #                         'title': a.get("title"),
        #                         'description': a.get("description"),
        #                         'image_url': a.get("urlToImage"),
        #                         'author': a.get("author"),
        #                         'content': a.get("content"),
        #                         'published_date': datetime.fromisoformat(a["publishedAt"].replace('Z', '+00:00')),
        #                         'category': category_obj,
        #                 }
        #                 )
        category_obj = Category.objects.get(name="Gaming")
        gamenews = News.objects.filter(category=category_obj).order_by('-published_date')

        features_data = [
                {
                "nid":n.nid,
                "title": n.title,
                "description": n.description,
                "url": n.url,
                "image": n.image_url,
                "author": n.author,
                "content": n.content,
                "time": n.published_date,
                "slug": slugify(n.title),
                }
                for n in gamenews
        ]

        # # Build your feature data
        # features_data = [
        #         {
        #         "title": a["title"],
        #         "description": a["description"],
        #         "url": a["url"],
        #         "image": a["urlToImage"],
        #         "author": a["author"],
        #         "time": datetime.fromisoformat(a["publishedAt"].replace("Z", "+00:00")),
        #         }
        #         for a in articles if a.get("title") and a.get("urlToImage")
        # ]

        context = {
                "list_items": features_data,
        }
        return render (request,'../templates/gaming.html',context)

def tech(request):

        # Keywords you want to allow
        # KEYWORDS = ["technology", "gadgets", "ai", "artificial intelligence", "smartphones", "software", "hardware"]

        # # Fetch articles (still from IGN + Polygon)
        # headlines = newsapi.get_everything(
        #         q="technology OR gadgets OR ai OR artificial intelligence OR smartphones OR software OR hardware",
        #         language="en",
        #         sort_by="publishedAt", 
        #         sources="techcrunch,the-verge,wired,ars-technica,engadget",
        # )

        # # Filter only articles that contain keywords in title or description
        # articles = [
        #         a for a in headlines.get("articles", [])
        #         if any(
        #                 kw.lower() in (
        #                 (a.get("title") or "") + (a.get("description") or "")
        #                 ).lower()
        #                 for kw in KEYWORDS
        #         )
        # ]
        category_obj = Category.objects.get(name="Tech")

        # for a in articles:
        #         News.objects.get_or_create(
        #                 url=a["url"],
        #                 defaults={
        #                         'title': a.get("title"),
        #                         'description': a.get("description"),
        #                         'image_url': a.get("urlToImage"),
        #                         'author': a.get("author"),
        #                         'content': a.get("content"),
        #                         'published_date': datetime.fromisoformat(a["publishedAt"].replace('Z', '+00:00')),
        #                         'category': category_obj,
        #                 }
        #                 )
        technews = News.objects.filter(category=category_obj).order_by('-published_date')

        features_data = [
                {
                "nid":n.nid,
                "title": n.title,
                "description": n.description,
                "url": n.url,
                "image": n.image_url,
                "author": n.author,
                "content": n.content,
                "time": n.published_date,
                "slug": slugify(n.title),
                }
                for n in technews
        ]

        context = {
                "list_items": features_data,
        }
        return render (request,'../templates/tech.html',context)

def animng(request):
        # Keywords you want to allow
        # KEYWORDS = ["anime", "manga", "otaku", "cosplay", "jpop", "jrock", "japan"]

        # # Fetch articles (still from IGN + Polygon)
        # headlines = newsapi.get_everything(
        #         q="anime OR manga OR otaku OR cosplay OR jpop OR jrock",
        #         language="en",
        #         sort_by="publishedAt", 
        #         sources="ign,polygon,entertainment-weekly,anime-news-network",
        # )

        # # Filter only articles that contain keywords in title or description
        # articles = [
        #         a for a in headlines.get("articles", [])
        #         if any(
        #                 kw.lower() in (
        #                 (a.get("title") or "") + (a.get("description") or "")
        #                 ).lower()
        #                 for kw in KEYWORDS
        #         )
        # ]


        category_obj = Category.objects.get(name="Animang")

        # for a in articles:
        #         News.objects.get_or_create(
        #                 url=a["url"],
        #                 defaults={
        #                         'title': a.get("title"),
        #                         'description': a.get("description"),
        #                         'image_url': a.get("urlToImage"),
        #                         'author': a.get("author"),
        #                         'content': a.get("content"),
        #                         'published_date': datetime.fromisoformat(a["publishedAt"].replace('Z', '+00:00')),
        #                         'category': category_obj,
        #                 }
        #                 )
        animngnews = News.objects.filter(category=category_obj).order_by('-published_date')

        features_data = [
                {
                "nid":n.nid,
                "title": n.title,
                "description": n.description,
                "url": n.url,
                "image": n.image_url,
                "author": n.author,
                "content": n.content,
                "time": n.published_date,
                "slug": slugify(n.title),
                }
                for n in animngnews
        ]

        context = {
                "list_items": features_data,
        }
        return render (request,'../templates/animng.html',context)

def science(request):
        # Keywords you want to allow
        # KEYWORDS = ["sience", "space", "physics", "biology", "chemistry", "environment"]

        # # Fetch articles (still from IGN + Polygon)
        # headlines = newsapi.get_everything(
        #         q="sience OR space OR physics OR biology OR chemistry OR environment",
        #         language="en",
        #         sort_by="publishedAt", 
        #         sources="new-scientist,national-geographic,scientific-american,ars-technica",
        # )

        # # Filter only articles that contain keywords in title or description
        # articles = [
        #         a for a in headlines.get("articles", [])
        #         if any(
        #                 kw.lower() in (
        #                 (a.get("title") or "") + (a.get("description") or "")
        #                 ).lower()
        #                 for kw in KEYWORDS
        #         )
        # ]


        category_obj = Category.objects.get(name="Sciences")

        # for a in articles:
        #         News.objects.get_or_create(
        #                 url=a["url"],
        #                 defaults={
        #                         'title': a.get("title"),
        #                         'description': a.get("description"),
        #                         'image_url': a.get("urlToImage"),
        #                         'author': a.get("author"),
        #                         'content': a.get("content"),
        #                         'published_date': datetime.fromisoformat(a["publishedAt"].replace('Z', '+00:00')),
        #                         'category': category_obj,
        #                 }
        #                 )
        sciencenews = News.objects.filter(category=category_obj).order_by('-published_date')

        features_data = [
                {
                "nid":n.nid,
                "title": n.title,
                "description": n.description,
                "url": n.url,
                "image": n.image_url,
                "author": n.author,
                "content": n.content,
                "time": n.published_date,
                "slug": slugify(n.title),
                }
                for n in sciencenews
        ]

        context = {
                "list_items": features_data,
        }
        return render (request,'../templates/science.html',context)

def comic(request):
    # Keywords you want to allow
        # KEYWORDS = ["comics", "manga", "graphic novels", "superheroes", "villains", "dc comics", "marvel"]
        #         # Fetch articles (still from IGN + Polygon)
        # headlines = newsapi.get_everything(
        #         q="comics OR manga OR graphic novels OR superheroes OR villains OR dc comics OR marvel",
        #         language="en",
        #         sort_by="publishedAt", 
        #         sources="ign,polygon,entertainment-weekly,comicbook-resources",
        # )

        # # Filter only articles that contain keywords in title or description
        # articles = [
        #         a for a in headlines.get("articles", [])
        #         if any(
        #                 kw.lower() in (
        #                 (a.get("title") or "") + (a.get("description") or "")
        #                 ).lower()
        #                 for kw in KEYWORDS
        #         )
        # ]


        category_obj = Category.objects.get(name="Comic")

        # for a in articles:
        #         News.objects.get_or_create(
        #                 url=a["url"],
        #                 defaults={
        #                         'title': a.get("title"),
        #                         'description': a.get("description"),
        #                         'image_url': a.get("urlToImage"),
        #                         'author': a.get("author"),
        #                         'content': a.get("content"),
        #                         'published_date': datetime.fromisoformat(a["publishedAt"].replace('Z', '+00:00')),
        #                         'category': category_obj,
        #                 }
        #                 )
        comicnews = News.objects.filter(category=category_obj).order_by('-published_date')

        features_data = [
                {
                "nid":n.nid,
                "title": n.title,
                "description": n.description,
                "url": n.url,
                "image": n.image_url,
                "author": n.author,
                "content": n.content,
                "time": n.published_date,
                "slug": slugify(n.title),
                }
                for n in comicnews
        ]

        context = {
                "list_items": features_data,
        }
        return render(request, '../templates/comic.html', context)

def cinema(request):
    # Keywords you want to allow
        # KEYWORDS = ["comics", "manga", "graphic novels", "superheroes", "villains", "dc comics", "marvel"]
        #         # Fetch articles (still from IGN + Polygon)
        # headlines = newsapi.get_everything(
        #         q="comics OR manga OR graphic novels OR superheroes OR villains OR dc comics OR marvel",
        #         language="en",
        #         sort_by="publishedAt", 
        #         sources="ign,polygon,entertainment-weekly,comicbook-resources",
        # )

        # # Filter only articles that contain keywords in title or description
        # articles = [
        #         a for a in headlines.get("articles", [])
        #         if any(
        #                 kw.lower() in (
        #                 (a.get("title") or "") + (a.get("description") or "")
        #                 ).lower()
        #                 for kw in KEYWORDS
        #         )
        # ]


        category_obj = Category.objects.get(name="Cinema")

        # for a in articles:
        #         News.objects.get_or_create(
        #                 url=a["url"],
        #                 defaults={
        #                         'title': a.get("title"),
        #                         'description': a.get("description"),
        #                         'image_url': a.get("urlToImage"),
        #                         'author': a.get("author"),
        #                         'content': a.get("content"),
        #                         'published_date': datetime.fromisoformat(a["publishedAt"].replace('Z', '+00:00')),
        #                         'category': category_obj,
        #                 }
        #                 )
        comicnews = News.objects.filter(category=category_obj).order_by('-published_date')

        features_data = [
                {
                "nid":n.nid,
                "title": n.title,
                "description": n.description,
                "url": n.url,
                "image": n.image_url,
                "author": n.author,
                "content": n.content,
                "time": n.published_date,
                "slug": slugify(n.title),
                }
                for n in comicnews
        ]

        context = {
                "list_items": features_data,
        }
        return render(request, '../templates/cinema.html', context)

def detail(request, nid):
        news=News.objects.filter(nid=nid).first()
        top_stories = News.objects.filter(category=news.category).order_by('-published_date')[:8]
        related_news = []
        if news:
                # Take some keywords from the title for related search
                title_words = news.title.split()[:5]  # Take first 5 words as keywords

                # Build Q object to search for any of the words in title or description
                query = Q()
                for word in title_words:
                        query |= Q(title__icontains=word) | Q(description__icontains=word)

                # Exclude current news
                related_news = News.objects.filter(query).exclude(nid=news.nid)[:5] 
        # Search articles using `q`
        # headlines = newsapi.get_everything(
        #         q=title_search,
        #         language="en",
        # )

        # articles = headlines["articles"]
        # features_data = []

        # for a in articles:
        #         if a.get("title") and a.get("urlToImage") and a.get("url"):
        #                 try:
        #                         article = Article(a["url"])
        #                         article.download()
        #                         time.sleep(1)  # Let the article download properly
        #                         article.parse()
        #                         full_content = article.text  # Full scraped text
        #                 except Exception as e:
        #                         print(f"Error scraping {a['url']}: {e}")
        #                         full_content = a.get("description") or ""

        #                 features_data.append({
        #                         "title": a["title"],
        #                         "description": a["description"],
        #                         "url": a["url"],
        #                         "image": a["urlToImage"],
        #                         "author": a["author"],
        #                         "content": full_content,
        #                         "time": datetime.fromisoformat(a["publishedAt"].replace("Z", "+00:00")),
        #                         "slug": slugify(a["title"]),
        #         })

        paragraphs = []
        if news and news.content:
                # Split content by line breaks and remove empty lines
                paragraphs = [p.strip() for p in news.content.split('\n') if p.strip()]

        context = {
                "news": news,
                "paragraphs":paragraphs,
                "related_news": related_news,
                "top_stories": top_stories,
        }

        return render(request, '../templates/detail.html', context)

def topic(request):
        return render (request,'../templates/topic.html')
def search(request):
        query = request.GET.get('q', '')
        news = [] 
        if query:
            news = News.objects.filter( Q(title__icontains=query) | Q(description=query)| Q(author__icontains=query)).order_by('-published_date')  
        else:
            news = []
        news_data = [
                {
                "nid":n.nid,
                "title": n.title,
                "description": n.description,
                "url": n.url,
                "image": n.image_url,
                "author": n.author,
                "content": n.content,
                "time": n.published_date,
                "slug": slugify(n.title),
                }
                for n in news
        ]

        # live_news = news_data[0] if news_data else None
        # highlights = news_data[1:5]
        latest = news_data

        context = { 
               "query": query,
                "latest": latest,
        }
        return render (request,'../templates/search.html',context)