import socket, threading, json

registered_files = {}  # info_hash -> list of (ip, port)

def handle_client(conn, addr):
    try:
        data = conn.recv(1024).decode()
        msg = json.loads(data)
        if msg['type'] == 'register':
            info_hash = msg['info_hash']
            peer = (addr[0], msg['port'])
            registered_files.setdefault(info_hash, []).append(peer)
            conn.send(json.dumps({'status': 'registered'}).encode())
        elif msg['type'] == 'request':
            info_hash = msg['info_hash']
            peers = registered_files.get(info_hash, [])
            conn.send(json.dumps({'peers': peers}).encode())
    except Exception as e:
        print('Tracker error:', e)
    finally:
        conn.close()

def start_tracker(host='0.0.0.0', port=8000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(f'[TRACKER] Listening on {host}:{port}')
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()