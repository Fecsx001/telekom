import sys
import socket
import struct
import random

packer = struct.Struct("20s i")

server_addr = (sys.argv[1], int(sys.argv[2]))

txt = sys.argv[3]
number = random.randint(0, len(txt))
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect(server_addr)
    values = (txt.encode(), number)
    data = packer.pack(*values)
    client.sendall(data)
    rec_packer = struct.Struct(f"{number}s")
    data = client.recv(rec_packer.size)
    print(rec_packer.unpack(data))
