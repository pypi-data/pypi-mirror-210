import requests
import logging


logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


class TravelManagerAPI:
    @classmethod
    def connect(cls, url, portal_id, token):
        cls.api_url = f"https://{url}/q"
        cls.portal_id = portal_id
        cls.token = token
        cls.basic_params = {
            "portal": TravelManagerAPI.portal_id,
            "token": TravelManagerAPI.token,
        }

    @staticmethod
    def get(endpoint, params={}):
        params = (
            TravelManagerAPI.basic_params
            | params
            | {
                "call": endpoint,
            }
        )
        print(params)

        # set log level to debug
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

        return requests.get(
            TravelManagerAPI.api_url, params=params, timeout=5
        ).json()

    @staticmethod
    def post(endpoint, params={}, data={}):
        params = (
            TravelManagerAPI.basic_params
            | params
            | {
                "call": endpoint,
            }
        )

        # set log level to debug
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

        return requests.post(
            TravelManagerAPI.api_url, json=data, params=params, timeout=5
        ).json()


# URL = peters-test.travelmanager.software
# portal=1000572&
# token=e017243b9113ca6d81ed3e9c03defb56357d2693549441cf1a6e8ab4ac62d284
