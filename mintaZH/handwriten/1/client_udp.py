import sys
import socket
import struct

ADDR = (sys.argv[1], int(sys.argv[2]))

packer = struct.Struct("20s i")

print(sys.argv)


def msg():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sent = sock.sendto(packer.pack(sys.argv[3].encode(), int(sys.argv[4])), ADDR)
        data, server = sock.recvfrom(1024)
        print(f"Response from {server}: {data!r}")


if __name__ == "__main__":
    msg()
