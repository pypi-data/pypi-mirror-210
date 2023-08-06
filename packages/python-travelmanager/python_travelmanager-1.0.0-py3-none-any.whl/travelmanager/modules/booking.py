from datetime import date
from ..travelmanager_api import TravelManagerAPI


class Booking:
    @staticmethod
    def create(
        product: str,
        date: date,
        tickets: list,
        customer_name: str,
        phone: str,
        email: str,
        reference: str,
        remarks: str = "",
    ) -> dict:
        data = {
            "product": product,
            "date": date,
            "ticket": [ticket.__dict__ for ticket in tickets],
            "customer": customer_name,
            "phone": phone,
            "email": email,
            "booking_reference": reference,
            "remarks": remarks,
        }
        return TravelManagerAPI.post("booking", data=data)

    @staticmethod
    def delete(booking_id: str) -> dict:
        param = {
            "booking_reference": booking_id,
        }
        return TravelManagerAPI.get("cancel", param)
