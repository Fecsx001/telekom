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
server_addr = ("", int(sys.argv[1]))  # pl. python calc_server.py 10000

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.bind(server_addr)
    while True:
        data, client = sock.recvfrom(1024)
        a, b, op = packer.unpack(data)
        result = ops[op](a, b)
        print(f"{a} {op.decode()} {b} = {result}")
        sock.sendto(packer.pack(result, 0, b"R"), client)
