import socket, struct, random
HOST, PORT = 'localhost', 10000
FMT = '20s i'

def recv_all(sock, n):                       # pontosan n bajt (TCP stream!)
    buf = b''
    while len(buf) < n:
        part = sock.recv(n - len(buf))
        if not part: raise ConnectionError('A szerver lezarta a kapcsolatot')
        buf += part
    return buf

text = input('Szoveg: ')
num = random.randint(1, len(text))           # veletlen szam (1..hossz)
print('Kuldes:', text, num)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(struct.pack(FMT, text.encode()[:20], num))
    reply_fmt = f'{num}s'                    # a valasz formatuma a szamtol fugg
    data = recv_all(s, struct.calcsize(reply_fmt))
    print('Valasz:', struct.unpack(reply_fmt, data)[0].decode())
