import socket
import select
import struct
import sys

# --- TCP/Client Oldali Állandók ---
# Bejövő TCP üzenet: 4s (parancs) + i (érték)
TCP_COMMAND_LEN = 4
TCP_RECV_PACKER = struct.Struct(f'{TCP_COMMAND_LEN}s i')
TCP_RECV_SIZE = TCP_RECV_PACKER.size
# A TCP kliens válasza bytesztring volt, de most az UDP válaszát (struct i) küldjük vissza.

# --- UDP/Server Oldali Állandók ---
# Kifelé menő UDP üzenet: 5s (parancs) + i (érték)
UDP_SERVER_IP = '127.0.0.1' 
UDP_SERVER_PORT = 4000 # Feltételezzük, hogy itt fut az UDP szerver
UDP_COMMAND_LEN = 5
UDP_SEND_PACKER = struct.Struct(f'{UDP_COMMAND_LEN}s i')
# UDP válasz: i (integer)
UDP_RECV_PACKER = struct.Struct('i')
UDP_RECV_SIZE = UDP_RECV_PACKER.size

def map_command_and_format(tcp_command, tcp_value):
    """
    TCP parancs lefordítása UDP parancsra és a küldendő struct előállítása.
    """
    udp_command = None
    udp_value = tcp_value
    
    if tcp_command == "IN":
        udp_command = "PUSH"
    elif tcp_command == "INCR":
        udp_command = "PLUS"
    elif tcp_command == "DECR":
        udp_command = "MINUS"
        
    if udp_command:
        # Kódolás: 5 bájtra igazítás és struct csomagolás
        cmd_bytes = udp_command.ljust(UDP_COMMAND_LEN).encode('utf-8')
        udp_message = UDP_SEND_PACKER.pack(cmd_bytes, udp_value)
        return udp_message, udp_command
    
    return None, None


def handle_client_request(tcp_client_sock, udp_socket):
    """
    Lekezeli az egy kliens TCP kérését: fogad, proxyzál az UDP-nek, visszaküld.
    """
    try:
        # 1. TCP kérés fogadása
        data = tcp_client_sock.recv(TCP_RECV_SIZE)
        
        if not data:
            # Kliens lezárta a kapcsolatot
            return False 

        if len(data) < TCP_RECV_SIZE:
             print(f"Hiányos TCP csomag érkezett. Elvetve.")
             return True

        # Kicsomagolás (4s i)
        command_bytes, value = TCP_RECV_PACKER.unpack(data)
        tcp_command = command_bytes.decode('utf-8').strip().upper()
        
        print(f"TCP Kérés: {tcp_client_sock.getpeername()} -> {tcp_command}, {value}")
        
        # 2. Protokoll konverzió és UDP csomag előállítása
        udp_message, udp_command = map_command_and_format(tcp_command, value)

        if not udp_message:
            # Ismeretlen parancs esetén visszaküldjük a hibaüzenetet
            error_msg = f"Ismeretlen parancs: {tcp_command}".encode('utf-8')
            tcp_client_sock.sendall(error_msg)
            return True

        # 3. Proxyzás az UDP szerver felé
        udp_socket.sendto(udp_message, (UDP_SERVER_IP, UDP_SERVER_PORT))
        print(f"Proxy: TCP ({tcp_command}) -> UDP ({udp_command}) elküldve.")

        # 4. UDP válasz fogadása
        # Az UDP szerver válasza struct 'i' (4 bájt)
        udp_response, _ = udp_socket.recvfrom(UDP_RECV_SIZE)
        
        if len(udp_response) != UDP_RECV_SIZE:
             raise IOError("Hibás méretű UDP válasz érkezett.")
        
        # Kicsomagolás (i)
        (final_value,) = UDP_RECV_PACKER.unpack(udp_response)

        # 5. Válasz visszaküldése a TCP kliensnek
        # A feladat azt kéri, hogy az UDP szerver válaszát küldje vissza.
        # Az UDP szerver 'i' formátumban küld, a TCP kliens ezt kapja.
        tcp_client_sock.sendall(udp_response)
        
        print(f"Válasz: {final_value} (struct i) visszaküldve a TCP kliensnek.")
        
        return True # Sikeres feldolgozás
        
    except ConnectionResetError:
        print(f"Kapcsolat megszakadt a klienssel: {tcp_client_sock.getpeername()}")
        return False
    except socket.timeout:
        print("Időtúllépés az UDP várakozásnál.")
        # Visszaküldünk egy nulla értéket a kliensnek, ha nincs válasz
        tcp_client_sock.sendall(UDP_RECV_PACKER.pack(0))
        return True
    except Exception as e:
        print(f"Hiba történt a feldolgozásban ({tcp_client_sock.getpeername()}): {e}")
        return False # Kapcsolat lezárása

def main_tcp_proxy_server():
    
    if len(sys.argv) != 3:
        print("Használat: python TCP_proxy_server.py <IP-cím> <Port>")
        return

    SERVER_IP = sys.argv[1]
    SERVER_PORT = int(sys.argv[2])

    # 1. TCP Listen Socket beállítása
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    listen_socket.bind((SERVER_IP, SERVER_PORT))
    listen_socket.listen(5)
    
    # 2. UDP Socket létrehozása a háttérkommunikációhoz
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Beállítunk egy timeoutot, hogy ne akadjunk el, ha az UDP szerver meghal
    udp_socket.settimeout(3.0) 
    
    inputs = [listen_socket]
    print(f"TCP Proxy Szerver elindítva: {SERVER_IP}:{SERVER_PORT} (Proxyz UDP:{UDP_SERVER_PORT}-re)")

    while inputs:
        try:
            readable, _, _ = select.select(inputs, [], [], 1.0) 
            
            for sock in readable:
                if sock is listen_socket:
                    # Új TCP kapcsolat
                    connection, client_address = sock.accept()
                    connection.setblocking(False) 
                    inputs.append(connection) 
                    print(f"Új TCP kapcsolat: {client_address}")
                
                else:
                    # Adat érkezett egy meglévő TCP kliensről
                    if not handle_client_request(sock, udp_socket):
                        # Ha a kezelés hibával tért vissza, lezárjuk a kapcsolatot
                        sock.close()
                        inputs.remove(sock)
                            
        except KeyboardInterrupt:
            print("\nProxy Szerver leállítás...")
            break
        except Exception as e:
            print(f"Általános hiba a select hívásban: {e}")
            break
            
    for s in inputs:
        s.close()
    udp_socket.close()
    print("Szerver leállítva.")

if __name__ == "__main__":
    main_tcp_proxy_server()