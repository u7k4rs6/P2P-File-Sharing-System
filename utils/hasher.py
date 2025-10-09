import hashlib, os

def file_info_hash(path, piece_size=16384):
    size = os.path.getsize(path)
    h = hashlib.sha1()
    with open(path, 'rb') as f:
        while chunk := f.read(piece_size):
            h.update(hashlib.sha1(chunk).digest())
    return {'info_hash': h.hexdigest(), 'size': size, 'piece_size': piece_size}

def read_piece(path, index, piece_size):
    with open(path, 'rb') as f:
        f.seek(index * piece_size)
        return f.read(piece_size)

def write_piece(path, index, data, piece_size):
    with open(path, 'r+b') as f:
        f.seek(index * piece_size)
        f.write(data)
