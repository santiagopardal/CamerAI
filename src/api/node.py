import src.api.api as API


async def register(ip: str, port: int):
    return (await API.post('node/', {"ip": ip, "port": port})).json()
