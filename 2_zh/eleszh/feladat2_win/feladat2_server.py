import socket
import sys
import select
import struct

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = sys.argv[1]
port = int(sys.argv[2])

server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)        # több kliens
server.bind((ip, port))
server.listen(5)

inputs = [server]
timeout = 1.0

# matrix = []                       # üres mátrix
# for i in range(3):
#     row = []
#     for j in range(3):
#         row.append(0)
#     matrix.append(row)            # 0-kal inicializált mátrix
        
matrix = [[0,0,0],[0,0,0],[0,0,0]]
    
packer = struct.Struct('3s i i i')

while True:
    try:
        rlist, wlist, xlist = select.select(inputs, [], [], timeout)
        
        for s in rlist:
            if s is server:
                conn, client_addr = s.accept()      # socket és a címe (ip, port)
                inputs.append(conn)
            else:
                try:
                    data = s.recv(packer.size)
                    if data:
                        command, fst, scd, thrd = packer.unpack(data)
                        command_decoded = command.decode('utf-8').strip('\x00').upper()

                        if command_decoded == "SET":
                            matrix[fst][scd] = thrd
                            return_value = thrd
                        elif command_decoded == "GET":
                            return_value = matrix[fst][scd]
                        elif command_decoded == "SUM":
                            return_value = 0
                            for i in range(3):
                                for j in range(3):
                                    return_value += matrix[i][j]
                        else:
                            print(f"Ismeretlen parancs: {command_decoded}")
                        
                        reply_packer = struct.Struct('i')
                        packed_reply = reply_packer.pack(return_value)
                        s.sendall(packed_reply)
                    else:
                        print(f"Kliens lezárta a kapcsolatot: {s.getpeername()}")
                        s.close()
                        inputs.remove(s)
                        
                except ConnectionResetError:
                        print(f"Kapcsolat megszakadt (ConnectionResetError): {s.getpeername()}")
                        s.close()
                        inputs.remove(s)
                except Exception as e:
                        print(f"Hiba a socket feldolgozása során ({s.getpeername()}): {e}")
                        s.close()
                        inputs.remove(s)               
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

# kapott válaszok:
# Test1: F8r2b6G0zQ4x
# Test2: p5J1m9V3nT7c
# Test3: R2d8k4S6yL0h