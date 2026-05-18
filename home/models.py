from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255)
    keywords = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class News(models.Model):
    nid = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    url = models.URLField(max_length=200, blank=True, null=True)
    image_url = models.URLField(max_length=200, blank=True, null=True)
    author = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    published_date = models.DateTimeField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title
    
class Gamen(models.Model):
    gid = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    url = models.URLField(max_length=200, blank=True, null=True)
    image_url = models.URLField(max_length=200, blank=True, null=True)
    author = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    published_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title
    
class Tech(models.Model):
    gid = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    url = models.URLField(max_length=200, blank=True, null=True)
    image_url = models.URLField(max_length=200, blank=True, null=True)
    author = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    published_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title
    
class Animng(models.Model):
    gid = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    url = models.URLField(max_length=200, blank=True, null=True)
    image_url = models.URLField(max_length=200, blank=True, null=True)
    author = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    published_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title
    
class Science(models.Model):
    gid = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    url = models.URLField(max_length=200, blank=True, null=True)
    image_url = models.URLField(max_length=200, blank=True, null=True)
    author = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    published_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title
    
class Comic(models.Model):
    gid = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    url = models.URLField(max_length=200, blank=True, null=True)
    image_url = models.URLField(max_length=200, blank=True, null=True)
    author = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    published_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title
    
class FetchStatus(models.Model):
    last_fetch = models.DateTimeField(null=True, blank=True)
    is_fetching = models.BooleanField(default=False)

    def __str__(self):
        return (
            self.last_fetch.strftime("%Y-%m-%d %H:%M:%S")
            if self.last_fetch
            else "Never Fetched"
        )