import sys
import socket
import struct
import random

packer = struct.Struct("20s i")

server_addr = (sys.argv[1], int(sys.argv[2]))

with open("input.txt", "r") as f:
    data = f.read().strip().split("\n")

num = random.randint(1, 3)
data_row = data[num - 1]
txt, number = data_row.split(" ")
number = int(number)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect(server_addr)
    values = (txt.encode(), number)
    data = packer.pack(*values)
    client.sendall(data)
    rec_packer = struct.Struct(f"{number}s")
    data = client.recv(rec_packer.size)
    print(rec_packer.unpack(data))
