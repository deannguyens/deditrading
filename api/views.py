import requests
from django.shortcuts import render
from django.http import JsonResponse


def index(request):
    datapoints = [
        {"label": "Online Store", "y": 27},
        {"label": "Offline Store", "y": 25},
        {"label": "Discounted Sale", "y": 30},
        {"label": "B2B Channel", "y": 8},
        {"label": "Others", "y": 10}
    ]
    return render(request, 'index.html', {"datapoints": datapoints})


def cron_dedi(request):
    page = request.GET.get("page", 1)
    count = request.GET.get("count", 100)
    url = "https://cardano-mainnet.blockfrost.io/api/v0/assets/64f7b108bd43f4bde344b82587655eeb821256c0c8e79ad48db15d1844454449/addresses"
    url = "{}?page={}&count={}".format(url, page, count)
    headers = {"Project_id": "mainnetFbU0YNyHUewavE3TwqUNsVH5eI9Ra4pi"}
    response = requests.get(url, headers=headers)
    return JsonResponse({"results": response.json()})

