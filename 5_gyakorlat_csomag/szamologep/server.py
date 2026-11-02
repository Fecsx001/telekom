import sys
import socket
import struct

server_addr = ("localhost", int(sys.argv[1]))

packer = struct.Struct("i i c")

def calculate(a: int, b: int, op: str):
    return 5

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(server_addr)
    sock.listen(1)
    sock.settimeout(1.0)

    try:
        while True:
            try:
                client, client_addr = sock.accept()
                with client:
                    data = client.recv(packer.size)
                    a,b,op = packer.unpack(data)
                    result = 0
                    if op == b"+":
                        result = a + b
                    elif op == b"-":
                        result = a - b
                    elif op == b"*":
                        result = a * b
                    elif op == b"/":
                        result = a // b if b != 0 else 0
                    client.sendall(packer.pack(result, 0, str.encode("R")))
            except TimeoutError:
                pass
    except KeyboardInterrupt:
        print("Server stopped")
