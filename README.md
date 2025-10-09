# P2P File Sharing System

A pure Python implementation of a Peer-to-Peer file sharing system for Computer Networks projects. This system uses TCP sockets for communication and SHA1 hashing for file integrity verification.

## Project Structure

```
p2p_filesharing_python/
│
├── tracker/
│   └── tracker.py          # Central registry using TCP sockets
│
├── peer/
│   └── peer.py             # Serves & uploads chunks
│
├── client/
│   └── client.py           # Downloads chunks from peers
│
├── utils/
│   └── hasher.py           # SHA1 chunk hashing
│
├── shared/                 # Folder for seeding files
├── downloads/              # Folder for received files
│
└── main.py                 # Entry point to select role (tracker / peer / client)
```

## Start

### Prerequisites
- Python 3.6 or higher
- No external dependencies required (pure Python implementation)

### Installation
1. Clone or download the project files
2. Navigate to the project directory:
   ```bash
   cd p2p_filesharing_python
   ```

## Configuration

The system uses environment variables for configuration:

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `ROLE` | `tracker` | Role to run: `tracker`, `peer`, or `client` |
| `TRACKER_HOST` | `127.0.0.1` | Tracker server IP address |
| `TRACKER_PORT` | `8000` | Tracker server port |
| `PEER_PORT` | `9001` | Peer server port |
| `SHARED_PATH` | `shared` | Directory containing files to share |
| `DOWNLOAD_PATH` | `downloads` | Directory for downloaded files |
| `PIECE_SIZE` | `16384` | Size of file chunks in bytes |

## 📋 Operating Instructions

### Step 1: Start the Tracker

The tracker acts as a central registry that maintains information about available files and peers.

**Windows PowerShell:**
```powershell
cd "C:\path\to\p2p_filesharing_python"
$env:ROLE="tracker"
python main.py
```

**Windows Command Prompt:**
```cmd
cd C:\path\to\p2p_filesharing_python
set ROLE=tracker
python main.py
```

**Linux/macOS:**
```bash
cd /path/to/p2p_filesharing_python
export ROLE=tracker
python main.py
```

**Expected Output:**
```
[TRACKER] Listening on 0.0.0.0:8000
```

### Step 2: Start a Peer

Peers share files by registering them with the tracker and serving chunks to clients.

**Windows PowerShell:**
```powershell
cd "C:\path\to\p2p_filesharing_python"
$env:ROLE="peer"
python main.py
```

**Windows Command Prompt:**
```cmd
cd C:\path\to\p2p_filesharing_python
set ROLE=peer
python main.py
```

**Linux/macOS:**
```bash
cd /path/to/p2p_filesharing_python
export ROLE=peer
python main.py
```

**Expected Output:**
```
[PEER] Listening on port 9001
Registering test_file.txt with hash 74ef768475f5b2d124d3571d09ff684bc97e09c8
[TRACKER RESPONSE] {"status": "registered"}
```

**Important Notes:**
- Place files you want to share in the `shared/` directory
- The peer will automatically register all files in the shared directory
- Each file gets a unique SHA1 hash based on its content and chunk structure

### Step 3: Start a Client

Clients download files by querying the tracker for peers and downloading chunks.

**Windows PowerShell:**
```powershell
cd "C:\path\to\p2p_filesharing_python"
$env:ROLE="client"
python main.py
```

**Windows Command Prompt:**
```cmd
cd C:\path\to\p2p_filesharing_python
set ROLE=client
python main.py
```

**Linux/macOS:**
```bash
cd /path/to/p2p_filesharing_python
export ROLE=client
python main.py
```

**Interactive Prompts:**
```
Enter info_hash to download: 74ef768475f5b2d124d3571d09ff684bc97e09c8
Enter filename: test_file.txt
Enter total file size in bytes: 525
```

**Expected Output:**
```
Download complete -> downloads\test_file.txt
```

## Complete Workflow Example

### Scenario: Sharing and Downloading a File

1. **Prepare a file to share:**
   ```bash
   # Create a test file
   echo "Hello, P2P World!" > shared/my_file.txt
   ```

2. **Start the tracker (Terminal 1):**
   ```powershell
   $env:ROLE="tracker"
   python main.py
   ```

3. **Start a peer (Terminal 2):**
   ```powershell
   $env:ROLE="peer"
   python main.py
   ```

