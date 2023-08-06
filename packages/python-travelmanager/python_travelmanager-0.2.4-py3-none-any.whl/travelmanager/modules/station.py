from ..travelmanager_api import TravelManagerAPI


class Station:
    @staticmethod
    def get():
        return TravelManagerAPI.get("fetchstations")
