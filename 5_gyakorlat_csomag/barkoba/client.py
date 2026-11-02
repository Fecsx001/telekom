import socket
import struct
import sys


packer_guess = struct.Struct("6s i i")
packer_answer = struct.Struct("c 10s")
packer_final = struct.Struct("6s 10s i")
packer_code = struct.Struct("12s")


def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            return b""
        data += chunk
    return data


def pad_neptun(name):
    return name.encode("ascii").ljust(6, b" ")[:6]


def main():
    if len(sys.argv) != 4:
        print(f"Használat: python {sys.argv[0]} <host> <port> <NEPTUN>", file=sys.stderr)
        raise SystemExit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    neptun = pad_neptun(sys.argv[3])

    lower_bound = 1
    upper_bound = 100
    send_count = 0

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((host, port))

        while True:
            send_count += 1
            guess = (lower_bound + upper_bound) // 2
            client.sendall(packer_guess.pack(neptun, guess, send_count))

            data = recv_exact(client, packer_answer.size)
            if not data:
                raise RuntimeError("A szerver lezárta a kapcsolatot a válasz előtt.")

            method, identifier = packer_answer.unpack(data)
            identifier = identifier.rstrip(b"\x00")

            if method == b"=":
                if not identifier:
                    raise RuntimeError("Találat volt, de üres azonosító érkezett.")
                client.sendall(packer_final.pack(neptun, identifier, send_count + 1))
                code = recv_exact(client, packer_code.size)
                if not code:
                    raise RuntimeError("A szerver nem adott vissza kódot.")
                answer = packer_code.unpack(code)[0].rstrip(b"\x00").decode("ascii", errors="replace")
                print(answer)
                return

            if method == b"<":
                upper_bound = guess - 1
            elif method == b">":
                lower_bound = guess + 1
            else:
                raise RuntimeError(f"Ismeretlen válasz: {method!r}")

            if lower_bound > upper_bound:
                raise RuntimeError("A bináris keresés érvénytelen tartományra jutott.")


if __name__ == "__main__":
    main()
