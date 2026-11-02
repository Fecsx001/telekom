import socket, struct
FMT = '20s i'
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.bind(('localhost', 10000))
while True:
    data, addr = s.recvfrom(1024)
    text, num = struct.unpack(FMT, data)
    res = text.rstrip(b'\0').decode()[:num][::-1]
    s.sendto(struct.pack(f'{num}s', res.encode()), addr)
