from ..travelmanager_api import TravelManagerAPI


class Relation:
    @staticmethod
    def get(station_id, date):
        params = {
            "station": station_id,
            "date": date,
        }
        return TravelManagerAPI.get("relations", params)
