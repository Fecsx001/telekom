import socket, struct, random
ADDR = ('localhost', 10000)
FMT = '20s i'
text = input('Szoveg: ')
num = random.randint(1, len(text))
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.settimeout(3)                          # UDP: nincs garancia, kell timeout
    s.sendto(struct.pack(FMT, text.encode()[:20], num), ADDR)
    data, _ = s.recvfrom(1024)               # egy datagram = egy valasz
    rf = f'{num}s'
    print('Valasz:', struct.unpack(rf, data[:struct.calcsize(rf)])[0].decode())
