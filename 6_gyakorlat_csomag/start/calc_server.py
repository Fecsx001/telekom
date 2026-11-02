import select
import socket
import struct
import sys

packer = struct.Struct("i i c")  # ket szam es a muveleti jel
ops = {
    b"+": lambda a, b: a + b,
    b"-": lambda a, b: a - b,
    b"*": lambda a, b: a * b,
    b"/": lambda a, b: a // b,
}
server_addr = ("localhost", int(sys.argv[1]))  # pl. python calc_server.py 10000


def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            return b""
        data += chunk
    return data

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(server_addr)
    sock.listen(5)
    inputs = [sock]
    print(f"Select calc server listening on {server_addr[1]}")

    try:
        while True:
            readables, writeables, exceptionals = select.select(inputs, [], [], 1.0)
            for s in readables:
                if s is sock:
                    client, client_addr = sock.accept()
                    print(f"Connected: {client_addr[0]}:{client_addr[1]}")
                    inputs.append(client)
                    continue

                msg = recv_exact(s, packer.size)
                if not msg:
                    try:
                        peer = s.getpeername()
                        print(f"Disconnected: {peer[0]}:{peer[1]}")
                    except OSError:
                        pass
                    inputs.remove(s)
                    s.close()
                    continue

                a, b, op = packer.unpack(msg)
                result = ops[op](a, b)
                print(f"{a} {op.decode()} {b} = {result}")
                s.sendall(packer.pack(result, 0, b"R"))
    except KeyboardInterrupt:
        for s in inputs:
            if s is not sock:
                s.close()
        print("Server stopped")
