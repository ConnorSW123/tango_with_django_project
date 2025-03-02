from django.shortcuts import render, redirect
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserProfileForm
from django.urls import reverse
#from rango.forms import UserForm, UserProfileForm
#from django.contrib.auth import authenticate, login, logout
#from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.bing_search import run_query
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.models import User
from rango.models import UserProfile
from django.utils import timezone
from django.shortcuts import get_object_or_404


def index(request):

    # Query the database for a list of ALL categories currently stored.
    # Order the categories by the number of likes in descending order.
    # Retrieve the top 5 only -- or all if less than 5.
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list

    visitor_cookie_handler(request)

    response = render(request, 'rango/index.html', context=context_dict)
    return response
    
@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
    
    if category is None:
        return redirect(reverse('rango:index'))  
    
    form = PageForm()
    
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)
    
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)


def about(request):
    # prints out whether the method is a GET or a POST 
    print(request.method) 
    # prints out the user name, if no one is logged in it prints `AnonymousUser` 
    print(request.user) 
    visitor_cookie_handler(request)
    visits = request.session.get('visits', 1)

    return render(request, 'rango/about.html',{'visits': visits})


def show_category(request, category_name_slug):
    context_dict = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category).order_by('-views')

        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None

    # Start new search functionality code.
    if request.method == 'POST':
        if request.method == 'POST':
            query = request.POST['query'].strip()
            
            if query:
                context_dict['result_list'] = run_query(query)
                context_dict['query'] = query
    # End new search functionality code.
    
    return render(request, 'rango/category.html', context_dict)



@login_required
def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return redirect(reverse('rango:index')) 
        else:
            print(form.errors)

    return render(request, 'rango/add_category.html', {'form': form}) 



@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')


# A helper method
def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

# Updated the function definition
def visitor_cookie_handler(request):
    # Get the number of visits to the site.
    # We use the COOKIES.get() function to obtain the visits cookie.
    # If the cookie exists, the value returned is casted to an integer.
    # If the cookie doesn't exist, then the default value of 1 is used.
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request, 'last_visit',str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],'%Y-%m-%d %H:%M:%S')

    # If it's been more than a day since the last visit...
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        # Update the last visit cookie now that we have updated the count
        request.session['last_visit'] = str(datetime.now())
    else:
        # Set the last visit cookie
        request.session['last_visit'] = str(datetime.now())

    # Update/set the visits cookie
    request.session['visits'] = visits


from django.shortcuts import render
from .bing_search import run_query  # Ensure you import your Bing search function


def goto_url(request):
    if request.method == 'GET':
        page_id = request.GET.get('page_id')

        try:
            selected_page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return redirect(reverse('rango:index'))
        selected_page.last_visit = timezone.now()
        selected_page.views = selected_page.views + 1
        selected_page.save()

        return redirect(selected_page.url)

    return redirect(reverse('rango:index'))





class AboutView(View):
    def get(self, request): 
        context_dict = {}

        visitor_cookie_handler(request) 
        context_dict['visits'] = request.session['visits']

        return render(request,
                      'rango/about.html', 
                      context_dict)

class AddCategoryView(View):
    @method_decorator(login_required)
    def get(self, request): 
        form = CategoryForm()
        return render(request, 'rango/add_category.html', {'form': form})

    @method_decorator(login_required)
    def post(self, request):
        form = CategoryForm(request.POST)

        if form.is_valid(): 
            form.save(commit=True)
            return redirect(reverse('rango:index'))
        else:
            print(form.errors)

        return render(request, 'rango/add_category.html', {'form': form})




class IndexView(View):
    def get(self, request):
        # Get top 5 categories by likes
        category_list = Category.objects.order_by('-likes')[:5]
        # Get top 5 pages by views
        page_list = Page.objects.order_by('-views')[:5]

        context_dict = {
            'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!',
            'categories': category_list,
            'pages': page_list  # Pass pages to template
        }

        visitor_cookie_handler(request)

        # Debugging print
        print("Pages in context:", [(page.id, page.title) for page in page_list])

        return render(request, 'rango/index.html', context_dict)


class AddPageView(View):
    @method_decorator(login_required)
    def get(self, request, category_name_slug):
        try:
            category = Category.objects.get(slug=category_name_slug)
        except Category.DoesNotExist:
            category = None

        if category is None:
            return redirect(reverse('rango:index'))

        form = PageForm()
        context_dict = {'form': form, 'category': category}
        return render(request, 'rango/add_page.html', context_dict)

    @method_decorator(login_required)
    def post(self, request, category_name_slug):
        try:
            category = Category.objects.get(slug=category_name_slug)
        except Category.DoesNotExist:
            category = None

        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)

        context_dict = {'form': form, 'category': category}
        return render(request, 'rango/add_page.html', context_dict)

