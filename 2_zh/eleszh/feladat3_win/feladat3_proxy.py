import socket
import struct
import select

proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
proxy.bind(('localhost', 10003))
proxy.listen(5)
proxy.setblocking(False)                    # nem-blokkoló mód a select-hez

udp_server = ('localhost', 10002)
tcp_server = ('localhost', 10001)

packer = struct.Struct('i 20s')             # sürgősségjelző és üzenet

tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.connect(tcp_server)
# tcp_socket.setblocking(False)
            
inputs = [proxy, tcp_socket]
outputs = []

client_map = {}         # a kliensek, akiknek épp válaszolunk
                        # kulcs: a szerver socket, érték: a kliens socket (conn)

try:
    while inputs:        
        rlist, wlist, xlist = select.select(inputs, outputs, inputs);

        for s in rlist:
            if s is proxy:
                conn, addr = proxy.accept()             # client sockete és címe (host, port)
                # conn.setblocking(False);
                inputs.append(conn);
            elif s is tcp_socket:
                # válasz érkezett a tcp szerverről
                data = s.recv(1024)
                if data and s in client_map:
                    target_client = client_map.pop(s)
                    try:
                        target_client.sendall(data);
                    finally:
                        target_client.close();
                        if target_client in inputs:
                            inputs.remove(target_client);
            else:
                # adat érkezett a klienstől
                data = s.recv(packer.size)
                if data:
                    sos, msg = packer.unpack(data)
                    if sos == 0:
                        client_map[tcp_socket] = s
                        tcp_socket.sendall(msg)
                    else:
                        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   # UDP-nél nincs connect!!!
                        udp_socket.sendto(msg, udp_server)

                        data, addr = udp_socket.recvfrom(1024)      # recvfrom adattal + címmel tér vissza!!!
                        reply = data
                        s.sendall(reply)
                        s.close()
                        inputs.remove(s)
                        udp_socket.close()
                else:
                    # A kliens lezárta a kapcsolatot
                    if s in inputs:
                        inputs.remove(s)
                    s.close()
        for s in xlist:
            inputs.remove(s)
            s.close()

except Exception as e:
    print(f"Hiba a kommunikáció során: {e}")
finally:
    # Kapcsolat lezárása a klienssel
    proxy.close()
    tcp_socket.close()
    print(f"Kapcsolat lezárva.")
    
# kapott eremények
# Test1: aK9xT2mQ7Zp4
# Test2: B3nV8yR1cL0d
# Test3: zH7qW5kM2fP9
# Test4: J6uE1tX4sN8b
#
        