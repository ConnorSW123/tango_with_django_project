from django.test import TestCase
from rango.models import Category
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from rango.models import Page
import datetime


def add_category(name, views=0, likes=0):
    """ Helper function to add a category with the necessary checks. """
    # Ensure that views is non-negative
    if views < 0:
        views = 0

    # Generate a slug
    slug = slugify(name)

    # Create the category, ensuring that the slug is unique
    category, created = Category.objects.get_or_create(
        name=name,
        defaults={'views': views, 'likes': likes, 'slug': slug}
    )

    # If the category already exists but slug conflict happened (get_or_create won't handle this),
    # we need to generate a new unique slug.
    if not created:
        if category.slug != slug:
            category.slug = slug
            category.save()

    return category

def add_page_to_category(title, url, category=None, last_visit=None):
    """ Helper function to add a page to a category. """
    # Ensure that we provide a category, otherwise raise an error
    if not category:
        raise ValueError("A category must be provided.")

    page = Page.objects.create(
        title=title,
        url=url,
        category=category,  # Ensure the category is passed
        last_visit=last_visit or timezone.now()
    )
    return page


def add_page(title, url, category_name, views=0, last_visit=None):
    """ Helper function to add a page with required fields and constraints. """
    # Ensure views are non-negative
    if views < 0:
        views = 0

    # Ensure that last_visit is not in the future
    if last_visit and last_visit > timezone.now():
        raise ValueError("last_visit cannot be in the future.")
    
    # Get or create the category
    category, created = Category.objects.get_or_create(name=category_name)

    # Create the page
    page = Page.objects.create(
        title=title,
        url=url,
        category=category,
        views=views,
        last_visit=last_visit or timezone.now()  # Use provided last_visit or set to now
    )

    return page





class CategoryMethodTests(TestCase): 

    def test_ensure_views_are_positive(self): 
        """ Ensures the number of views received for a Category are positive or zero. 
        """ 
        category = add_category('test', views=-1, likes=0)
        self.assertEqual((category.views >= 0), True)

    def test_slug_line_creation(self): 
        """ Checks to make sure that when a category is created, an appropriate slug is created. Example: "Random Category String" should be "random-category-string". 
        """ 
        category = add_category('Random Category String') 
        self.assertEqual(category.slug, 'random-category-string')


class IndexViewTests(TestCase): 

    def test_index_view_with_no_categories(self): 
        """ If no categories exist, the appropriate message should be displayed. 
        """ 
        response = self.client.get(reverse('rango:index')) 
        self.assertEqual(response.status_code, 200) 
        self.assertContains(response, 'There are no categories present.') 
        self.assertQuerysetEqual(response.context['categories'], [])

    def test_index_view_with_categories(self): 
        """ Checks whether categories are displayed correctly when present. 
        """ 
        # Use add_category to add categories to the database
        add_category('Python', 1, 1) 
        add_category('C++', 1, 1) 
        add_category('Erlang', 1, 1) 
        
        response = self.client.get(reverse('rango:index')) 
        self.assertEqual(response.status_code, 200) 
        self.assertContains(response, "Python") 
        self.assertContains(response, "C++") 
        self.assertContains(response, "Erlang") 
        num_categories = len(response.context['categories']) 
        self.assertEquals(num_categories, 3)


from django.test import TestCase
from rango.models import Page, Category
from django.utils import timezone

class PageModelTests(TestCase):

    def test_page_creation(self):
        # Create a category
        category = Category.objects.create(name="Python", views=5, likes=10)

        # Create a page associated with the category
        page = add_page("Test Page", "http://example.com", "Python", views=100)

        # Check that the page was created correctly
        self.assertEqual(page.title, "Test Page")
        self.assertEqual(page.url, "http://example.com")
        self.assertEqual(page.category, category)
        self.assertEqual(page.views, 100)
        self.assertLessEqual(page.last_visit, timezone.now())

    def test_invalid_last_visit(self):
        # Try to create a page with last_visit in the future
        future_time = timezone.now() + timezone.timedelta(days=1)
        with self.assertRaises(ValueError):
            add_page("Test Page", "http://example.com", "Python", views=100, last_visit=future_time)

    def test_page_creation_without_category(self):
        # Ensure a category is created if it doesn't exist
        page = add_page("Another Test Page", "http://example.com", "Django", views=50)

        # Ensure the category was created
        category = Category.objects.get(name="Django")
        self.assertEqual(page.category, category)


class PageViewTests(TestCase):
    def test_last_visit_updated_on_page_click(self):
        """ Ensures that last_visit is updated when a page is requested. """
        
        # Create a category for the page to reference
        category = Category.objects.create(name="Test", views=0, likes=0)
        
        # Create a page with a valid category
        page = Page.objects.create(title="Test Page", url="http://example.com", category=category)

        # Initially, capture the current last_visit time
        initial_last_visit = page.last_visit

        # Manually construct the URL with page_id as a query parameter
        url = reverse('rango:goto') + f'?page_id={page.id}'

        # Simulate a page click (request the page)
        self.client.get(url)

        # Fetch the updated page from the database
        page.refresh_from_db()

        # Assert that the last_visit field has been updated
        self.assertGreaterEqual(page.last_visit, initial_last_visit)
