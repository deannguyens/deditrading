from datetime import datetime
import celery
import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from asset_address.models import AssetAddress, AssetQuantity
from celery import shared_task



@shared_task()
def cron_end(from_page, only_page=True):
    URL_SPECIFIC_ADDRESS = "https://deditrading.vercel.app/api/specific-address?address={}"
    check = True
    page = from_page
    while check:
        print("start call api--------page--", page)
        url = "https://deditrading.vercel.app/api/index?page={}&count={}".format(page, 100)
        response = requests.get(url)
        if response.status_code != 200:
            continue
        results = response.json()
        results = results.get("results")

        if len(results) == 0:
            check = False
            print("FINISH--------page--", page)
        else:
            for index, result in enumerate(results, 1):
                if index == len(results):
                    print("end call per api--------page--", page)
                if int(result.get("quantity")) < 100000:
                    continue
                address = result['address']
                response_wa = requests.get(URL_SPECIFIC_ADDRESS.format(address))
                response_wa = response_wa.json()
                stake_address = None
                if response_wa.get("result"):
                    result_wa = response_wa.get("result")
                    stake_address = result_wa.get("stake_address")
                quantity = int(result['quantity']) / 1000000
                if quantity > 0:
                    if stake_address:
                        asset_address, created = AssetAddress.objects.get_or_create(stake_address=stake_address)
                        if created:
                            asset_address.payment_address = address
                            asset_address.save(update_fields=['payment_address'])
                    else:
                        asset_address, created = AssetAddress.objects.get_or_create(
                            payment_address=address
                        )
                    if asset_address.asset_quantity.filter(
                            created_at__year=datetime.now().year,
                            created_at__month=datetime.now().month,
                            created_at__day=datetime.now().day
                    ).exists():
                        asset_address.asset_quantity.filter(
                            created_at__year=datetime.now().year,
                            created_at__month=datetime.now().month,
                            created_at__day=datetime.now().day
                        ).update(quantity=quantity)
                    else:
                        asset_address.asset_quantity.create(quantity=quantity)
        if only_page:
            check = False
        else:
            page += 1

def background_process():
    print("start a---------background_process----------------------------")
    services_tasks = []
    for i in range(1, 21):
        services_tasks.append(cron_end.s(i))
    services_tasks.append(cron_end.s(21, False))
    transaction.on_commit(lambda: celery.group(services_tasks).apply_async())


@shared_task()
def run_5seconds():
    import time
    print("start a---------run_5seconds----------------------------")
    for i in range(5):
        print("run after: ", i)
        time.sleep(1)

def create_file_json():
    from django.core import serializers
    now = timezone.now()
    name_file = now.strftime("%d_%m_%Y")
    print("__name__", name_file)
    import json

    # Data to be written
    queryset = AssetQuantity.objects.filter(
        created_at__year=now.year, created_at__month=now.month, created_at__day=now.day,
        quantity__gt=1
    ).order_by("-quantity").values(
        "id",
        "quantity",
        "asset_address__payment_address",
        "asset_address__stake_address",
    )
    # data  = serializers.serialize('json', queryset)
    # print("data:  ", queryset)
    # dictionary = {
    #     "name": "sathiyajith",
    #     "rollno": 56,
    #     "cgpa": 8.6,
    #     "phonenumber": "9976770500"
    # }
    # print("data:  ", data)

    # Serializing json
    # print("queryset:  ", queryset)
    data = {
        "results": list(queryset),
        "created_at": now.strftime("%d-%m-%Y %H:%M:%S"),
    }
    json_object = json.dumps(data, indent=2)

    # Writing to sample.json
    with open("{}/{}.json".format(settings.MEDIA_ROOT,name_file), "w") as outfile:
        outfile.write(json_object)