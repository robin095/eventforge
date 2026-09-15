import threading

import requests

URL = "http://127.0.0.1:8000/reservations"

payload = {
    "user_id": 1,
    "event_id": 1,
    "seat_id": 1
}


def make_request():
    response = requests.post(URL, json=payload)
    print(response.status_code, response.text)


thread1 = threading.Thread(target=make_request)
thread2 = threading.Thread(target=make_request)

thread1.start()
thread2.start()

thread1.join()
thread2.join()