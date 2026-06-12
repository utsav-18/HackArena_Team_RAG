import os
import requests
from dotenv import load_dotenv

load_dotenv()

NODEMCU_IP = os.getenv(
    "NODEMCU_IP"
)


def activate_corridor():

    try:

        requests.get(
            f"http://{NODEMCU_IP}/emergency",
            timeout=3
        )

        return True

    except:

        return False
def normal_mode():

    try:

        requests.get(
            f"http://{NODEMCU_IP}/normal",
            timeout=3
        )

        return True

    except:

        return False