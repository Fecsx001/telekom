import socket
import struct
import sys

def send_command(command_str, value):
    SERVER_IP = '127.0.0.1' 
    SERVER_PORT = 5000 
    
    # Adat csomagolása
    FORMAT_SEND = '4s i'
    packer = struct.Struct(FORMAT_SEND)
    
    # Fontos: A parancsot pontosan 4 bájtra kell kódolni.
    command_bytes = command_str.upper().ljust(4).encode('utf-8')
    message = packer.pack(command_bytes, value)
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((SERVER_IP, SERVER_PORT))
            print(f"Küldés: {command_str}, {value} (Csomag mérete: {len(message)})")
            
            sock.sendall(message)
            
            # Válasz fogadása (bytesztring)
            response = sock.recv(1024)
            if response:
                print(f"Válasz a szervertől: {response.decode('utf-8')}")
            else:
                print("A szerver nem küldött választ.")
                
    except ConnectionRefusedError:
        print("Hiba: Nem sikerült kapcsolódni a szerverhez.")
    except Exception as e:
        print(f"Hiba történt: {e}")

if __name__ == "__main__":
    send_command("IN", 20)
    send_command("INCR", 4)
    send_command("INCR", 50)
    send_command("DECR", 25)