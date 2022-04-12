from pyexpat import model
from django import forms
from .models import Product, ProductGallery

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('product_name','description','price','images','stock','category')

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control col-lg-8'
            
class ProductGalleryForm(forms.ModelForm):
    class Meta:
        model= ProductGallery
        fields = ['product','image']
        