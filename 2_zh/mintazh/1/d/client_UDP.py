import socket
import random
import struct
import sys

#d) A TCP kliens helyett használjunk UDP klienst! (Ekkor a szerver nyilván UDP szerver lesz.)

def main_udp_client():
    # TCP-vel ellentétben az UDP-nek nem kell a localhost, de használható.
    SERVER_IP = '127.0.0.1' 
    SERVER_PORT = 4000
    
    # Feladat (a) logikáját használjuk: felhasználói bevitel és véletlen szám
    text = input("Adj meg egy szöveget (max. 20 karakter): ")
    if len(text) == 0 or len(text) > 20:
        print(f"Hiba: A szöveg nem lehet üres és maximum 20 karakter lehet!")
        return
        
    szam = random.randint(1, len(text))
    
    print(f"Elküldendő adatok: Szöveg='{text}', Szám='{szam}'")

    packer_send = struct.Struct('20s i')

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        try:
            # 1. Csomagolás és küldés a szerver címére (sendto)
            text_bytes = text.encode('utf-8')
            message = packer_send.pack(text_bytes, szam)
            
            sock.sendto(message, (SERVER_IP, SERVER_PORT))
            print("Adatcsomag elküldve az UDP szervernek!")
            
            # 2. Válasz fogadása (recvfrom)
            expected_length = szam
            # Maximális buffer méret a fogadáshoz, 1024 elegendő
            response_message, server_addr = sock.recvfrom(1024) 
            
            if len(response_message) < expected_length:
                 print(f"Figyelem: Kevesebb adat érkezett, mint vártuk ({len(response_message)} bájt).")

            # Válasz kicsomagolása
            packer_recv = struct.Struct(f'{expected_length}s')
            (reversed_text_bytes, ) = packer_recv.unpack(response_message) # Biztosítjuk a pontos méretet
            reversed_text = reversed_text_bytes.decode('utf-8')
            
            print(f"Kapott válasz a szervertől ({server_addr}): {reversed_text}")
            
        except socket.timeout:
            print("Hiba: Időtúllépés - a szerver nem válaszolt időben.")
        except Exception as e:
            print(f"Hiba történt: {e}")

if __name__ == "__main__":
    main_udp_client()