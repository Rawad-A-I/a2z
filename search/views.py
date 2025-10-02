from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.paginator import Paginator
from django_elasticsearch_dsl import Q
from search.documents import ProductDocument, CategoryDocument
import json


class ProductSearchView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        category = request.GET.get('category', '')
        min_price = request.GET.get('min_price', '')
        max_price = request.GET.get('max_price', '')
        in_stock = request.GET.get('in_stock', '')
        featured = request.GET.get('featured', '')
        sort_by = request.GET.get('sort', 'relevance')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))

        # Build search query
        search = ProductDocument.search()

        # Text search
        if query:
            search = search.query(
                Q('multi_match', 
                  query=query,
                  fields=['product_name^3', 'product_description^2', 'category_name'],
                  fuzziness='AUTO')
            )

        # Filters
        filters = []
        
        if category:
            filters.append(Q('term', category_name=category))
        
        if min_price:
            filters.append(Q('range', price={'gte': float(min_price)}))
        
        if max_price:
            filters.append(Q('range', price={'lte': float(max_price)}))
        
        if in_stock == 'true':
            filters.append(Q('term', is_in_stock=True))
        
        if featured == 'true':
            filters.append(Q('term', is_featured=True))

        # Apply filters
        if filters:
            search = search.filter(Q('bool', must=filters))

        # Sorting
        if sort_by == 'price_asc':
            search = search.sort('price')
        elif sort_by == 'price_desc':
            search = search.sort('-price')
        elif sort_by == 'name':
            search = search.sort('product_name.raw')
        elif sort_by == 'newest':
            search = search.sort('-created_at')
        else:  # relevance
            pass  # Use default relevance scoring

        # Pagination
        start = (page - 1) * per_page
        search = search[start:start + per_page]

        # Execute search
        response = search.execute()

        # Format results
        results = []
        for hit in response:
            results.append({
                'uid': hit.uid,
                'product_name': hit.product_name,
                'slug': hit.slug,
                'price': hit.price,
                'category_name': hit.category_name,
                'is_in_stock': hit.is_in_stock,
                'is_featured': hit.is_featured,
                'is_bestseller': hit.is_bestseller,
                'is_new_arrival': hit.is_new_arrival,
                'score': hit.meta.score
            })

        # Get aggregations for faceted search
        aggregations = {}
        if hasattr(response, 'aggregations'):
            aggregations = response.aggregations.to_dict()

        return JsonResponse({
            'results': results,
            'total': response.hits.total.value if hasattr(response.hits.total, 'value') else response.hits.total,
            'page': page,
            'per_page': per_page,
            'aggregations': aggregations,
            'query': query
        })


class CategorySearchView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        
        search = CategoryDocument.search()
        
        if query:
            search = search.query(
                Q('match', category_name=query)
            )
        
        response = search.execute()
        
        results = []
        for hit in response:
            results.append({
                'uid': hit.uid,
                'category_name': hit.category_name,
                'slug': hit.slug,
                'product_count': hit.product_count
            })
        
        return JsonResponse({
            'results': results,
            'total': response.hits.total.value if hasattr(response.hits.total, 'value') else response.hits.total
        })


class SearchSuggestionsView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        limit = int(request.GET.get('limit', 5))
        
        if not query or len(query) < 2:
            return JsonResponse({'suggestions': []})
        
        # Search for product names that start with or contain the query
        search = ProductDocument.search()
        search = search.query(
            Q('prefix', product_name=query) | 
            Q('match_phrase_prefix', product_name=query)
        )
        search = search[:limit]
        
        response = search.execute()
        
        suggestions = []
        for hit in response:
            suggestions.append({
                'text': hit.product_name,
                'value': hit.product_name,
                'category': hit.category_name
            })
        
        return JsonResponse({'suggestions': suggestions})


@method_decorator(csrf_exempt, name='dispatch')
class AdvancedSearchView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Advanced search parameters
            query = data.get('query', '')
            filters = data.get('filters', {})
            sort = data.get('sort', {})
            pagination = data.get('pagination', {})
            
            # Build search
            search = ProductDocument.search()
            
            # Query
            if query:
                search = search.query(
                    Q('multi_match',
                      query=query,
                      fields=['product_name^3', 'product_description^2', 'category_name'],
                      type='best_fields',
                      fuzziness='AUTO')
                )
            
            # Filters
            must_filters = []
            
            if filters.get('categories'):
                must_filters.append(Q('terms', category_name=filters['categories']))
            
            if filters.get('price_range'):
                price_range = filters['price_range']
                if price_range.get('min'):
                    must_filters.append(Q('range', price={'gte': price_range['min']}))
                if price_range.get('max'):
                    must_filters.append(Q('range', price={'lte': price_range['max']}))
            
            if filters.get('in_stock'):
                must_filters.append(Q('term', is_in_stock=True))
            
            if filters.get('featured'):
                must_filters.append(Q('term', is_featured=True))
            
            if filters.get('bestsellers'):
                must_filters.append(Q('term', is_bestseller=True))
            
            if filters.get('new_arrivals'):
                must_filters.append(Q('term', is_new_arrival=True))
            
            # Apply filters
            if must_filters:
                search = search.filter(Q('bool', must=must_filters))
            
            # Sorting
            if sort.get('field') and sort.get('order'):
                field = sort['field']
                order = sort['order']
                if order == 'desc':
                    field = f'-{field}'
                search = search.sort(field)
            
            # Pagination
            page = pagination.get('page', 1)
            per_page = pagination.get('per_page', 20)
            start = (page - 1) * per_page
            search = search[start:start + per_page]
            
            # Execute search
            response = search.execute()
            
            # Format results
            results = []
            for hit in response:
                results.append({
                    'uid': hit.uid,
                    'product_name': hit.product_name,
                    'slug': hit.slug,
                    'price': hit.price,
                    'category_name': hit.category_name,
                    'is_in_stock': hit.is_in_stock,
                    'is_featured': hit.is_featured,
                    'is_bestseller': hit.is_bestseller,
                    'is_new_arrival': hit.is_new_arrival,
                    'score': hit.meta.score
                })
            
            return JsonResponse({
                'results': results,
                'total': response.hits.total.value if hasattr(response.hits.total, 'value') else response.hits.total,
                'page': page,
                'per_page': per_page,
                'query': query
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
