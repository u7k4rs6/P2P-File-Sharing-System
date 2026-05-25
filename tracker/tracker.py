import socket, threading, json

registered_files = {}  # info_hash -> list of (ip, port)
lock = threading.Lock()

def recv_all(conn):
    data = b''
    while True:
        chunk = conn.recv(4096)
        if not chunk:
            break
        data += chunk
        try:
            json.loads(data.decode())
            break
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
    return data.decode()

def handle_client(conn, addr):
    try:
        data = recv_all(conn)
        msg = json.loads(data)
        if msg['type'] == 'register':
            info_hash = msg['info_hash']
            peer = (addr[0], msg['port'])
            with lock:
                peers = registered_files.setdefault(info_hash, [])
                if peer not in peers:
                    peers.append(peer)
            conn.send(json.dumps({'status': 'registered'}).encode())
        elif msg['type'] == 'request':
            info_hash = msg['info_hash']
            with lock:
                peers = list(registered_files.get(info_hash, []))
            conn.send(json.dumps({'peers': peers}).encode())
    except Exception as e:
        print('Tracker error:', e)
    finally:
        conn.close()

def start_tracker(host='0.0.0.0', port=8000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen()
    print(f'[TRACKER] Listening on {host}:{port}')
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()