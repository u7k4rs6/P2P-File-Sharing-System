import os
from tracker.tracker import start_tracker
from peer.peer import start_peer
from client.client import start_client

if __name__ == '__main__':
    role = os.getenv('ROLE', 'tracker')
    if role == 'tracker':
        start_tracker()
    elif role == 'peer':
        start_peer()
    elif role == 'client':
        start_client()
    else:
        print('Unknown ROLE. Use tracker | peer | client')
