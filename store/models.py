
from random import choices
from django.db import models
from django.urls import reverse

from django.core.validators import MinValueValidator, MaxValueValidator

from category.models import Category


# Create your models here.


class Product(models.Model):
    product_name        = models.CharField(max_length=200,unique=True)
    slug                = models.SlugField(max_length=200,unique=True)
    description         = models.TextField(null=True,blank=True)
    price               = models.DecimalField(max_digits=10, decimal_places=2)
    images              = models.ImageField(upload_to='photos/products', default='default_product1.png')
    stock               = models.IntegerField()
    is_available        = models.BooleanField(default=True)
    category            = models.ForeignKey(Category,on_delete=models.CASCADE)
    discount_type       = models.CharField(max_length=50, null=True,blank=True)
    discount_percentage = models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(100)], null=True,blank=True)
    mrp_price           = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    created_date        = models.DateTimeField(auto_now_add=True)
    modified_date      = models.DateTimeField(auto_now=True)


    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])


    def __str__(self):
        return self.product_name






class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    images = models.ImageField(upload_to = "store/products",max_length=255)
    

    def __str__(self):
        return self.product.product_name


    class Meta:
        verbose_name = 'product_gallery'
        verbose_name_plural = 'product_gallery'

