import socket
import random
import struct
import sys

# b) A kliens töltse be az alábbi tartalmú input.txt fájlt (ezt hozzuk létre előzőleg):
# almafa 4
# kortefa 3
# barackfa 5
# ezután a kliens generáljon egy véletlen számot 1 és 3 között, a számnak megfelelő sort töltse be és a sornak megfelelően küldje el
# a szervernek a szöveget és a számot!

def main():
    SERVER_IP = '127.0.0.1' 
    SERVER_PORT = 4000 
    INPUT_FILE = "input.txt"

    data = []
    try:
        with open(INPUT_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    text = parts[0]
                    szam = int(parts[1])
                    if len(text) <= 20 and szam > 0:
                        data.append((text, szam))
        
        if not data:
            print(f"Hiba: Az '{INPUT_FILE}' fájl üres, vagy nem tartalmaz érvényes adatot.")
            return

    except FileNotFoundError:
        print(f"Hiba: Az '{INPUT_FILE}' fájl nem található.")
        return
    except ValueError:
        print(f"Hiba: Az '{INPUT_FILE}' fájl formátuma hibás (a szám nem egész szám).")
        return
    
    # Véletlen sorszám generálása 1 és a sorok száma között
    random_index = random.randint(0, len(data) - 1)
    
    text, szam = data[random_index]
    
    print(f"Betöltött adatok: {data}")
    print(f"Kiválasztott sorszám: {random_index + 1}. sor (index: {random_index})")
    print(f"Elküldendő adatok: Szöveg='{text}', Szám='{szam}'")

    packer = struct.Struct('20s i')
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((SERVER_IP, SERVER_PORT))
            
            # Csomagolás és küldés
            text_encoded = text.encode('utf-8')
            message = packer.pack(text_encoded, szam)
            sock.sendall(message)
            print("Adatok elküldve!")
            
            # Válasz fogadása (méret: min(len(text), szam))
            expected_length = szam
            
            # if expected_length <= 0: return

            response_message = sock.recv(expected_length)
            
            if len(response_message) == 0: return
            
            packer_recv = struct.Struct(f'{expected_length}s')
            (reversed_text_encoded, ) = packer_recv.unpack(response_message)
            reversed_text = reversed_text_encoded.decode('utf-8')
            
            print(f"Kapott válasz (Levágott és megfordított {expected_length} karakter): {reversed_text}")
            
    except ConnectionRefusedError:
        print("Hiba: Nem sikerült kapcsolódni a szerverhez.")
    except Exception as e:
        print(f"Hiba történt: {e}")

if __name__ == "__main__":
    main()