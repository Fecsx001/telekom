import argparse
import socket
import struct

PACK = struct.Struct("20s i")


def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            return b""
        data += chunk
    return data


def transform_text(text: str, count: int) -> str:
    if count <= 0:
        return ""
    count = min(count, len(text))
    return text[:count][::-1]


def handle_tcp_request(data: bytes) -> bytes:
    text_bytes, count = PACK.unpack(data)
    text = text_bytes.rstrip(b"\x00").decode("utf-8", errors="replace")
    return transform_text(text, count).encode("utf-8")


def run_tcp_server(host: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(5)
        print(f"[TCP server] listening on {host}:{port}")
        while True:
            client, addr = server.accept()
            with client:
                print(f"[TCP] client connected: {addr}")
                data = recv_exact(client, PACK.size)
                if not data:
                    continue
                response = handle_tcp_request(data)
                client.sendall(response)
                try:
                    client.shutdown(socket.SHUT_WR)
                except OSError:
                    pass


def run_udp_server(host: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        server.bind((host, port))
        print(f"[UDP server] listening on {host}:{port}")
        while True:
            data, client = server.recvfrom(4096)
            if len(data) != PACK.size:
                print(f"[UDP] invalid packet length from {client}: {len(data)} bytes")
                continue
            response = handle_tcp_request(data)
            server.sendto(response, client)


def main():
    parser = argparse.ArgumentParser(description="Task 1: TCP/UDP string transformation server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9001)
    parser.add_argument("--udp", action="store_true")
    args = parser.parse_args()

    if args.udp:
        run_udp_server(args.host, args.port)
    else:
        run_tcp_server(args.host, args.port)


if __name__ == "__main__":
    main()
