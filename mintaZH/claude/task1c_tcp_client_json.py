import socket, struct, random, json
HOST, PORT = 'localhost', 10000
FMT = '20s i'

def recv_all(sock, n):
    buf = b''
    while len(buf) < n:
        part = sock.recv(n - len(buf))
        if not part: raise ConnectionError('lezart kapcsolat')
        buf += part
    return buf

with open('input.json', encoding='utf-8') as f:
    data = json.load(f)
key = str(random.randint(1, 3))              # JSON kulcs mindig sztring!
text, num = data[key]
print('Kulcs:', key, text, num)
with socket.socket() as s:
    s.connect((HOST, PORT))
    s.sendall(struct.pack(FMT, text.encode(), num))
    rf = f'{num}s'
    print('Valasz:', struct.unpack(rf, recv_all(s, struct.calcsize(rf)))[0].decode())