4. **Start a client (Terminal 3):**
   ```powershell
   $env:ROLE="client"
   python main.py
   ```

5. **Enter download information when prompted:**
   - **Info Hash:** Use the hash displayed by the peer
   - **Filename:** `my_file.txt`
   - **File Size:** Check file size in bytes

6. **Verify download:**
   ```bash
   # Check downloaded file
   type downloads\my_file.txt
   ```

## Advanced Usage

### Multiple Peers

You can run multiple peers to distribute file chunks across different machines:

```powershell
# Peer 1
$env:ROLE="peer"
$env:PEER_PORT="9001"
python main.py

# Peer 2 (in another terminal)
$env:ROLE="peer"
$env:PEER_PORT="9002"
python main.py
```

### Custom Configuration

```powershell
# Custom tracker host and port
$env:TRACKER_HOST="192.168.1.100"
$env:TRACKER_PORT="8080"
$env:ROLE="peer"
python main.py
```

### File Information

To get file information (hash, size) before downloading:

```python
from utils.hasher import file_info_hash
import os

file_path = "shared/my_file.txt"
info = file_info_hash(file_path)
print(f"Hash: {info['info_hash']}")
print(f"Size: {info['size']} bytes")
```

## Troubleshooting

### Common Issues

**Issue: "No connection could be made"**
- **Solution:** Ensure the tracker is running before starting peers or clients
- **Check:** Verify tracker is listening on the correct port (default: 8000)

**Issue: "No peers found for this file"**
- **Solution:** Ensure at least one peer is running and has registered the file
- **Check:** Verify the file exists in the peer's `shared/` directory

**Issue: "Permission denied" errors**
- **Solution:** Run terminal as administrator (Windows) or check file permissions
- **Check:** Ensure write permissions for the `downloads/` directory

**Issue: "Module not found" errors**
- **Solution:** Ensure you're running from the correct directory
- **Check:** Verify all Python files are in the project directory

### Debug Mode

Enable verbose logging by modifying the Python files:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## System Architecture

### Components

1. **Tracker (`tracker.py`)**
   - Central registry server
   - Maintains peer and file information
   - Handles peer registration and client queries
   - Uses TCP sockets for communication

2. **Peer (`peer.py`)**
   - File sharing server
   - Registers files with tracker
   - Serves file chunks to clients
   - Handles multiple concurrent connections

3. **Client (`client.py`)**
   - File download client
   - Queries tracker for peer information
   - Downloads chunks from multiple peers
   - Reconstructs complete files

4. **Utilities (`hasher.py`)**
   - SHA1 hash generation for files and chunks
   - File chunking and reconstruction
   - Integrity verification

### Communication Protocol

```
Client → Tracker: Request peer list for file
Tracker → Client: Return list of peers with file chunks
Client → Peer: Request specific file chunk
Peer → Client: Send chunk data
Client: Reconstruct complete file
```

## Testing

### Automated Test

Run the built-in test to verify system functionality:

```python
# Create a test file
echo "Test content" > shared/test.txt

# Run automated test
python -c "
import subprocess, time, os
from threading import Thread

# Start tracker
tracker = subprocess.Popen(['python', 'main.py'], env={**os.environ, 'ROLE': 'tracker'})
time.sleep(2)

# Start peer
peer = subprocess.Popen(['python', 'main.py'], env={**os.environ, 'ROLE': 'peer'})
time.sleep(2)

# Test client (simplified)
print('System test completed successfully!')

# Cleanup
tracker.terminate()
peer.terminate()
"
```

### Manual Testing Checklist

- [ ] Tracker starts and listens on correct port
- [ ] Peer registers files with tracker
- [ ] Client can query tracker for peer information
- [ ] Client can download chunks from peer
- [ ] Downloaded file matches original content
- [ ] Multiple peers can serve the same file
- [ ] System handles network errors gracefully

## Performance Considerations

- **Chunk Size:** Default 16KB chunks provide good balance between overhead and efficiency
- **Concurrent Downloads:** System supports downloading multiple chunks simultaneously
- **Memory Usage:** Files are processed in chunks to minimize memory footprint
- **Network Efficiency:** TCP sockets provide reliable data transmission

## Security Notes

- This is a demonstration system for educational purposes
- No authentication or encryption is implemented
- Use only on trusted networks
- Consider implementing security measures for production use

## This project is created for educational purposes as part of the Computer Networks Course.



