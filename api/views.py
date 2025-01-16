from datetime import datetime
import requests
from django.http import HttpResponse
from django.http import JsonResponse
from asset_address.task import cron


def index(request):
    now = datetime.now()
    html = f'''
    <html>
        <body>
            <h1>Hello from Vercel!</h1>
            <p>The current time is { now }.</p>
            <a href="/write-file">Write File</a>
        </body>
    </html>
    '''
    url = "https://cardano-mainnet.blockfrost.io/api/v0/assets/64f7b108bd43f4bde344b82587655eeb821256c0c8e79ad48db15d1844454449/addresses"
    url = "{}?page={}".format(url, 1)

    headers = {"Project_id": "mainnetFbU0YNyHUewavE3TwqUNsVH5eI9Ra4pi"}
    print("start request---")
    response = requests.get(url, headers=headers)
    results = response.json()
    return JsonResponse({"data": results})
    # return HttpResponse(html)


def cron_dedi(request):
    # cron()
    return HttpResponse("OK")