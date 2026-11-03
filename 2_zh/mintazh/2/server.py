import socket
import select
import struct
import sys

TEXT_MAX_LEN = 4 # A parancs (pl. 'INCR') hossza
RECV_PACKER = struct.Struct(f'{TEXT_MAX_LEN}s i') # struct formátum a bejövő üzenetekhez: 4s (parancs) + i (érték)
RECV_SIZE = RECV_PACKER.size

# Közös állapot: A szerveren tárolt egész szám
GLOBAL_VALUE = 0 

# --- Fő Szerver Függvény ---
def main():
    global GLOBAL_VALUE

    if len(sys.argv) != 3:
        print("Használat: python server.py <IP-cím> <Port>")
        return

    SERVER_IP = sys.argv[1]
    SERVER_PORT = int(sys.argv[2])

    # Készítünk egy TCP listen socket-et
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Beállítjuk a SO_REUSEADDR opciót, hogy újrahasználható legyen a cím azonnal a szerver leállítása után
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    listen_socket.bind((SERVER_IP, SERVER_PORT))
    listen_socket.listen(5)
    
    # A figyelt socket-ek listája: kezdetben csak a listen socket van benne
    inputs = [listen_socket]
    print(f"Szerver elindítva: {SERVER_IP}:{SERVER_PORT}. Közös érték: {GLOBAL_VALUE}")

    while inputs:
        try:
            # select.select(rlist, wlist, xlist[, timeout])
            # Figyeljük, mely socket-ek állnak készen az olvasásra (rlist)
            readable, _, _ = select.select(inputs, [], [], 1.0) # 1.0 másodperces timeout
            
            for sock in readable: # olvasásra készen álló socketeken megyünk végig
                if sock is listen_socket:
                    # Új kapcsolat érkezett
                    connection, client_address = sock.accept()  # accept() --> Visszatér egy új socket objektummal (amit a klienssel való kommunikációra használunk) és a kliens címével
                    connection.setblocking(False)               # Non-blocking mód a select használatához
                    inputs.append(connection)                   # Hozzáadjuk a kliens socketet a figyelt listához
                    print(f"Új kapcsolat: {client_address}")
                
                else:
                    # Adat érkezett egy meglévő klienstől
                    try:
                        data = sock.recv(RECV_SIZE)
                        
                        if data:
                            # Adat érkezett, feldolgozzuk a kérést
                            
                            if len(data) < RECV_SIZE:
                                # Ez jelzi, hogy nem érkezett meg a teljes struct csomag,
                                # de a TCP réteg miatt ez ritka lehet, UDP-nél gyakoribb
                                print(f"Hiányos csomag a {sock.getpeername()}-tól. Elvetve.")
                                continue

                            # Kicsomagolás (4s i)
                            command_encoded, value = RECV_PACKER.unpack(data)
                            command = command_encoded.decode('utf-8').strip('\x00').upper()
                            
                            # Parancs feldolgozása és a közös érték módosítása
                            old_value = GLOBAL_VALUE
                            
                            if command == "IN  ":               # kell a 2 szóköz, mert a formátum miatt kitölti 4 byte-ra
                                GLOBAL_VALUE = value
                                print(f"👉 IN: {old_value} -> {GLOBAL_VALUE} (Új érték: {value})")
                            elif command == "INCR":
                                GLOBAL_VALUE += value
                                print(f"👉 INCR: {old_value} -> {GLOBAL_VALUE} (Növelés: {value})")
                            elif command == "DECR":
                                GLOBAL_VALUE -= value
                                print(f"👉 DECR: {old_value} -> {GLOBAL_VALUE} (Csökkentés: {value})")
                            else:
                                print(f"Ismeretlen parancs: {command} (Érték: {value})")
                                # Azért is visszaküldjük az eredeti értéket, hogy a kliens tudjon valamit kezdeni a válasszal
                            
                            # Válasz visszaküldése a kliensnek (bytesztringként)
                            response = str(GLOBAL_VALUE).encode('utf-8')
                            # A protokoll szerint csak bytesztringet küldünk vissza (nem struct)
                            sock.sendall(response)
                            print(f"Válasz elküldve a {sock.getpeername()}-nek: {response.decode()}")

                        else:
                            # Üres adat: a kliens lezárta a kapcsolatot
                            print(f"Kliens lezárta a kapcsolatot: {sock.getpeername()}")
                            sock.close()
                            inputs.remove(sock)
                            
                    except ConnectionResetError:
                        # Hirtelen megszakadt kapcsolat
                        print(f"Kapcsolat megszakadt (ConnectionResetError): {sock.getpeername()}")
                        sock.close()
                        inputs.remove(sock)
                    except Exception as e:
                        print(f"Hiba a socket feldolgozása során ({sock.getpeername()}): {e}")
                        sock.close()
                        inputs.remove(sock)

        except KeyboardInterrupt:
            print("\nSzerver leállítás...")
            break
        except Exception as e:
            print(f"Általános hiba a select hívásban: {e}")
            break
            
    # Tisztítás
    for s in inputs:
        s.close()
    print("Szerver leállítva.")

if __name__ == "__main__":
    main()