from django.db import models

# Create your models here.

class AssetAddress(models.Model):
    payment_address = models.CharField(max_length=200)
    stake_address = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
class AssetQuantity(models.Model):
    asset_address = models.ForeignKey(AssetAddress, on_delete=models.CASCADE, related_name='asset_quantity')
    quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class PageFlockFrost(models.Model):
    current = models.PositiveSmallIntegerField(default=1)