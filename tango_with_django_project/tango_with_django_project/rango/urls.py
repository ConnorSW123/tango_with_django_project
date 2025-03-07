from django.urls import path
from rango import views

#CHAPTER 14/15 ADDITIONS - Adding Classes structure to Rango's Views
from rango.views import AboutView, IndexView, AddPageView, ShowCategoryView, GotoUrlView, RegisterProfileView, TrackURLView


app_name = 'rango'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    #Updated path that point to the new about class-based views.
    path('about/', AboutView.as_view(), name='about'),
    path('category/<category_name_slug>/', ShowCategoryView.as_view(), name='show_category'),
    path('add_category/', views.AddCategoryView.as_view(), name='add_category'),
    path('add_page/<category_name_slug>/', AddPageView.as_view(), name='add_page'),
    #path('register/', views.register, name='register'),
    #path('login/', views.user_login, name='login'),
    path('restricted/', views.restricted, name='restricted'),
    ##path('search/', views.search, name='search'),
    path('goto/', GotoUrlView.as_view(), name='goto'),
    path('accounts/register/', RegisterProfileView.as_view(), name='register'),
    #path('logout/', views.user_logout, name='logout')
    path('profile/<username>/', views.ProfileView.as_view(), name='profile'),
    path('profiles/', views.ListProfilesView.as_view(), name='list_profiles'),
    path('search_add_page/', views.SearchAddPageView.as_view(), name='search_add_page'),
    path('goto/<int:page_pk>/', TrackURLView.as_view(), name='track_url'),

    ]