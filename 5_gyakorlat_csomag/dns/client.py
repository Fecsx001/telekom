import socket
import struct
import sys


def recv_exact(sock: socket.socket, size):
	data = b""
	while len(data) < size:
		chunk = sock.recv(size - len(data))
		if not chunk:
			raise ConnectionError("A kapcsolat megszakadt olvasas kozben.")
		data += chunk
	return data


def encode_qname(hostname):
	labels = hostname.strip(".").split(".")
	qname = b""
	for label in labels:
		encoded = label.encode("ascii")
		qname += struct.pack("!B", len(encoded)) + encoded
	return qname + b"\x00"


def decode_qname(msg, offset):
	labels = []
	jumped = False
	original_offset = offset

	while True:
		length = msg[offset]
		if length == 0:
			offset += 1
			break

		if length & 0xC0 == 0xC0:
			pointer = struct.unpack("!H", msg[offset : offset + 2])[0] & 0x3FFF
			if not jumped:
				original_offset = offset + 2
			offset = pointer
			jumped = True
			continue

		offset += 1
		labels.append(msg[offset : offset + length].decode("ascii", errors="replace"))
		offset += length

	if jumped:
		return ".".join(labels), original_offset
	return ".".join(labels), offset


def build_query(hostname):
	txid = 0x1234
	flags = 0x0100  # standard query, recursion desired
	qdcount = 1
	ancount = 0
	nscount = 0
	arcount = 0

	header = struct.pack("!HHHHHH", txid, flags, qdcount, ancount, nscount, arcount)
	question = encode_qname(hostname) + struct.pack("!HH", 1, 1)  # QTYPE=A, QCLASS=IN
	message = header + question
	return struct.pack("!H", len(message)) + message


def parse_response(resp, expected_txid):
	txid, flags, qdcount, ancount, nscount, arcount = struct.unpack("!HHHHHH", resp[:12])
	if txid != expected_txid:
		raise ValueError("Nem egyezo tranzakcio azonosito.")

	rcode = flags & 0x000F
	if rcode != 0:
		raise ValueError(f"DNS hiba kod: {rcode}")

	offset = 12
	for _ in range(qdcount):
		_, offset = decode_qname(resp, offset)
		offset += 4  # QTYPE + QCLASS

	for _ in range(ancount):
		_, offset = decode_qname(resp, offset)
		rtype, rclass, _, rdlength = struct.unpack("!HHIH", resp[offset : offset + 10])
		offset += 10
		rdata = resp[offset : offset + rdlength]
		offset += rdlength

		if rtype == 1 and rclass == 1 and rdlength == 4:
			return ".".join(str(b) for b in rdata)

	raise ValueError("A valaszban nincs IPv4 (A) rekord.")


def main():
	if len(sys.argv) != 4:
		print(f"Hasznalat: python {sys.argv[0]} <host> <port> <nev>", file=sys.stderr)
		raise SystemExit(1)

	host = sys.argv[1]
	port = int(sys.argv[2])
	name = sys.argv[3]

	query = build_query(name)

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
		sock.connect((host, port))
		sock.sendall(query)

		resp_len = struct.unpack("!H", recv_exact(sock, 2))[0]
		response = recv_exact(sock, resp_len)

	ip = parse_response(response, expected_txid=0x1234)
	print(ip)


if __name__ == "__main__":
	main()

