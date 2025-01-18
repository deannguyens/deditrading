from django.db import models
from django.db.models import Count, Sum


# Create your models here.

class AssetAddress(models.Model):
    payment_address = models.CharField(max_length=200)
    stake_address = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)


class AssetQuantityQuerySet(models.QuerySet):

    def total_quantity(self):
        asset_address = AssetAddress.objects.values("stake_address").annotate(count=Count("payment_address")).filter(count__gt=1).values_list("stake_address", flat=True)
        return self.filter(asset_address__stake_address__in=asset_address).aggregate(
            total=Sum("quantity")
        ).get("total", 0) + self.exclude(
            asset_address__stake_address__in=asset_address
            ).aggregate(total=Sum("quantity")).get("total", 0)

    
class AssetQuantity(models.Model):
    asset_address = models.ForeignKey(AssetAddress, on_delete=models.CASCADE, related_name='asset_quantity')
    quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = AssetQuantityQuerySet.as_manager()


class PageFlockFrost(models.Model):
    current = models.PositiveSmallIntegerField(default=1)