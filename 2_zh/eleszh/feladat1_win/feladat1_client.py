import socket
import struct
import sys

server_host = sys.argv[1]
server_ip = int(sys.argv[2])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    
    packer = struct.Struct('6s 13s 6s')         
    unpacker = struct.Struct('i i')             # van/nincs (1/0) és kölcsönzési idő
    client.connect((server_host, server_ip))

    NEPTUN_code = "E2FDGV"
    ISBN = "9780679760801"
    MSG_type = "submit"
    
    NEPTUN_code_encoded = NEPTUN_code.encode()
    ISBN_encoded = ISBN.encode()
    MSG_type_encoded = MSG_type.encode()

    msg = packer.pack(NEPTUN_code.encode(), ISBN.encode(), MSG_type.encode())
    client.sendall(msg)
    
    reply = client.recv(unpacker.size)
    y_n, days = unpacker.unpack(reply)
    
    if y_n == 0:
        reply_to_server = packer.pack(NEPTUN_code_encoded, ISBN_encoded, b"cancel")
        client.sendall(reply_to_server)
    else:
        if days >= 21:
            reply_to_server = packer.pack(NEPTUN_code_encoded, ISBN_encoded, b"borrow")
            client.sendall(reply_to_server)
        else:
            reply_to_server = packer.pack(NEPTUN_code_encoded, ISBN_encoded, b"extend")
            client.sendall(reply_to_server)
    
            reply_unpacker = struct.Struct('i i')
            reply = client.recv(reply_unpacker.size)
            
            deny_or_not, new_days = reply_unpacker.unpack(reply)      # elutas/elfog és új kölcsönzési idő
            
            if deny_or_not == 1 and new_days >= 21:
                reply_to_server = packer.pack(NEPTUN_code_encoded, ISBN_encoded, b"borrow")
                client.sendall(reply_to_server)               
                
            else:
                reply_to_server = packer.pack(NEPTUN_code_encoded, ISBN_encoded, b"cancel")
                client.sendall(reply_to_server)
                
    final_reply_unpacker = struct.Struct('12s')
    final_reply = client.recv(final_reply_unpacker.size)
                
    final_identifier = final_reply_unpacker.unpack(final_reply)[0]              # a struct unpack-je mindig tuple-el tér vissza (akkor is, ha egy elemű), 
                                                                                # nekünk annak az első eleme kell most --> [0]
    final_identifier_decoded = final_identifier.strip(b'\x00').decode('utf-8')  # a tuple maradt volna, itt nem működne a strip
                
    print(f'Kölcsönzési azonosító:{final_identifier_decoded}')                  # ez volt: g8h1j4k6l2m9
                