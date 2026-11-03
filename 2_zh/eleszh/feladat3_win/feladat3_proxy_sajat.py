import socket
import struct
import sys

# Konfiguráció
PROXY_HOST = 'localhost'
PROXY_PORT = 10003
UDP_SERVER_ADDR = ('localhost', 10002)
TCP_SERVER_ADDR = ('localhost', 10001)

PACKER = struct.Struct('i 20s')                 # sürgősségjelző (i) és üzenet (20s)

#  TCP hallgató socket
proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
proxy.bind((PROXY_HOST, PROXY_PORT))
proxy.listen(5)
print(f"Proxy elindult, TCP-n fogad: {PROXY_PORT}")

while True:
    # kliens kapcsolat fogadása (blokkoló)
    conn, addr = proxy.accept()
    try:
        # adat fogadása a klienstől
        data = conn.recv(PACKER.size)
        if not data:
            conn.close()
            continue
            
        sos, msg_bytes = PACKER.unpack(data)
        
        # Tisztítás a struct által hozzáadott null bájtoktól (opcionális, de jó gyakorlat)
        # msg = msg_bytes.strip(b'\x00') 
        msg = msg_bytes # A 20s formátum miatt a szerver elvárhatja a teljes 20 bájtot
        
        server_response = b''
        
        if sos == 0:  # TCP szerverhez küldjük (Nem sürgős)            
            # új TCP socket a TCP szerverhez
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.connect(TCP_SERVER_ADDR) 
            
            # Küldés (connect után sima send)
            tcp_socket.sendall(msg)
            
            # Válasz fogadása (sima recv)
            server_response = tcp_socket.recv(1024)
            tcp_socket.close()

        else:  # UDP szerverhez küldjük (Sürgős)            
            # új UDP socket
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Küldés (sendto)
            udp_socket.sendto(msg, UDP_SERVER_ADDR)
            
            # Válasz fogadása (recvfrom, tuple-t ad vissza)
            data, server_addr = udp_socket.recvfrom(1024)
            server_response = data # Csak az adatot vesszük
            udp_socket.close()

        # válasz visszaküldése a kliensnek
        conn.sendall(server_response)
        print(f"<- Válasz visszaküldve a kliensnek.")

    except Exception as e:
        print(f"Hiba a kommunikáció során: {e}")

    finally:
        # Kapcsolat lezárása a klienssel
        conn.close()
        print(f"Kapcsolat lezárva: {addr}\n")