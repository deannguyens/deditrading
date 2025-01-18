import requests
from django.conf import settings
from django.db.models import Count
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from enum import Enum
from dataclasses import dataclass
from django.utils import timezone
from asset_address.models import AssetQuantity, AssetAddress
from asset_address.task import run_5seconds
from pathlib import Path
import json

@dataclass
class Asset:
    display: str
    text: str
    value: int
    key_from: str
    value_from: int
    value_to: int = 0
    key_to: str = None
    href=None


class Season(Enum):
    DIGITAL_CAPTAIN = 20*1000
    SYSTEM_GENERAL = 100*1000
    GPU_COMMANDER = 200*1000
    GPU_ADMIRAL = 1000*1000

carts = [
    Asset(
        display="Digital Captain",
        text="(1 -> 20k)",
        value=0,
        key_from="quantity__gt",
        value_from=1,
        key_to="quantity__lte",
        value_to=Season.DIGITAL_CAPTAIN.value
    ),
    Asset(
        display="System General",
        text="(20,001 -> 100K)",
        value=0,
        key_from="quantity__gt",
        value_from=Season.DIGITAL_CAPTAIN.value,
        key_to="quantity__lte",
        value_to=Season.SYSTEM_GENERAL.value
    ),
    Asset(
        display="GPU Commander",
        text="(100,001 - 200k)",
        value=0,
        key_from="quantity__gt",
        value_from=Season.SYSTEM_GENERAL.value,
        key_to="quantity__lte",
        value_to=Season.GPU_COMMANDER.value
    ),
    Asset(
        display="GPU Admiral",
        text="(200,001 - > 1M)",
        value=0,
        key_from="quantity__gt",
        value_from=Season.GPU_COMMANDER.value,
        key_to="quantity__lte",
        value_to=Season.GPU_ADMIRAL.value
    ),
    Asset(
        display="GPU Whale",
        text="(> 1M)",
        value=0,
        key_from="quantity__gt",
        value_from=Season.GPU_ADMIRAL.value,
    )
]


def index(request):
    now = timezone.now()
    asset_address = AssetAddress.objects.values("stake_address").annotate(count=Count("payment_address")).filter(
        count__gt=1).values_list("stake_address", flat=True)
    assets_quantity = AssetQuantity.objects.exclude(
        asset_address__stake_address__in=asset_address
    ).filter(created_at__year=now.year, created_at__month=now.month, created_at__day=now.day)

    assets_quantity_many_wallet = AssetQuantity.objects.filter(
        asset_address__stake_address__in=asset_address
    ).filter(created_at__year=now.year, created_at__month=now.month, created_at__day=now.day)

    datapoints = [
        {
            "label": "Digital Captain",
            "y": assets_quantity.filter(
                quantity__lte=Season.DIGITAL_CAPTAIN.value
            ).count() + assets_quantity_many_wallet.filter(
                quantity__lte=Season.DIGITAL_CAPTAIN.value
            ).count()
        },
        {
            "label": "System General",
            "y": assets_quantity.filter(
                quantity__gt=Season.DIGITAL_CAPTAIN.value,
                quantity__lte=Season.SYSTEM_GENERAL.value
            ).count() + assets_quantity_many_wallet.filter(
                quantity__gt=Season.DIGITAL_CAPTAIN.value,
                quantity__lte=Season.SYSTEM_GENERAL.value
            ).count()
        },
        {
            "label": "GPU Commander",
            "y": assets_quantity.filter(
                quantity__gt=Season.SYSTEM_GENERAL.value,
                quantity__lte=Season.GPU_COMMANDER.value
            ).count() + assets_quantity_many_wallet.filter(
                quantity__gt=Season.SYSTEM_GENERAL.value,
                quantity__lte=Season.GPU_COMMANDER.value
            ).count()
        },
        {
            "label": "GPU Admiral",
            "y": assets_quantity.filter(
                quantity__gt=Season.GPU_COMMANDER.value,
                quantity__lte=Season.GPU_ADMIRAL.value
            ).count() + assets_quantity_many_wallet.filter(
                quantity__gt=Season.GPU_COMMANDER.value,
                quantity__lte=Season.GPU_ADMIRAL.value
            ).count()
        },
        {
            "label": "GPU Whale",
            "y": assets_quantity.filter(
                quantity__gt=Season.GPU_ADMIRAL.value,
            ).count() + assets_quantity_many_wallet.filter(
                quantity__gt=Season.GPU_ADMIRAL.value,
            ).count()
        },
    ]

    



    stepcount = [
        {"y": 10560, "label": "Sunday"},
        {"y": 9060, "label": "Monday"},
        {"y": 6650, "label": "Tuesday"},
        {"y": 8305, "label": "Wednesday"},
        {"y": 8531, "label": "Thursday"},
        {"y": 10150, "label": "Friday"},
        {"y": 8921, "label": "Saturday"}
    ]
    return render(request, 'index.html', {"datapoints": datapoints, "stepcount": stepcount})


