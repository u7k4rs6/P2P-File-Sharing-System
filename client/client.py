import socket, threading, json, os
from utils.hasher import write_piece

TRACKER_HOST = os.getenv('TRACKER_HOST', '127.0.0.1')
TRACKER_PORT = int(os.getenv('TRACKER_PORT', '8000'))
DOWNLOAD_PATH = os.getenv('DOWNLOAD_PATH', 'downloads')
PIECE_SIZE = 16384

os.makedirs(DOWNLOAD_PATH, exist_ok=True)

def get_peers(info_hash):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TRACKER_HOST, TRACKER_PORT))
    s.send(json.dumps({'type': 'request', 'info_hash': info_hash}).encode())
    peers = json.loads(s.recv(2048).decode())['peers']
    s.close()
    return peers

def download_piece(peer, filename, index, piece_size, outpath):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(tuple(peer))
        req = {'type': 'get_piece', 'filename': filename, 'index': index, 'piece_size': piece_size}
        s.send(json.dumps(req).encode())
        data = b''
        while True:
            chunk = s.recv(4096)
            if not chunk: break
            data += chunk
        write_piece(outpath, index, data, piece_size)
    except Exception as e:
        print('Error downloading piece:', e)
    finally:
        s.close()

def start_client():
    info_hash = input('Enter info_hash to download: ').strip()
    filename = input('Enter filename: ').strip()
    peers = get_peers(info_hash)
    if not peers:
        print('No peers found for this file.')
        return
    size = int(input('Enter total file size in bytes: '))
    pieces = (size + PIECE_SIZE - 1) // PIECE_SIZE
    outpath = os.path.join(DOWNLOAD_PATH, filename)
    open(outpath, 'wb').truncate(size)
    threads = []
    for i in range(pieces):
        peer = peers[i % len(peers)]
        t = threading.Thread(target=download_piece, args=(peer, filename, i, PIECE_SIZE, outpath))
        t.start()
        threads.append(t)
    for t in threads: t.join()
    print('Download complete ->', outpath)
