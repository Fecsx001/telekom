import socket
import struct

TCP_ADDR = ("127.0.0.1", 9103)
UDP_ADDR = ("127.0.0.1", 9102)
TCP_REQ = struct.Struct("4s i")
UDP_REQ = struct.Struct("5s i")


def query_tcp(value: int = 0):
    payload = TCP_REQ.pack(b"INCR", value)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(TCP_ADDR)
        sock.sendall(payload)
        data = sock.recv(1024)
    return int(data.decode("ascii"))


def query_udp(value: int = 0):
    payload = UDP_REQ.pack(b"PLUS ", value)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(payload, UDP_ADDR)
        data, _ = sock.recvfrom(1024)
    return struct.unpack("i", data)[0]


def main():
    tcp_value = query_tcp(0)
    udp_value = query_udp(0)
    print(f"TCP value: {tcp_value}")
    print(f"UDP value: {udp_value}")

    if tcp_value == udp_value:
        print("UDP szerver helyes: a random drift nincs látszólag hatással.")
    else:
        print("UDP szerver hibázott: az értékek különböznek.")


if __name__ == "__main__":
    main()
