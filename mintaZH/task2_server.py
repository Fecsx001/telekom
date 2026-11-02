import argparse
import select
import socket
import struct

PACK = struct.Struct("4s i")
CURRENT_VALUE = 0


def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            return b""
        data += chunk
    return data


def parse_command(raw: bytes):
    cmd_bytes, value = PACK.unpack(raw)
    cmd = cmd_bytes.decode("ascii", errors="replace").strip().upper()
    return cmd, value


def apply_command(cmd: str, value: int) -> int:
    global CURRENT_VALUE
    if cmd == "IN":
        CURRENT_VALUE = value
    elif cmd == "INCR":
        CURRENT_VALUE += value
    elif cmd == "DECR":
        CURRENT_VALUE -= value
    else:
        raise ValueError(f"Ismeretlen parancs: {cmd!r}")
    return CURRENT_VALUE


def run_server(host: str, port: int):
    global CURRENT_VALUE
    CURRENT_VALUE = 0
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(10)
        print(f"[Task 2] select server listening on {host}:{port}")
        inputs = [server]
        while True:
            readable, _, _ = select.select(inputs, [], [], 1.0)
            for sock in readable:
                if sock is server:
                    client, addr = server.accept()
                    print(f"[Task 2] new client: {addr}")
                    inputs.append(client)
                    continue

                data = recv_exact(sock, PACK.size)
                if not data:
                    print(f"[Task 2] client disconnected: {sock.getpeername()}")
                    inputs.remove(sock)
                    sock.close()
                    continue

                try:
                    cmd, value = parse_command(data)
                    result = apply_command(cmd, value)
                    sock.sendall(str(result).encode("ascii"))
                    print(f"[{sock.getpeername()}] {cmd} {value} -> {result}")
                except ValueError as exc:
                    print(f"[Task 2] error: {exc}")
                    sock.sendall(b"ERROR")


def main():
    parser = argparse.ArgumentParser(description="Task 2: multi-client TCP select server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9003)
    args = parser.parse_args()
    run_server(args.host, args.port)


if __name__ == "__main__":
    main()
