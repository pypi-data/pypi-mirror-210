import requests
import pandas as pd
from .logger import Logger

def predict(endpoint_url,content_type,data):
    logger = Logger.get_instance()
    try:
        response = requests.post(endpoint_url, headers={"Content-Type":content_type}, data=data)

        if response.status_code==200:
            return response.json()
        elif response.status_code==413:
            raise Exception("Inference data passed is too large. This might be due to mlflow docker image's nginx configuration limiting inferencing data size to 5 MiB.",response.text)
        else:
            raise Exception("Inferencing endpoint failed.",response.text)
    except Exception as e:
        logger.error(e)
        raise