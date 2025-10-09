import socket, threading, os, json, hashlib
from utils.hasher import file_info_hash, read_piece
import time

TRACKER_HOST = os.getenv('TRACKER_HOST', '127.0.0.1')
TRACKER_PORT = int(os.getenv('TRACKER_PORT', '8000'))
PEER_PORT = int(os.getenv('PEER_PORT', '9001'))
SHARED_PATH = os.getenv('SHARED_PATH', 'shared')

def register_with_tracker(info_hash):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TRACKER_HOST, TRACKER_PORT))
    msg = {'type': 'register', 'info_hash': info_hash, 'port': PEER_PORT}
    s.send(json.dumps(msg).encode())
    resp = s.recv(1024).decode()
    s.close()
    print('[TRACKER RESPONSE]', resp)

def serve_peer(conn, addr):
    try:
        req = json.loads(conn.recv(1024).decode())
        if req['type'] == 'get_piece':
            path = os.path.join(SHARED_PATH, req['filename'])
            data = read_piece(path, req['index'], req['piece_size'])
            conn.send(data)
    except Exception as e:
        print('Peer error:', e)
    finally:
        conn.close()

def start_peer():
    print(f'[PEER] Listening on port {PEER_PORT}')
    for fname in os.listdir(SHARED_PATH):
        full_path = os.path.join(SHARED_PATH, fname)
        if os.path.isfile(full_path):
            info = file_info_hash(full_path)
            print(f'Registering {fname} with hash {info["info_hash"]}')
            register_with_tracker(info['info_hash'])

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', PEER_PORT))
    server.listen()
    while True:
        conn, addr = server.accept()
        threading.Thread(target=serve_peer, args=(conn, addr)).start()
