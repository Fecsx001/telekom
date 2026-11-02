import socket, struct, time
with socket.socket() as s:
    s.connect(('localhost', 10000))
    for cmd, x in [(b'IN', 20), (b'INCR', 4), (b'DECR', 5)]:
        s.sendall(struct.pack('4s i', cmd, x))
        print(cmd.decode(), x, '->', s.recv(1024).decode())
