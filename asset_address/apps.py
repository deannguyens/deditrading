from django.apps import AppConfig
from threading import Timer


class AssetAddressConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'asset_address'


    def ready(self):
        try:
            import asset_address.task
        except ImportError:
            pass

    # def ready(self):
    #     print("start-------1")
    #     import threading
    #     t = threading.Thread(target=background_process, args=(), kwargs={})
    #     t.setDaemon(True)
    #     t.start()
    #     print("sart___2__")


# def background_process():
#     print("start a---------background_process----------------------------")
#     Timer(3, background_process).start()