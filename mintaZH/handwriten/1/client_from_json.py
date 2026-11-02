import sys
import socket
import struct
import random
import json

packer = struct.Struct("20s i")

server_addr = (sys.argv[1], int(sys.argv[2]))

with open("input.json", "r") as f:
    data = json.load(f)

num = str(random.randint(1, 3))
data_row = data[num]
txt, number = data_row[0], data_row[1]
number = int(number)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect(server_addr)
    values = (txt.encode(), number)
    data = packer.pack(*values)
    client.sendall(data)
    rec_packer = struct.Struct(f"{number}s")
    data = client.recv(rec_packer.size)
    print(rec_packer.unpack(data))
