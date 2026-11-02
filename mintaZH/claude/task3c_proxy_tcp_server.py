# 3/c: TCP proxy szerver (select) - az ertek az UDP szerveren van
import socket, select, struct
PORT, UDP_ADDR = 10000, ('localhost', 10001)
IN_FMT, OUT_FMT = '4s i', '5s i'
IN_SIZE = struct.calcsize(IN_FMT)
MAP = {'IN': b'PUSH', 'INCR': b'PLUS', 'DECR': b'MINUS'}   # TCP -> UDP parancs

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); udp.settimeout(2)
srv = socket.socket(); srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(('0.0.0.0', PORT)); srv.listen()
inputs, buffers = [srv], {}

def forward(cmd, x):
    cmd = cmd.rstrip(b'\0').decode().strip().upper()
    udp.sendto(struct.pack(OUT_FMT, MAP[cmd], x), UDP_ADDR)
    data, _ = udp.recvfrom(1024)
    return struct.unpack('i', data)[0]

while True:
    readable, _, _ = select.select(inputs, [], [])
    for s in readable:
        if s is srv:
            c, _ = srv.accept(); inputs.append(c); buffers[c] = b''; continue
        data = s.recv(1024)
        if not data:
            inputs.remove(s); del buffers[s]; s.close(); continue
        buffers[s] += data
        while len(buffers[s]) >= IN_SIZE:
            chunk, buffers[s] = buffers[s][:IN_SIZE], buffers[s][IN_SIZE:]
            cmd, x = struct.unpack(IN_FMT, chunk)
            try: s.sendall(str(forward(cmd, x)).encode())
            except (socket.timeout, KeyError): s.sendall(b'ERROR')
