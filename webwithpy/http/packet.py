class DefaultPacket:
    def __init__(self, request: str):
        ...


class UserPacket:
    ...

class JsonPacket: ...


class PacketHandler:
    def get_packet(self, request: str):

