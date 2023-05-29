import vk_api
import requests
import re
from datetime import datetime
import statistics as st
import pandas as pd

access_token = "vk1.a._DaUOaPDsrAYJlj3dTqQQsVJKyxRwSW8KsXMn5ZzWWJctj5xrVJmwXm-Same__ieQo9UMfyywrPZkNbJU26QJerkwDp7zlEpGGtkJSucyawAk8b7P1oTT7mqcxKpNfdDOViJ8qN8a15Tr6awljGO3US86YMSIq57e9azozHWL0mjHKHn1zI9CGZ0k4LmjenwCOWzuGqfe3BaMoIplCNxEw"
session = vk_api.VkApi(token=access_token)

url = "id29097433"
user_id = None
screen_name = url.replace("https://vk.com/", "").strip()

try:
    user_id = int(screen_name)
except ValueError:
    if screen_name[:1] == "id":
        try:
            user_id = int(screen_name[1:])
        except ValueError:
            pass
    if user_id is None:
        user_id = int(session.method("utils.resolveScreenName", {"screen_name": screen_name})["object_id"])

print(user_id)
