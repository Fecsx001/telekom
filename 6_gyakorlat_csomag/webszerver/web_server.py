import mimetypes
import os
import select
import socket
import sys


def build_response(status_line, content_type, body):
    headers = [
        status_line,
        f"Content-Type: {content_type}",
        f"Content-Length: {len(body)}",
        "Connection: close",
        "",
        "",
    ]
    return "\r\n".join(headers).encode("ascii") + body


def safe_join(root_dir, request_path):
    raw_path = request_path.split(b"?", 1)[0].decode("utf-8", errors="replace")
    if raw_path == "/":
        raw_path = "/index.html"
    relative = raw_path.lstrip("/")
    candidate = os.path.abspath(os.path.join(root_dir, relative))
    root_abs = os.path.abspath(root_dir)
    if os.path.commonpath([candidate, root_abs]) != root_abs:
        return None
    return candidate


def make_404():
    body = b"Not Found"
    return build_response("HTTP/1.1 404 Not Found", "text/plain; charset=utf-8", body)


def handle_http_request(root_dir, request_bytes):
    first_line = request_bytes.split(b"\r\n", 1)[0]
    parts = first_line.split()
    if len(parts) < 3:
        return make_404()

    method, path, _ = parts
    if method != b"GET":
        return make_404()

    file_path = safe_join(root_dir, path)
    if file_path is None or not os.path.isfile(file_path):
        return make_404()

    with open(file_path, "rb") as f:
        body = f.read()

    mime, _ = mimetypes.guess_type(file_path)
    if mime is None:
        mime = "application/octet-stream"
    if mime.startswith("text/"):
        mime = f"{mime}; charset=utf-8"

    return build_response("HTTP/1.1 200 OK", mime, body)


def close_client(client, inputs, buffers):
    buffers.pop(client, None)
    if client in inputs:
        inputs.remove(client)
    client.close()


def main():
    if len(sys.argv) != 4:
        print(f"Usage: python {sys.argv[0]} <host> <port> <www_dir>")
        raise SystemExit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    root_dir = os.path.abspath(sys.argv[3])

    if not os.path.isdir(root_dir):
        print(f"Directory not found: {root_dir}")
        raise SystemExit(1)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(10)
        print(f"Web server listening on {host}:{port}, root={root_dir}")

        inputs = [server]
        buffers = {}

        while True:
            readables, _, _ = select.select(inputs, [], [], 1.0)
            for s in readables:
                if s is server:
                    client, addr = server.accept()
                    inputs.append(client)
                    buffers[client] = b""
                    print(f"Connected: {addr[0]}:{addr[1]}")
                    continue

                chunk = s.recv(4096)
                if not chunk:
                    close_client(s, inputs, buffers)
                    continue

                buffers[s] += chunk

                if b"\r\n\r\n" not in buffers[s]:
                    continue

                request = buffers[s]
                response = handle_http_request(root_dir, request)
                s.sendall(response)
                close_client(s, inputs, buffers)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Server stopped")
