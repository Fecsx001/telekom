import socket
import random
import struct
import sys

# A kliens egy szöveget és egy számot küld a szervernek struct segítségével (20s i) (változatok lent).
# A szerver a szám alapján levág a szöveg elejéről X darab karaktert és megfordítja, amit visszaküld a kliensnek.
# Itt a formátum a kapott számérték alapján legyen (Xs).
# Példa:
# almafa,4 -> amla
# kortefa,3 -> rok

# a) A kliens a felhasználótól kérje be a szöveget, valamint generáljon egy véletlen számot!

def main():

    SERVER_IP = 'localhost' # megadottra módosítani kell majd!
    SERVER_PORT = 4000 

    text = input("Adj meg egy szöveget: ")
    if len(text) == 0:
        print("Hiba: A szöveg nem lehet üres!")
        return

    if len(text) > 20:
        print("Hiba: A szöveg maximum 20 karakter lehet!")
        return

    # number = random.random()  # véletlen lebegőpontos szám 0.0 és 1.0 között
    # Véletlen egész szám két határ között (mindkét végpont benne van)
    szam = random.randint(1, len(text))

    # Véletlen lebegőpontos szám két határ között
    # szam = random.uniform(1.5, 10.5)

    # Véletlen egész szám egy tartományból (felső határ nincs benne)
    # szam = random.randrange(0, 100)  # 0-tól 99-ig
    # szam = random.randrange(0, 100, 5)  # 0-tól 99-ig, 5-ös lépésközzel
    # véletlen elem kiválasztásához listából
    # szam = random.choice(lista)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((SERVER_IP, SERVER_PORT))
            print("Kapcsolat létrejött!")
            # csomagolás
            packer = struct.Struct(f'20s i')

            text_bytes = text.encode()   # Kitölti a szöveget nullákkal a rögzített méretre
            message = packer.pack(text_bytes, szam)
            print(f"\nCsomagolt adat mérete: {len(message)} byte")
            
            sock.sendall(message)
            print("Adatok elküldve!")
            
            expected_length = szam
            # if expected_length <= 0:
            #     print("Figyelem: A levágandó karakterek száma miatt a szerver nem küld vissza szöveget.")
            #     return

            response_message = sock.recv(expected_length)
            if len(response_message) == 0:
                print("A szerver lezárta a kapcsolatot.")
                return
            if len(response_message) < expected_length:
                print(f"Figyelem: Kevesebb adat érkezett, mint vártuk ({len(response_message)} bájt).")
            
            # válasz kicsomagolása
            # A válasz formátuma: Xs, ahol X = szam
            packer_recv = struct.Struct(f'{szam}s')
            (reversed_text_bytes, ) = packer_recv.unpack(response_message)
            reversed_text = reversed_text_bytes.decode()
            print(f"\nKapott válasz a szervertől: {reversed_text}")
        except ConnectionRefusedError:
            print("Hiba: Nem sikerült kapcsolódni a szerverhez. Biztos fut a szerver?")
        except socket.timeout:
            print("Hiba: Időtúllépés - a szerver nem válaszolt időben.")
        except Exception as e:
            print(f"Hiba történt: {e}")

if __name__ == "__main__":
    main()