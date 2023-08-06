from ..travelmanager_api import TravelManagerAPI


class Availability:
    @staticmethod
    def get(product, start_date, stop_date):
        params = {
            "product": product,
            "start": start_date,
            "stop": stop_date,
        }
        return TravelManagerAPI.get("availability", params)
