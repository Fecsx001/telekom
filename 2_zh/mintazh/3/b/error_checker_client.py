import socket
import struct
import sys

# --- TCP Konfiguráció (TCP szerver parancsai) ---
TCP_IP = '127.0.0.1'
TCP_PORT = 5000 
TCP_COMMAND = "INCR" # 0-val való növelés (lekérdezés)
TCP_PACKER_SEND = struct.Struct('4s i')

# --- UDP Konfiguráció (UDP szerver parancsai) ---
UDP_IP = '127.0.0.1'
UDP_PORT = 4000
UDP_COMMAND = "PLUS" # 0-val való növelés (lekérdezés)
UDP_PACKER_SEND = struct.Struct('5s i')
UDP_PACKER_RECV = struct.Struct('i')

def get_tcp_value():
    """Lekérdezi az aktuális értéket a TCP szervertől (INCR 0)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((TCP_IP, TCP_PORT))
            
            # Csomagolás: 'INCR' + 0
            cmd_bytes = TCP_COMMAND.ljust(4).encode('utf-8')
            message = TCP_PACKER_SEND.pack(cmd_bytes, 0)
            
            sock.sendall(message)
            
            # Válasz bytesztringként érkezik
            response = sock.recv(1024)
            if response:
                return int(response.decode('utf-8'))
            return None
    except ConnectionRefusedError:
        print(f"TCP Hiba: Nincs futó szerver a {TCP_PORT} porton.")
        return None
    except Exception as e:
        print(f"TCP Hiba: {e}")
        return None

def get_udp_value():
    """Lekérdezi az aktuális értéket az UDP szervertől (PLUS 0)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(2.0)
            
            # Csomagolás: 'PLUS' + 0
            cmd_bytes = UDP_COMMAND.ljust(5).encode('utf-8')
            message = UDP_PACKER_SEND.pack(cmd_bytes, 0)
            
            sock.sendto(message, (UDP_IP, UDP_PORT))
            
            # Válasz structként érkezik
            response, _ = sock.recvfrom(UDP_PACKER_RECV.size)
            if response:
                (current_value,) = UDP_PACKER_RECV.unpack(response)
                return current_value
            return None
    except socket.timeout:
        print("UDP Hiba: Időtúllépés (nincs válasz a szervertől).")
        return None
    except ConnectionRefusedError:
        print(f"UDP Hiba: Nincs futó szerver a {UDP_PORT} porton.")
        return None
    except Exception as e:
        print(f"UDP Hiba: {e}")
        return None

def main_checker():
    print("--- Ellenőrző Kliens Indul ---")

    # Lekérdezés
    tcp_val = get_tcp_value()
    udp_val = get_udp_value()

    print(f"\nTCP Szerver Érték: {tcp_val}")
    print(f"UDP Szerver Érték: {udp_val}")

    if tcp_val is None or udp_val is None:
        print("\nA teszt sikertelen: Nem kaptunk értéket mindkét szervertől.")
        return

    # Összehasonlítás
    diff = udp_val - tcp_val
    
    if diff == 0:
        print("\nAz UDP szerver az elvárt értéket adta vissza (különbség: 0). Nincs Hiba.")
    elif diff in [-1, 1]:
        print(f"\nAz UDP szerver HIBAÜZENETET TARTALMAZÓ értéket adott vissza.")
        print(f"   Elvárt (TCP): {tcp_val}, Kapott (UDP): {udp_val}, Különbség: {diff}.")
    else:
        print(f"\nSÚLYOS HIBA: Az UDP szerver értéke jelentősen eltér az elvárttól (Különbség: {diff}).")
        
if __name__ == "__main__":
    main_checker()