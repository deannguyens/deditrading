from datetime import datetime

import requests

from asset_address.models import AssetAddress, AssetQuantity

def cron():


    # URL = "https://api.koios.rest/api/v1/asset_addresses?_asset_policy=64f7b108bd43f4bde344b82587655eeb821256c0c8e79ad48db15d18&_asset_name=44454449"
    check = True
    page = 1
    while check:
        print("start call api----------")
        url = "https://cardano-mainnet.blockfrost.io/api/v0/assets/64f7b108bd43f4bde344b82587655eeb821256c0c8e79ad48db15d1844454449/addresses"
        url = "{}?page={}".format(url, page)

        headers = {"Project_id": "mainnetFbU0YNyHUewavE3TwqUNsVH5eI9Ra4pi"}

        response = requests.get(url, headers=headers)
        print("start_______________", response.status_code)
        results = response.json()

        if len(results) == 0:
            check = False
        else:
            for result in results:
                asset_address, created = AssetAddress.objects.get_or_create(
                    payment_address=result['address'],
                )
                quantity = int(result['quantity']) / 1000000
                print(result, quantity)
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
            page+=1

    