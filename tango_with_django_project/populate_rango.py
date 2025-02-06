import os 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 
                      'tango_with_django_project.settings') 

import django 
django.setup() 
from rango.models import Category, Page 

def populate(): 
    # First, we will create lists of dictionaries containing the pages 
    # we want to add into each category. 
    # Then we will create a dictionary of dictionaries for our categories. 
    # This might seem a little bit confusing, but it allows us to iterate 
    # through each data structure, and add the data to our models. 
    # Creating categories with the updated views and likes values
    
    python_category = Category.objects.get_or_create(name="Python")[0]
    python_category.views = 128
    python_category.likes = 64
    python_category.save()

    django_category = Category.objects.get_or_create(name="Django")[0]
    django_category.views = 64
    django_category.likes = 32
    django_category.save()

    other_frameworks_category = Category.objects.get_or_create(name="Other Frameworks")[0]
    other_frameworks_category.views = 32
    other_frameworks_category.likes = 16
    other_frameworks_category.save()

    print("Categories populated!")


    python_pages =[  
        {'title': 'Official Python Tutorial',  
         'url':'http://docs.python.org/3/tutorial/'},  
        {'title':'How to Think like a Computer Scientist',  
         'url':'http://www.greenteapress.com/thinkpython/'},  
        {'title':'Learn Python in 10 Minutes',  
         'url':'http://www.korokithakis.net/tutorials/python/'} ] 
    
    django_pages =[ 
        {'title':'Official Django Tutorial', 
         'url':'https://docs.djangoproject.com/en/2.1/intro/tutorial01/'}, 
        {'title':'Django Rocks',  
         'url':'http://www.djangorocks.com/'}, 
        {'title':'How to Tango with Django',  
         'url':'http://www.tangowithdjango.com/'} ] 
    
    other_pages = [  
        {'title':'Bottle',  
         'url':'http://bottlepy.org/docs/dev/'},  
        {'title':'Flask',  
         'url':'http://flask.pocoo.org'} ] 
    
    cats = { 'Python': {'pages': python_pages},  
             'Django': {'pages': django_pages},  
             'Other Frameworks': {'pages': other_pages} } 
    
    # If you want to add more categories or pages, 
    # add them to the dictionaries above. 
    
    # The code below goes through the cats dictionary,then add seach category, 
    # and then adds all the associated pages for that category. 
    for cat,cat_data in cats.items():  
        c= add_cat(cat)  
        for p in cat_data['pages']:  
           add_page(c,p['title'], p['url']) 
    
    # Print out the categories we have added. 
    for c in Category.objects.all(): 
        for p in Page.objects.filter(category=c): 
            print(f'- {c}: {p}') 
 
def add_page(cat, title,url,views=0): 
    p = Page.objects.get_or_create(category=cat,title=title)[0] 
    p.url=url 
    p.views=views 
    p.save() 
    return p 

def add_cat(name): 
    c = Category.objects.get_or_create(name=name)[0] 
    c.save() 
    return c

#Start execution here!
if __name__ == '__main__':
    print('Starting Rango population script...')
    populate()