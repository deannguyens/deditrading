from datetime import datetime

import requests
from django.contrib.auth import get_user_model
from threading import Timer
from asset_address.models import AssetAddress, PageFlockFrost
from celery import shared_task


# @shared_task()
def cron():
    # URL = "https://api.koios.rest/api/v1/asset_addresses?_asset_policy=64f7b108bd43f4bde344b82587655eeb821256c0c8e79ad48db15d18&_asset_name=44454449"
    page: PageFlockFrost = PageFlockFrost.objects.first()
    print("start call api--------page--", page)

    url = "https://cardano-mainnet.blockfrost.io/api/v0/assets/64f7b108bd43f4bde344b82587655eeb821256c0c8e79ad48db15d1844454449/addresses"
    url = "{}?page={}&count={}".format(url, page.current, 60)

    headers = {"Project_id": "mainnetFbU0YNyHUewavE3TwqUNsVH5eI9Ra4pi"}

    response = requests.get(url, headers=headers)
    results = response.json()
    print("test______", response.status_code)

    if len(results) == 0:
        page.current = 1
        page.save()
    else:
        for result in results:
            if int(result.get("quantity")) < 100000:
                continue
            asset_address, created = AssetAddress.objects.get_or_create(
                payment_address=result['address'],
            )
            print("lop__________------___", result)
            quantity = int(result['quantity']) / 1000000
            if quantity > 0:
                if asset_address.asset_quantity.filter(
                        created_at__year=datetime.now().year,
                        created_at__month=datetime.now().month,
                        created_at__day=datetime.now().day
                ).exists():
                    continue
                asset_address.asset_quantity.create(
                    quantity=quantity,
                )
        page.current = page.current + 1
        page.save()



    