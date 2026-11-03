import socket
import sys
import select
import struct

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = sys.argv[1]
port = int(sys.argv[2])

server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((ip, port))
server.listen(5)

inputs = [server]
timeout = 1.0

grades = {
    'NET101': {"ABC123": 5.0,
            "CBA321": 5.0},
    'NET102': {"ABC123": 4.0,
            "CBA321": 4.5}
}
    
packer = struct.Struct('3s 6s 6s f')

while True:
    #try:
    rlist, wlist, xlist = select.select(inputs, [], [], timeout)
    
    for s in rlist:
        if s is server:
            conn, client_addr = s.accept()      # socket és a címe (ip, port)
            inputs.append(conn)
        else:
            #try:
            data = s.recv(packer.size)
            if data:
                command, subj, n_code, grade = packer.unpack(data)
                cmd = command.decode('utf-8').strip('\x00').upper()
                subj = subj.decode('utf-8').strip('\x00').upper()
                neptun = n_code.decode('utf-8').strip('\x00').upper()
                
                return_value = 0.0
                if subj not in grades:
                    grades[subj] = {}
                if cmd == "INS":
                    grades[subj][neptun] = grade
                    return_value = grade
                
                elif cmd == "GET":
                    return_value = grades[subj].get(neptun, 0.0)
                
                elif cmd == "AVG":
                    subject_grades = grades[subj].values()
                    if len(subject_grades) > 0:
                        return_value = sum(subject_grades) / len(subject_grades)
                    else:
                        return_value = 0.0
                
                reply_packer = struct.Struct('f')
                reply = reply_packer.pack(return_value)
                s.sendall(reply)
            else:
                print(f"Kliens lezárta a kapcsolatot: {s.getpeername()}")
                s.close()
                inputs.remove(s)
                    
            #except ConnectionResetError:
            #        print(f"Kapcsolat megszakadt (ConnectionResetError): {s.getpeername()}")
            #        s.close()
            #        inputs.remove(s)
            #except Exception as e:
            #        print(f"Hiba a socket feldolgozása során ({s.getpeername()}): {e}")
            #        s.close()
            #        inputs.remove(s)               
    #except KeyboardInterrupt:
    #        print("\nSzerver leállítás...")
    #        break
    #except Exception as e:
    #        print(f"Általános hiba a select hívásban: {e}")
    #        break
# Tisztítás
#for s in inputs:
#    s.close()
#print("Szerver leállítva.")