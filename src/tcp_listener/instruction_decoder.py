HALTING = 1
DISCOVERY = 2
RESPONSE = 3
ACK = 4
NODE_REQUEST = 5
WRONG_FORMAT = 6


class InstructionDecoder:
    def __init__(self, node):
        self._node = node

    def decode(self, instruction_type: int, data: dict):
        if instruction_type == HALTING:
            self._node.stop()
        elif instruction_type == DISCOVERY:
            pass
        elif instruction_type == RESPONSE:
            pass
        elif instruction_type == ACK:
            pass
        elif instruction_type == NODE_REQUEST:
            print(data)
            method = getattr(self._node, data['method'])
            return method(data['args'])
        else:
            pass
