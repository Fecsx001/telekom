# Teszt szerver az 1. feladathoz (a ZH-n a szerver meg lesz adva)
import socket, struct
FMT = '20s i'; SIZE = struct.calcsize(FMT)
s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('localhost', 10000)); s.listen()
while True:
    c, _ = s.accept()
    data = c.recv(SIZE)
    text, num = struct.unpack(FMT, data)
    text = text.rstrip(b'\0').decode()
    res = text[:num][::-1]                      # elso X karakter, megforditva
    c.sendall(struct.pack(f'{num}s', res.encode()))
    c.close()
