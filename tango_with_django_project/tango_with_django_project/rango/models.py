from django.db import models
from django.contrib import admin
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django import forms
from django.utils import timezone




class Category(models.Model):
    NAME_MAX_LENGTH = 128
    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)

    
    def save(self, *args, **kwargs):
         # Ensure that views is non-negative
        if self.views < 0:
            self.views = 0
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)
    class Meta:
        verbose_name_plural = 'categories'
    def __str__(self):
        return self.name
        
class Page(models.Model): 
    TITLE_MAX_LENGTH = 128
    URL_MAX_LENGTH = 200
    category = models.ForeignKey(Category, on_delete=models.CASCADE) 
    title = models.CharField(max_length=TITLE_MAX_LENGTH)
    url = models.URLField() 
    views = models.IntegerField(default=0) 
    last_visit = models.DateTimeField(default=timezone.now)
    click_count = models.IntegerField(default=0)  # Add click count field


    class Meta:
        verbose_name_plural = 'pages'
    
    def __str__(self): 
        return self.title
    
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')


    def __str__(self): 
        return self.list_display
    
class UserProfile(models.Model):
    # This line is required. Links UserProfile to a user model instance.
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    #The additional attributes we wish to include.
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    def __str__(self):
        return self.user.username  # Now displays the username in Django Admin


