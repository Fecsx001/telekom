import argparse
import socket
import struct

TCP_PACK = struct.Struct("4s i")
UDP_PACK = struct.Struct("5s i")

UDP_SERVER = ("127.0.0.1", 9102)
COMMAND_MAP = {
    "IN": "PUSH",
    "INCR": "PLUS",
    "DECR": "MINUS",
}


def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            return b""
        data += chunk
    return data


def encode_udp_command(name: str) -> bytes:
    return name.encode("ascii").ljust(5, b" ")[:5]


def run_proxy(host: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(10)
        print(f"[Proxy] listening on {host}:{port}")
        while True:
            client, addr = server.accept()
            with client:
                print(f"[Proxy] connected: {addr}")
                data = recv_exact(client, TCP_PACK.size)
                if not data:
                    continue
                cmd_raw, value = TCP_PACK.unpack(data)
                cmd = cmd_raw.decode("ascii", errors="replace").strip().upper()
                if cmd not in COMMAND_MAP:
                    client.sendall(b"ERROR")
                    continue

                udp_cmd = COMMAND_MAP[cmd]
                payload = UDP_PACK.pack(encode_udp_command(udp_cmd), value)
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
                    udp_sock.sendto(payload, UDP_SERVER)
                    response, _ = udp_sock.recvfrom(1024)
                client.sendall(response)


def main():
    parser = argparse.ArgumentParser(description="Task 3c: TCP proxy to UDP state server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9103)
    args = parser.parse_args()
    run_proxy(args.host, args.port)


if __name__ == "__main__":
    main()
