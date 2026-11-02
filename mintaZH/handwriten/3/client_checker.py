import socket
import struct
import sys

tcp_out = struct.Struct("4s i")
udp_out = struct.Struct("5s i")
udp_in = struct.Struct("i")

udp_port = int(sys.argv[1])
tcp_port = int(sys.argv[2])

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sent = sock.sendto(udp_out.pack("PLUS".encode(), 0), ("localhost", udp_port))
    data, server = sock.recvfrom(udp_in.size)
    udp_val = int(udp_in.unpack(data)[0])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect(("localhost", tcp_port))
    values = ("IN".encode(), 0)
    data = tcp_out.pack(*values)
    client.sendall(data)
    data = client.recv(1024)
    tcp_val = int(data.decode())

if udp_val == tcp_val:
    print(f"\33[92mThe values are the same on the 2 server\33[0m")
else:
    print(f"\33[91mThe values are not the same on the 2 server\33[0m")