class ShowCategoryView(View):
    def get_context_data(self, category_name_slug):
        context_dict = {}
        try:
            category = Category.objects.get(slug=category_name_slug)
            pages = Page.objects.filter(category=category).order_by('-views')

            context_dict['pages'] = pages
            context_dict['category'] = category
        except Category.DoesNotExist:
            context_dict['category'] = None
            context_dict['pages'] = None
        return context_dict

    def get(self, request, category_name_slug):
        context_dict = self.get_context_data(category_name_slug)
        return render(request, 'rango/category.html', context_dict)

    def post(self, request, category_name_slug):
        context_dict = self.get_context_data(category_name_slug)

        query = request.POST.get('query', '').strip()
        if query:
            context_dict['result_list'] = run_query(query)
            context_dict['query'] = query

        return render(request, 'rango/category.html', context_dict)

class GotoUrlView(View):
    def get(self, request):
        page_id = request.GET.get('page_id')

        try:
            selected_page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return redirect(reverse('rango:index'))

        selected_page.views = selected_page.views + 1
        selected_page.click_count = selected_page.click_count + 1

        selected_page.save()

        return redirect(selected_page.url)

    def post(self, request):
        return redirect(reverse('rango:index'))

class RegisterProfileView(View):
    @method_decorator(login_required)
    def get(self, request):
        form = UserProfileForm()
        context_dict = {'form': form}
        return render(request, 'rango/profile_registration.html', context_dict)

    @method_decorator(login_required)
    def post(self, request):
        form = UserProfileForm(request.POST, request.FILES)

        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user  # Associate with the logged-in user
            user_profile.save()

            return redirect(reverse('rango:index'))  # Redirect to the home page (or another page)

        else:
            print(form.errors)  # Print form validation errors to the console for debugging

        context_dict = {'form': form}
        return render(request, 'rango/profile_registration.html', context_dict)


class ProfileView(View):
    def get_user_details(self, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        user_profile = UserProfile.objects.get_or_create(user=user)[0] 
        form = UserProfileForm(instance=user_profile)
        
        return (user, user_profile, form) 

    @method_decorator(login_required)
    def get(self, request, username):
        try:
            (user, user_profile, form) = self.get_user_details(username)
        except TypeError:
            return redirect(reverse('rango:index'))

        context_dict = {'user_profile': user_profile,
                        'selected_user': user, 
                        'form': form}

        return render(request, 'rango/profile.html', context_dict)

    @method_decorator(login_required)
    def post(self, request, username):
        try:
            (user, user_profile, form) = self.get_user_details(username)
        except TypeError:
            return redirect(reverse('rango:index'))

        # Populate form with new data
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)

        if form.is_valid(): 
            form.save(commit=True)
            return redirect(reverse('rango:profile', kwargs={'username': user.username}))  # Redirect to updated profile
        else:
            print(form.errors)  # Debugging output

        context_dict = {'user_profile': user_profile,
                        'selected_user': user, 
                        'form': form}

        return render(request, 'rango/profile.html', context_dict)




class ListProfilesView(View): 
    @method_decorator(login_required) 
    def get(self, request):
        profiles = UserProfile.objects.all()

        return render(request,
        'rango/list_profiles.html',
        {'user_profile_list': profiles})



class SearchAddPageView(View):
    @method_decorator(login_required)
    def get(self, request):
        category_id = request.GET['category_id']
        title = request.GET['title']
        url = request.GET['url']

        try:
            category = Category.objects.get(id=int(category_id))
        except Category.DoesNotExist:
            return HttpResponse('Error - category not found.')
        except ValueError:
            return HttpResponse('Error - bad category ID.')

        p = Page.objects.get_or_create(category=category, title=title, url=url)

        pages = Page.objects.filter(category=category).order_by('-views')
        return render(request, 'rango/page_listing.html', {'pages': pages})
    
class TrackURLView(View):
    def get(self, request, page_pk):
        print(f"Received page_pk: {page_pk}")  # Debugging to check the pk
        
        page = get_object_or_404(Page, pk=page_pk)  # Use pk instead of id
        page.views += 1  # Increment views
        page.save()  # Save changes

        return redirect(page.url) 