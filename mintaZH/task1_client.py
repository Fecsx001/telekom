import argparse
import json
import random
import socket
import struct

PACK = struct.Struct("20s i")


def send_message(host: str, port: int, text: str, value: int, udp: bool = False):
    payload = PACK.pack(text.encode("utf-8").ljust(20, b"\x00"), value)
    if udp:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(payload, (host, port))
            data, _ = sock.recvfrom(1024)
            return data.decode("utf-8", errors="replace")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(2.0)
        sock.connect((host, port))
        sock.sendall(payload)
        chunks = []
        try:
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
        except socket.timeout:
            pass
        return b"".join(chunks).decode("utf-8", errors="replace")


def mode_a(host: str, port: int, udp: bool):
    text = input("Szöveg: ").strip()
    value = random.randint(1, 10)
    print(f"Küldés: {text!r}, {value}")
    print("Válasz:", send_message(host, port, text, value, udp))


def mode_b(host: str, port: int, file_path: str, udp: bool):
    with open(file_path, "r", encoding="utf-8") as f:
        rows = [line.strip() for line in f if line.strip()]
    choice = random.choice(rows)
    text, value = choice.split()
    value = int(value)
    print(f"Kiválasztott sor: {choice}")
    print("Válasz:", send_message(host, port, text, value, udp))


def mode_c(host: str, port: int, file_path: str, udp: bool):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    key = str(random.randint(1, len(data)))
    text, value = data[key]
    print(f"Kiválasztott kulcs: {key} -> {text}, {value}")
    print("Válasz:", send_message(host, port, text, value, udp))


def mode_d(host: str, port: int):
    mode_a(host, port, udp=True)


def main():
    parser = argparse.ArgumentParser(description="Task 1: TCP/UDP client")
    parser.add_argument("--mode", choices=["a", "b", "c", "d"], required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9001)
    parser.add_argument("--file", default="input.txt")
    parser.add_argument("--json-file", default="input.json")
    parser.add_argument("--udp", action="store_true", help="use UDP for task d mode")
    args = parser.parse_args()

    if args.mode == "a":
        mode_a(args.host, args.port, args.udp)
    elif args.mode == "b":
        mode_b(args.host, args.port, args.file, args.udp)
    elif args.mode == "c":
        mode_c(args.host, args.port, args.json_file, args.udp)
    else:
        mode_d(args.host, args.port)


if __name__ == "__main__":
    main()
