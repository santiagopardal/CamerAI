from src.node import Node
import asyncio
import logging


logging.basicConfig(
    filename='camerai.log',
    filemode='a',
    level=logging.INFO,
    format="{asctime} {levelname:<8} {message}",
    style="{"
)


sys = Node()
asyncio.run(sys.run())
