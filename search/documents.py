from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from products.models import Product, Category


@registry.register_document
class ProductDocument(Document):
    category = fields.ObjectField(properties={
        'category_name': fields.TextField(),
        'slug': fields.TextField(),
    })
    
    # Searchable fields
    product_name = fields.TextField(
        analyzer='standard',
        fields={'raw': fields.KeywordField()}
    )
    product_description = fields.TextField(analyzer='standard')
    
    # Faceted fields
    category_name = fields.TextField(fielddata=True)
    
    class Index:
        name = 'products'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'analysis': {
                'analyzer': {
                    'custom_analyzer': {
                        'type': 'custom',
                        'tokenizer': 'standard',
                        'filter': ['lowercase', 'stop', 'snowball']
                    }
                }
            }
        }

    class Django:
        model = Product
        fields = [
            'uid',
            'slug',
            'price',
            'stock_quantity',
            'is_in_stock',
            'is_featured',
            'is_bestseller',
            'is_new_arrival',
            'weight',
            'dimensions',
            'created_at',
            'updated_at',
        ]
        related_models = [Category]

    def prepare_category(self, instance):
        if instance.category:
            return {
                'category_name': instance.category.category_name,
                'slug': instance.category.slug,
            }
        return {}

    def prepare_product_description(self, instance):
        return instance.product_desription

    def prepare_category_name(self, instance):
        if instance.category:
            return instance.category.category_name
        return ""


@registry.register_document
class CategoryDocument(Document):
    category_name = fields.TextField(
        analyzer='standard',
        fields={'raw': fields.KeywordField()}
    )
    product_count = fields.IntegerField()

    class Index:
        name = 'categories'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = Category
        fields = [
            'uid',
            'slug',
            'created_at',
            'updated_at',
        ]

    def prepare_product_count(self, instance):
        return instance.products.count()
