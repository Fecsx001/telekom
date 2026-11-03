import socket
import struct
import sys

def send_udp_command(command_str, value):
    SERVER_IP = '127.0.0.1' 
    SERVER_PORT = 5000
    
    # Adat csomagolása
    COMMAND_MAX_LEN = 5
    FORMAT_SEND = f'{COMMAND_MAX_LEN}s i'
    PACKER_SEND = struct.Struct(FORMAT_SEND)
    
    # Válasz kicsomagolása (i)
    FORMAT_RECV = 'i'
    PACKER_RECV = struct.Struct(FORMAT_RECV)
    
    # Fontos: A parancsot pontosan 5 bájtra kell kódolni.
    command_bytes = command_str.upper().ljust(COMMAND_MAX_LEN).encode('utf-8')
    message = PACKER_SEND.pack(command_bytes, value)
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            # Rövid timeout beállítása, ha a szerver nem válaszol
            sock.settimeout(20.0) 
            
            print(f"Küldés: {command_str}, {value} (Csomag mérete: {len(message)})")
            
            # Küldés a szerver címére (sendto)
            sock.sendto(message, (SERVER_IP, SERVER_PORT))
            
            # Válasz fogadása (recvfrom)
            # A várt válasz mérete: a struct 'i' mérete (általában 4 bájt)
            response, server_addr = sock.recvfrom(PACKER_RECV.size)
            
            if response:
                # Kicsomagolás (i)
                (current_value,) = PACKER_RECV.unpack(response) # az addr-re nem vagyunk kíváncsiak, így a vessző után nem írunk semmit
                print(f"Válasz a szervertől ({server_addr}): Módosított érték = {current_value}")
            else:
                print("A szerver nem küldött választ.")
                
    except socket.timeout:
        print("Időtúllépés: A szerver nem válaszolt.")
    except Exception as e:
        print(f"Hiba történt: {e}")

if __name__ == "__main__":    
    # PUSH 20 -> Beállítja 20-ra (kezdeti érték 0 volt)
    send_udp_command("PUSH", 20)
    # PLUS 4 -> Növeli 4-gyel (20+4=24)
    send_udp_command("PLUS", 4)
    # MINUS 5 -> Csökkenti 5-tel (24-5=19)
    send_udp_command("MINUS", 5)
    # PLUS 100 -> Növeli 100-zal (19+100=119)
    send_udp_command("PLUS", 100)