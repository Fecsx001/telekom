import socket
import struct
import sys
import random

# --- Állandók és Globális Állapot ---
COMMAND_MAX_LEN = 5 
RECV_PACKER = struct.Struct(f'{COMMAND_MAX_LEN}s i')
RECV_SIZE = RECV_PACKER.size

FORMAT_SEND = 'i' 
SEND_PACKER = struct.Struct(FORMAT_SEND)

GLOBAL_UDP_VALUE = 0 

# --- Fő Szerver Függvény ---
def main_udp_server_error():
    global GLOBAL_UDP_VALUE
    
    if len(sys.argv) != 3:
        print("Használat: python UDP_server_error.py <IP-cím> <Port>")
        return

    SERVER_IP = sys.argv[1]
    SERVER_PORT = int(sys.argv[2])

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((SERVER_IP, SERVER_PORT))
            print(f"UDP Szerver (Hibás) elindítva: {SERVER_IP}:{SERVER_PORT}. Közös érték: {GLOBAL_UDP_VALUE}")

            while True:
                msg, client_addr = sock.recvfrom(1024) 
                
                if len(msg) < RECV_SIZE: continue

                try:
                    command_bytes, value = RECV_PACKER.unpack(msg[:RECV_SIZE])
                    command = command_bytes.decode('utf-8').strip().upper()
                except struct.error:
                    continue
                
                old_value = GLOBAL_UDP_VALUE
                
                # --- HIBABEVEZETÉS ---
                error_value = random.randint(-1, 1) # Véletlen hiba: -1, 0, vagy 1
                
                if command == "PUSH":
                    GLOBAL_UDP_VALUE = value
                elif command == "PLUS":
                    GLOBAL_UDP_VALUE += value
                elif command == "MINUS":
                    GLOBAL_UDP_VALUE -= value
                else:
                    # Ismeretlen command, az érték nem változik
                    error_value = 0 # Itt nem adunk hozzá hibát, ha nem parancs
                    
                # A HIBÁT MINDEN PARANCS FELDOLGOZÁSA UTÁN HOZZÁADJUK (kivéve az ismeretlent)
                if command in ["PUSH", "PLUS", "MINUS"]:
                    GLOBAL_UDP_VALUE += error_value
                    if error_value != 0:
                         print(f"Hiba bevezetve: {command}, {value}. Hozzáadva: {error_value}")
                    
                print(f"Kliens üzenete ({client_addr}): {command}, {value}. Új érték: {GLOBAL_UDP_VALUE}")
                    
                # Válasz visszaküldése struct formátumban (i)
                reply = SEND_PACKER.pack(GLOBAL_UDP_VALUE)
                sock.sendto(reply, client_addr)

    except KeyboardInterrupt:
        print("\nSzerver leállítás...")
    except Exception as e:
        print(f"Szerver hiba: {e}")

if __name__ == "__main__":
    main_udp_server_error()