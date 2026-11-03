import sys
import socket
import struct

# Állandó méretek
TEXT_MAX_LEN = 20
FORMAT_STRING_RECV = f'{TEXT_MAX_LEN}s i'
packer_recv = struct.Struct(FORMAT_STRING_RECV)

# -------------------------------------------------------------
# Módosított függvény a szerver logikájához
def process_data_modified(text, cut_length):
    """Levágja a szöveg elejéről 'cut_length' karaktert, és megfordítja a levágott részt."""
    
    # Ha a levágandó hossz nagyobb vagy egyenlő a teljes hosszal, a teljes szöveg a levágott rész
    if cut_length >= len(text):
        cut_part = text
    else:
        # Levágjuk az első 'cut_length' karaktert
        cut_part = text[:cut_length]
    
    # Megfordítjuk a levágott részt
    reversed_text = cut_part[::-1]
    
    return reversed_text
# -------------------------------------------------------------

def main_server_modified():
    if len(sys.argv) != 3:
        print("Használat: python server.py <IP-cím> <Port>")
        return

    server_addr = sys.argv[1]
    server_port = int(sys.argv[2])

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((server_addr, server_port))
            sock.listen(1)
            print(f"🚀 Szerver elindítva (MÓDOSÍTOTT LOGIKA): {server_addr}:{server_port}. Várakozás kapcsolatra...")

            while True:
                conn = None
                try:
                    conn, addr = sock.accept()
                    print(f"\n✅ Kapcsolódott egy kliens: {addr}")

                    msg = conn.recv(packer_recv.size)
                    
                    if not msg:
                        print("❌ A kliens lezárta a kapcsolatot.")
                        conn.close()
                        continue
                    
                    if len(msg) < packer_recv.size:
                        print(f"⚠️ Hiányos adat érkezett ({len(msg)} bájt a várt {packer_recv.size} helyett).")
                        conn.close()
                        continue

                    # Kicsomagolás (20s i)
                    text_bytes, cut_length = packer_recv.unpack(msg)
                    text = text_bytes.decode('utf-8').rstrip('\x00') 
                    
                    print(f"📥 Kliens üzenete: '{text}', Levágandó karakterek száma (X): {cut_length}")
                    
                    # Módosított logika végrehajtása
                    if cut_length <= 0:
                        print("⚠️ Hiba: Érvénytelen levágási hossz (<= 0). Üres eredménnyel válaszol.")
                        result = "" 
                    else:
                        result = process_data_modified(text, cut_length)
                        
                    result_len = len(result) # Itt: result_len = min(len(text), cut_length)
                    
                    # Válasz visszaküldése (Xs formátum, X = result_len = Levágott rész hossza)
                    FORMAT_STRING_SEND = f'{result_len}s'
                    packer_send = struct.Struct(FORMAT_STRING_SEND)
                    
                    result_encoded = result.encode('utf-8')
                    reply = packer_send.pack(result_encoded)
                    
                    conn.sendall(reply)
                    print(f"📤 Válasz elküldve ('{result}', formátum: {FORMAT_STRING_SEND}, méret: {len(reply)} bájt)")

                except struct.error as se:
                    print(f"❌ Struktúra hiba: {se}")
                except Exception as e:
                    print(f"❌ Hiba történt: {e}")
                finally:
                    if conn:
                        conn.close()

    except KeyboardInterrupt:
        print("\n🛑 Szerver leállítás...")
    except Exception as e:
        print(f"❌ Szerver hiba: {e}")

if __name__ == "__main__":
    main_server_modified()