import sys
import socket
import struct

def process_data_modified(text, cut_length):
    """Levágja a szöveg elejéről 'cut_length' karaktert, és megfordítja a levágott részt."""
    cut_part = text[:cut_length]
    return cut_part[::-1]

def main_udp_server():
    if len(sys.argv) != 3:
        print("Használat: python server:UDP.py <IP-cím> <Port>")
        return

    server_addr = sys.argv[1]
    server_port = int(sys.argv[2])
    packer_recv = struct.Struct('20s i')

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((server_addr, server_port))
            print(f"UDP Szerver elindítva: {server_addr}:{server_port}. Várakozás üzenetre...")

            while True:
                # 1. Adat fogadása és a kliens címének rögzítése (recvfrom)
                msg, client_addr = sock.recvfrom(1024) 
                
                if len(msg) < packer_recv.size:
                    print(f"Hiányos adat érkezett a {client_addr}-tól. Elvetve.")
                    continue

                # Kicsomagolás (20s i)
                text_encoded, cut_length = packer_recv.unpack(msg)
                text = text_encoded.decode('utf-8').rstrip('\x00')
                
                print(f"\nKliens üzenete ({client_addr}): '{text}', X: {cut_length}")
                
                # Logika végrehajtása
                result = process_data_modified(text, cut_length)
                result_len = len(result)
                
                # Válasz visszaküldése (Xs formátum, X = result_len)
                FORMAT_STRING_SEND = f'{result_len}s'
                packer_send = struct.Struct(FORMAT_STRING_SEND)
                
                result_encoded = result.encode('utf-8')
                reply = packer_send.pack(result_encoded)
                
                # 2. Válasz visszaküldése a fogadott címre (sendto)
                sock.sendto(reply, client_addr)
                print(f"Válasz elküldve a {client_addr}-nek ('{result}').")

    except KeyboardInterrupt:
        print("\nUDP Szerver leállítás...")
    except Exception as e:
        print(f"Szerver hiba: {e}")

if __name__ == "__main__":
    main_udp_server()