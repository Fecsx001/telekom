import socket
import random
import struct
import json
import sys

# c) A kliens töltse be az alábbi tartalmú input.json fájlt (ezt hozzuk létre előzőleg):
#{
#"1": ["almafa", 4],
#"2": ["kortefa", 3],
#"3": ["barackfa", 5]
#}
# ezután a kliens generáljon egy véletlen számot 1 és 3 között, alakítsa át sztringgé és ezt a JSON-ben kulcsként használva
# a hozzátartozó szöveget és számot küldje majd el a szervernek!

def main_c():
    SERVER_IP = '127.0.0.1' 
    SERVER_PORT = 4000
    INPUT_FILE = "input.json"

    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data_json = json.load(f)
        
    except FileNotFoundError:
        print(f"Hiba: Az '{INPUT_FILE}' fájl nem található.")
        return
    except json.JSONDecodeError:
        print(f"Hiba: Az '{INPUT_FILE}' fájl érvénytelen JSON formátumú.")
        return

    # Véletlen szám generálása 1 és 3 között, majd sztringgé alakítás
    random_szam = random.randint(1, 3)
    key = str(random_szam) 
    
    if key not in data_json:
        print(f"Hiba: A generált kulcs ('{key}') nem található a JSON fájlban.")
        return
        
    # A JSON-ből kinyert adatok
    data_list = data_json[key]
    if len(data_list) != 2:
        print(f"Hiba: A kulcshoz ('{key}') tartozó lista nem 2 elemet tartalmaz.")
        return
        
    text = data_list[0]
    szam = data_list[1]
    
    if len(text) > 20 or not isinstance(szam, int) or szam <= 0:
        print(f"Hiba: Érvénytelen adatok a JSON-ben (szöveg hossz > 20 vagy szám nem megfelelő).")
        return

    print(f"Betöltött adatok: {data_json}")
    print(f"Kiválasztott kulcs: '{key}'")
    print(f"Elküldendő adatok: Szöveg='{text}', Szám='{szam}'")

    packer_send = struct.Struct('20s i')

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((SERVER_IP, SERVER_PORT))
            
            text_encoded = text.encode('utf-8')
            message = packer_send.pack(text_encoded, szam)
            sock.sendall(message)
            print("Adatok elküldve!")
            
            expected_length = szam
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
    main_c()