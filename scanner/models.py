from django.db import models

class Product(models.Model):
    barcode = models.CharField(max_length=13, unique=True)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=200, null=True, blank=True)
    brand = models.CharField(max_length=200, null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)
    recycling_type = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name or "Produit inconnu"

