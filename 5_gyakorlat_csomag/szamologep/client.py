import sys
import socket
import struct

packer = struct.Struct("i i c")

server_addr = (sys.argv[1], int(sys.argv[2]))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect(server_addr)
    values = (int(sys.argv[3]), int(sys.argv[5]), sys.argv[4].encode())
    data = packer.pack(*values)
    client.sendall(data)
    data = client.recv(packer.size)
    print(packer.unpack(data)[0])