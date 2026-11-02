import socket
import select
import struct
import sys

in_packer = struct.Struct("4s i")

x = 0

server_addr = ("localhost", int(sys.argv[1]))


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
    print(f"Select storage server listening on {server_addr[1]}")

    try:
        while True:
            readables, writeables, exceptionals = select.select(inputs, [], [], 1.0)
            for s in readables:
                if s is sock:
                    client, client_addr = sock.accept()
                    print(f"Connected: {client_addr[0]}:{client_addr[1]}")
                    inputs.append(client)
                    continue

                msg = recv_exact(s, in_packer.size)
                if not msg:
                    try:
                        peer = s.getpeername()
                        print(f"Disconnected: {peer[0]}:{peer[1]}")
                    except OSError:
                        pass
                    inputs.remove(s)
                    s.close()
                    continue

                operation_raw, number = in_packer.unpack(msg)
                operation = operation_raw.decode("ascii", errors="replace").replace("\x00", "").strip().upper()

                match operation:
                    case "IN":
                        x = int(number)
                    case "INCR":
                        x += int(number)
                    case "DECR":
                        x -= int(number)
                    case _:
                        print(f"Unknown method: {operation_raw!r}")

                s.sendall(str(x).encode("ascii"))
    except KeyboardInterrupt:
        for s in inputs:
            if s is not sock:
                s.close()
        print("Server stopped")
