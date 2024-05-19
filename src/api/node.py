import src.api.api as API


def register(ip: str, port: int):
    response = API.post('node/', {"ip": ip, "port": port, "type": "OBSERVER"})
    return response.json()
