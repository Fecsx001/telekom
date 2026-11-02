# 3/a-b: UDP szerver, PUSH/PLUS/MINUS, parancs '5s i', valasz 'i'
# Hibas mod:  python3 task3a_udp_server.py --faulty
import socket, struct, random, sys
PORT = 10001
FAULTY = '--faulty' in sys.argv
FMT = '5s i'
value = 0
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.bind(('localhost', PORT))
while True:
    data, addr = s.recvfrom(1024)
    cmd, x = struct.unpack(FMT, data[:struct.calcsize(FMT)])
    cmd = cmd.rstrip(b'\0').decode().upper()
    if FAULTY: x += random.choice([-1, 0, 1])   # 3/b: veletlen hiba
    if cmd == 'PUSH': value = x
    elif cmd == 'PLUS': value += x
    elif cmd == 'MINUS': value -= x
    s.sendto(struct.pack('i', value), addr)
