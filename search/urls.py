from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.ProductSearchView.as_view(), name='product_search'),
    path('categories/', views.CategorySearchView.as_view(), name='category_search'),
    path('suggestions/', views.SearchSuggestionsView.as_view(), name='search_suggestions'),
    path('advanced/', views.AdvancedSearchView.as_view(), name='advanced_search'),
]
