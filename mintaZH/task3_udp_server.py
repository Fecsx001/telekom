import argparse
import random
import socket
import struct

REQUEST = struct.Struct("5s i")
REPLY = struct.Struct("i")


def normalize_name(raw: bytes) -> str:
    return raw.decode("ascii", errors="replace").strip().upper()


def run_server(host: str, port: int):
    state = 0
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((host, port))
        print(f"[UDP state server] listening on {host}:{port}")
        while True:
            data, client = sock.recvfrom(4096)
            if len(data) != REQUEST.size:
                print(f"[UDP] invalid packet from {client}: {len(data)} bytes")
                continue

            cmd_raw, value = REQUEST.unpack(data)
            cmd = normalize_name(cmd_raw)
            drift = random.randint(-1, 1)
            adjusted = value + drift
            if cmd == "PUSH":
                state = adjusted
            elif cmd == "PLUS":
                state += adjusted
            elif cmd == "MINUS":
                state -= adjusted
            else:
                print(f"[UDP] unknown command: {cmd!r}")
                continue

            print(f"[{client}] {cmd} {value} -> drift={drift}, state={state}")
            sock.sendto(REPLY.pack(state), client)


def main():
    parser = argparse.ArgumentParser(description="Task 3a/3b: UDP state server with random drift")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9102)
    args = parser.parse_args()
    run_server(args.host, args.port)


if __name__ == "__main__":
    main()
