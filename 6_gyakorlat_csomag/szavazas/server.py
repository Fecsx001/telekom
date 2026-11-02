import select
import socket
import struct
import sys

votes = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
client_votes = {}

request_packer = struct.Struct("4s i")
reply_packer = struct.Struct("i")

server_addr = ("localhost", int(sys.argv[1]))


def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            return b""
        data += chunk
    return data


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(server_addr)
    sock.listen(5)
    inputs = [sock]

    try:
        while True:
            readables, _, _ = select.select(inputs, [], [], 1.0)
            for s in readables:
                if s is sock:
                    client, client_addr = sock.accept()
                    print(f"Connected: {client_addr[0]}:{client_addr[1]}")
                    inputs.append(client)
                    continue

                msg = recv_exact(s, request_packer.size)

                if not msg:
                    try:
                        peer = s.getpeername()
                        print(f"Disconnected: {peer[0]}:{peer[1]}")
                    except OSError:
                        pass
                    inputs.remove(s)
                    s.close()
                    continue

                method_raw, number = request_packer.unpack(msg)
                method = method_raw.decode("ascii", errors="replace")
                result = -2

                if method == "VOTE":
                    if number not in votes:
                        result = -2
                    elif s in client_votes:
                        result = -1
                    else:
                        votes[number] += 1
                        client_votes[s] = number
                        result = votes[number]
                elif method == "UNDO":
                    if number != 0:
                        result = -2
                    elif s not in client_votes:
                        result = -1
                    else:
                        vote_number = client_votes.pop(s)
                        votes[vote_number] -= 1
                        result = votes[vote_number]
                elif method == "STAT":
                    if number == 0:
                        result = sum(votes.values())
                    elif number in votes:
                        result = votes[number]
                    else:
                        result = -2

                s.sendall(reply_packer.pack(result))

    except KeyboardInterrupt:
        for s in inputs:
            if s is not sock:
                s.close()
        print("Server stopped")


"""
A csoport szavazással dönti el, melyik napon legyen a pót-zh. Készítsünk TCP szervert, amely a select segítségével egyszerre több szavazót is kiszolgál!

    Öt időpont közül lehet választani (1–5).
    Mindenki csak egyszer szavazhat, de a szavazatát visszavonhatja, és utána újra szavazhat.
    Egy kapcsolat = egy szavazó. Ha a szavazó bontja a kapcsolatot, a szavazata megmarad.
    Fájl és indítás: szavazas/server.py <port>

Parancs 	Jelentés 	Válasz
VOTE n 	szavazat az n. időpontra 	az n. időpont szavazatainak új száma; ha már szavazott: -1
UNDO 0 	a saját szavazat visszavonása 	annak az időpontnak a szavazatszáma a visszavonás után; ha nem szavazott: -1
STAT n 	az n. időpont szavazatainak száma; STAT 0: az összes szavazat 	a kért szám
bármi más 	hibás parancs vagy időpont 	-2
Szavazószerver – üzenetek, állapot

request_packer = struct.Struct("4s i")    # 8 byte
reply_packer = struct.Struct("i")

Kérés (kliens → szerver)
Mező 	Formátum 	Érték
parancs 	4s 	b"VOTE", b"UNDO" vagy b"STAT"
szám 	i 	időpont (1–5); STAT-nál 0 is lehet, UNDO-nál 0

Válasz (szerver → kliens)
Mező 	Formátum 	Érték
eredmény 	i 	szavazatszám, vagy -1 / -2

A szerver kétféle állapotot tart számon:

    Közös állapot: az időpontonkénti szavazatszám – minden szavazó ugyanazt látja (egy lista vagy szótár).
    Szavazónkénti állapot: ki melyik időpontra szavazott – szótár, a kulcs a kliens socketje.
    Bontáskor a szavazó bejegyzését töröljük (a socket megszűnik), de a szavazata a közös állapotban megmarad.

Szavazószerver – ellenőrzés

A szervert a tesztkliens ellenőrzi:

python tests.py check ABC123 szavazas   # mindent egyben (szavazas/server.py)
python tests.py test szavazas 10000     # kézi mód: a szerver fusson pl. a 10000-es porton

Teszt 	Mit csinál 	Mikor kapunk kódot
1. 	egy szavazó: STAT, VOTE, STAT 	ha a szavazatszám eggyel nő
2. 	öt szavazó egyszerre, majd mind bont 	ha az összes szavazat (STAT 0) öttel nő, és bontás után is megmarad
3. 	dupla szavazás és visszavonás 	ha a második VOTE -1, az UNDO után pedig újra lehet szavazni
4. 	egy parancs két részletben, szünettel 	ha a szerver a teljes 8 byte-ot megvárja (recv_exact)

A tesztek a korábbi szavazatokhoz képest ellenőriznek, így a szervert nem kell újraindítani két futtatás között. A kódokat a Moodle gyakorló kvízbe írjuk.
"""
