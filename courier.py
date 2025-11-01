# courier.py
import time

def book_shipment(invoice, recipient_name, phone, address, cod_amount):
    print(f"INFO:courier:Booking shipment for order {invoice}")
    time.sleep(0.5)
    return {
        "tracking_code": f"TRK-MOCK-{invoice}",
        "status": "Booked"
    }