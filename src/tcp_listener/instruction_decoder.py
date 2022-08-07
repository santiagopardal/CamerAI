DISCOVERY = 1
RESPONSE = 2
ACK = 3
NODE_REQUEST = 4
WRONG_FORMAT = 5


class InstructionDecoder:
    def __init__(self, node):
        self._node = node

    def decode(self, instruction_type: int, data: dict):
        if instruction_type == DISCOVERY:
            pass
        elif instruction_type == RESPONSE:
            pass
        elif instruction_type == ACK:
            pass
        elif instruction_type == NODE_REQUEST:
            method = getattr(self._node, data['method'])
            if 'args' in data:
                return method(data['args'])
            else:
                method()
        else:
            pass
