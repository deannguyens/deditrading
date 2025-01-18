from datetime import datetime

import requests
from asset_address.models import AssetAddress
from celery import shared_task


@shared_task()
def cron():
    # URL = "https://api.koios.rest/api/v1/asset_addresses?_asset_policy=64f7b108bd43f4bde344b82587655eeb821256c0c8e79ad48db15d18&_asset_name=44454449"
    check = True
    page = 1
    while check:
        print("start call api--------page--", page)

        url = "https://deditrading.vercel.app/api/index"
        url = "{}?page={}&count={}".format(url, page, 100)
        response = requests.get(url)
        if response.status_code != 200:
            print("_____error___________", response.text, page)
            continue
        results = response.json()
        results = results.get("results")

        if len(results) == 0:
            check = False
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
        page += 1


def background_process():
    print("start a---------background_process----------------------------")
    cron.delay()
    