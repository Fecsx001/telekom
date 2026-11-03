import socket
import struct
import sys

TEXT_MAX_LEN = 5 # A parancs hossza
RECV_PACKER = struct.Struct(f'{TEXT_MAX_LEN}s i') # struct formátum a bejövő üzenetekhez: 5s (parancs) + i (érték)
RECV_SIZE = RECV_PACKER.size

FORMAT_SEND = 'i'
SEND_PACKER = struct.Struct(FORMAT_SEND)

GLOBAL_VALUE = 0 

def main():
    global GLOBAL_VALUE

    if len(sys.argv) != 3:
        print("Használat: python server.py <IP-cím> <Port>")
        return

    SERVER_IP = sys.argv[1]
    SERVER_PORT = int(sys.argv[2])

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((SERVER_IP, SERVER_PORT))
            print(f"UDP Szerver elindítva: {SERVER_IP}:{SERVER_PORT}. Közös érték: {GLOBAL_VALUE}")

            while True:
                # 1. Adat fogadása és a kliens címének rögzítése (recvfrom)
                # 1024 elegendő a bejövő csomag méretének, de legalább a RECV_SIZE kell
                msg, client_addr = sock.recvfrom(1024) 
                
                if len(msg) < RECV_SIZE:
                    print(f"Hiányos csomag ({len(msg)} bájt) a {client_addr}-tól. Elvetve.")
                    continue

                # Kicsomagolás (5s i)
                try:
                    command_decoded, value = RECV_PACKER.unpack(msg)
                    command = command_decoded.decode('utf-8').strip().upper()
                except struct.error as se:
                    print(f"Struktúra hiba a {client_addr}-tól érkező adatnál: {se}. Elvetve.")
                    continue
                
                print(f"\nKliens üzenete ({client_addr}): {command}, {value}")
                
                # Parancs feldolgozása és a közös érték módosítása
                old_value = GLOBAL_VALUE
                
                if command == "PUSH":               # nem kell szóköz, mert levágtuk őket
                    GLOBAL_VALUE = value
                    print(f"👉 PUSH: {old_value} -> {GLOBAL_VALUE} (Új érték: {value})")
                elif command == "PLUS":
                    GLOBAL_VALUE += value
                    print(f"👉 PLUS: {old_value} -> {GLOBAL_VALUE} (Növelés: {value})")
                elif command == "MINUS":
                    GLOBAL_VALUE -= value
                    print(f"👉 MINUS: {old_value} -> {GLOBAL_VALUE} (Csökkentés: {value})")
                else:
                    print(f"Ismeretlen parancs: {command} (Érték: {value})")
                
                # Válasz struct formában
                reply = SEND_PACKER.pack(GLOBAL_VALUE)
                
                sock.sendto(reply, client_addr)
                print(f"Válasz elküldve a {client_addr}-nek: {GLOBAL_VALUE}")
    except KeyboardInterrupt:
        print("\nSzerver leállítás...")
    except Exception as e:
        print(f"Általános hiba a select hívásban: {e}")

if __name__ == "__main__":
    main()