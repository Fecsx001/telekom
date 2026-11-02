import socket
import sys
import struct

in_packer = struct.Struct("5s i")
out_packer = struct.Struct("i")

x = 0

server_addr = ("localhost", int(sys.argv[1]))
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.bind(server_addr)
    while True:
        data, client = sock.recvfrom(in_packer.size)
        method, number = in_packer.unpack(data)

        method = method.decode().replace("\x00", "").strip().upper()

        match method:
            case "PUSH":
                x = int(number)
            case "PLUS":
                x += int(number)
            case "MINUS":
                x -= int(number)
            case _:
                print(f"Unknown method: {method}")

        sock.sendto(out_packer.pack(x), client)
