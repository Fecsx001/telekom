import select
import socket
import struct
import sys

packer = struct.Struct("i i c")  # ket szam es a muveleti jel, 9 byte

PROXY_ADDR = ("localhost", int(sys.argv[1]))
SERVER_ADDR = ("localhost", int(sys.argv[2]))


def recv_exact(sock, size):
    """Addig olvas, amig pontosan size byte meg nem erkezik (vagy a masik oldal bont)."""
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            return b""
        data += chunk
    return data


def proxy():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server, socket.socket(
        socket.AF_INET, socket.SOCK_STREAM
    ) as client:

        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client.bind(PROXY_ADDR)
        client.listen(5)
        print("Proxy is running:", PROXY_ADDR, "->", SERVER_ADDR)
        inputs = [client]

        while True:
            readables, _, _ = select.select(inputs, [], [], 1.0)
            for s in readables:
                if s is client:
                    client_con, addr = client.accept()
                    print(f"New client: {addr[0]}:{addr[1]}")
                    inputs.append(client_con)
                    continue
                msg = recv_exact(s, packer.size)
                if not msg:
                    inputs.remove(s)
                    s.close()
                    continue
                # atcsomagolas: a szerver csak a szamot kapja

                sent = server.sendto(msg, SERVER_ADDR)
                data, rec_serv = server.recvfrom(packer.size)
                s.sendall(data)


proxy()
