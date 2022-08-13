import src.api.api as API


def register(ip: str, port: int):
    return API.post('node/', {"ip": ip, "port": port}).json()