from django import forms

class SearchForm(forms.Form):
    query = forms.CharField(label='Search userId', max_length=100, initial="Text search")


def list_table(request):
    form = SearchForm(request.POST)
    now = timezone.now()
    queryset = AssetQuantity.objects.filter(
        created_at__year=now.year, created_at__month=now.month, created_at__day=now.day,
        quantity__gt=1
    ).order_by("-quantity")

    for item in carts:
        href = "/check-quantity?"
        if item.key_to:
            dt = {
                item.key_from: item.value_from,
                item.key_to: item.value_to
            }
            href = "{}{}={}&{}={}".format(href, item.key_from, item.value_from, item.key_to, item.value_to)
        else:
            dt = {item.key_from: item.value_from}
            href = "{}{}={}".format(href, item.key_from, item.value_from)
        item.value = queryset.filter(**dt).count()
        item.href = href
    json_object = return_json_object()

    return render(request, 'list-table.html', {"carts": carts, 'form': form, "json_object": json_object})


def return_json_object():
    # Opening JSON file
    now = timezone.now()

    check = True
    json_object = {}
    while check:
        name_file = now.strftime("%d_%m_%Y")
        if Path("{}/{}.json".format(settings.MEDIA_ROOT, name_file)).exists():
            with open("{}/{}.json".format(settings.MEDIA_ROOT, name_file), 'r') as openfile:
                json_object = json.load(openfile)
                break
        else:
            now = now - timezone.timedelta(days=1)
    return json_object


def check_quantity(request):
    now = timezone.now()
    json_object = return_json_object()
    results = json_object.get("results", [])
    params = dict(zip(request.GET.keys(), request.GET.values()))
    quantity__gte = params.get("quantity__gte")
    quantity__lte = params.get("quantity__lte")
    if not quantity__lte:
        results = list(filter(lambda x: int(x.get("quantity")) > int(quantity__gte), results))
    elif quantity__lte and quantity__gte:
        results = list(filter(lambda x: int(x.get("quantity")) > int(quantity__gte) and int(x.get("quantity")) <= int(quantity__lte), results))
    else:
        results = list(filter(lambda x: int(x.get("quantity")) >= int(quantity__gte), results))
    return render(request, 'check-quantity.html', {"results": results})
    # queryset = AssetQuantity.objects.filter(
    #     created_at__year=now.year, created_at__month=now.month, created_at__day=now.day,
    #     quantity__gt=0
    # ).order_by("-quantity")
    # if queryset:
    #     queryset = queryset.filter(**dict(zip(request.GET.keys(), request.GET.values()))).order_by("-quantity")
    # return render(request, 'check-quantity.html', {"results": queryset})


def cron_dedi(request):
    page = request.GET.get("page", 1)
    count = request.GET.get("count", 100)
    url = "https://cardano-mainnet.blockfrost.io/api/v0/assets/64f7b108bd43f4bde344b82587655eeb821256c0c8e79ad48db15d1844454449/addresses"
    url = "{}?page={}&count={}".format(url, page, count)
    headers = {"Project_id": "mainnetFbU0YNyHUewavE3TwqUNsVH5eI9Ra4pi"}
    response = requests.get(url, headers=headers)
    return JsonResponse({"results": response.json()})


def specific_address(request):
    address = request.GET.get("address")
    url = "https://cardano-mainnet.blockfrost.io/api/v0/addresses/{}".format(address)
    headers = {"Project_id": "mainnetFbU0YNyHUewavE3TwqUNsVH5eI9Ra4pi"}
    response = requests.get(url, headers=headers)
    return JsonResponse({"result": response.json()})

def task_test(request):
    print("start a---------task_test----------------------------")
    run_5seconds.delay()
    return HttpResponse("done")