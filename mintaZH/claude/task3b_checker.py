# 3/b: ellenorzo kliens - "0-val valo noveles" mindket szerveren
import socket, struct
TCP_ADDR, UDP_ADDR = ('localhost', 10000), ('localhost', 10001)

with socket.socket() as t:
    t.connect(TCP_ADDR)
    t.sendall(struct.pack('4s i', b'INCR', 0))
    tcp_val = int(t.recv(1024).decode())

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as u:
    u.settimeout(3)
    u.sendto(struct.pack('5s i', b'PLUS', 0), UDP_ADDR)
    udp_val = struct.unpack('i', u.recvfrom(1024)[0])[0]

print('TCP:', tcp_val, ' UDP:', udp_val)
print('Az UDP szerver HIBAZOTT' if tcp_val != udp_val else 'Az ertekek egyeznek')
