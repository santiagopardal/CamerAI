import src.api.api as API


def register(ip: str, port: int):
    response = API.post('node/', {"ip": ip, "port": port})
    return response.json()
