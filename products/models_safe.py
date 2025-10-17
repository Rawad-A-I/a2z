"""
Safe version of models for deployment without image optimization fields
This can be used temporarily if migration issues persist
"""

from django.db import models
from django.utils.text import slugify
import uuid


class BaseModel(models.Model):
    uid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(BaseModel):
    category_name = models.CharField(max_length=100)
    category_image = models.ImageField(
        upload_to="catgories",
        help_text="Upload any image format. Will be automatically optimized for web use."
    )
    slug = models.SlugField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.category_name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.category_name


class ProductImage(BaseModel):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name="product_images")
    image = models.ImageField(
        upload_to="product",
        help_text="Upload any image format. Will be automatically optimized for web use."
    )
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['sort_order', 'created_at']
    
    def __str__(self):
        return f"{self.product.product_name} - Image {self.sort_order}"


