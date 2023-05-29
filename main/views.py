from django.shortcuts import render
from django.views.generic.base import View
from static.python.methods import UserInformation
from django.apps import apps
import numpy as np
from joblib import load
from django.conf import settings


files = apps.get_model('main', 'ModelFile').objects.filter(draft=False)
access_token = "vk1.a.UAACp7RAdImZvjIw9GOoDJB6anF_TNspgPdvqvYHdwAHkzJ1IHtOT3Q2xlEA0kHuDbYskLtJUdoj-MaR9bj9LR8GYOMySWs62_mjw3gg3kl-aNRRrJ4JoYIb6L--MzxZmAMPmarlw8zSwmfr5xYvbXT0K3_NOqenfTCBB9-rCFOYKNtUeWxeB6YqmISaQPGfl5dfrj4wrsGbUkTvzoaCjg"


class MainView(View):
    def get(self, request):
        return render(request, "main/base.html")

    def post(self, request):
        info = UserInformation(request.POST["user"], access_token)
        user_info = info.collect_info()
        result = "Бот"
        if user_info["message"] == "success":
            predictions = []
            for file in files:
                model = load(settings.MEDIA_ROOT + f"/models/{file.get_filename()}")
                try:
                    prediction = model.predict(user_info["features"])[0]
                except:
                    prediction = None
                predictions.append(prediction)
            if len(predictions) > 0:
                if round(float(np.mean(predictions)), 0) == 1:
                    result = "Не бот"

        return render(request, "main/info.html", {
            "user_id": info.user_id,
            "name": user_info["name"],
            "photo": user_info["photo"],
            # "features": user_info["features"],
            "prediction": result,
            "message": user_info["message"]
        })
