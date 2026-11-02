# 2. feladat: select-es TCP szerver, kozos szamlalo, parancsok: '4s i'
import socket, select, struct
HOST, PORT = '0.0.0.0', 10000
FMT = '4s i'; SIZE = struct.calcsize(FMT)    # 8 bajt
value = 0

srv = socket.socket(); srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind((HOST, PORT)); srv.listen()
inputs = [srv]; buffers = {}                 # kliensenkent pufferelunk

def process(cmd, x):
    global value
    cmd = cmd.rstrip(b'\0').decode().strip().upper()
    if cmd == 'IN': value = x
    elif cmd == 'INCR': value += x
    elif cmd == 'DECR': value -= x
    return value

while True:
    readable, _, _ = select.select(inputs, [], [])
    for s in readable:
        if s is srv:
            c, addr = srv.accept(); inputs.append(c); buffers[c] = b''
            print('Uj kliens:', addr)
            continue
        data = s.recv(1024)
        if not data:                         # kliens lezart
            inputs.remove(s); del buffers[s]; s.close(); continue
        buffers[s] += data
        while len(buffers[s]) >= SIZE:       # tobb parancs / fel parancs kezelese
            chunk, buffers[s] = buffers[s][:SIZE], buffers[s][SIZE:]
            cmd, x = struct.unpack(FMT, chunk)
            s.sendall(str(process(cmd, x)).encode())
