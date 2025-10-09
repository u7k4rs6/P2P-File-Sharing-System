# Multi-Threaded HTTP Server

A pure Python implementation of a multi-threaded HTTP server using low-level TCP socket programming. This server supports GET and POST requests with comprehensive security features, thread pool management, and detailed logging.

## Project Structure

```
p2p_filesharing_python/
│
├── http_server.py          # Main HTTP server implementation
├── test_client.py          # Test client for server validation
├── sample.json             # Sample JSON for POST testing
├── create_jpeg.py          # Utility to create test JPEG file
├── resources/              # Directory for serving files
│   ├── index.html          # Main HTML test page
│   ├── test.txt            # Sample text file
│   ├── test.png            # Sample PNG image
│   ├── test.jpg            # Sample JPEG image
│   └── uploads/            # Directory for POST uploads
├── README.md               # This documentation
└── QUICK_REFERENCE.md      # Quick command reference
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

The server accepts command-line arguments for configuration:

| Argument | Default Value | Description |
|----------|---------------|-------------|
| `--host` | `127.0.0.1` | Server host address |
| `--port` | `8080` | Server port number |
| `--max-threads` | `10` | Maximum thread pool size |

## Operating Instructions

### Step 1: Start the HTTP Server

**Windows PowerShell:**
```powershell
cd "C:\path\to\p2p_filesharing_python"
python http_server.py --host 127.0.0.1 --port 8080 --max-threads 10
```

**Windows Command Prompt:**
```cmd
cd C:\path\to\p2p_filesharing_python
python http_server.py --host 127.0.0.1 --port 8080 --max-threads 10
```

**Linux/macOS:**
```bash
cd /path/to/p2p_filesharing_python
python http_server.py --host 127.0.0.1 --port 8080 --max-threads 10
```

**Expected Output:**
```
[2025-01-10 12:00:00] [INFO] HTTP Server initialized: 127.0.0.1:8080, max_threads=10
[2025-01-10 12:00:00] [INFO] Server started on 127.0.0.1:8080
[2025-01-10 12:00:00] [INFO] Thread pool started with 10 threads
```

### Step 2: Test the Server

#### Using the Test Client
```bash
python test_client.py
```

#### Using curl Commands

**Test GET Request (HTML):**
```bash
curl -H "Host: 127.0.0.1:8080" http://127.0.0.1:8080/
```

**Test GET Request (Text File):**
```bash
curl -H "Host: 127.0.0.1:8080" http://127.0.0.1:8080/test.txt
```

**Test GET Request (PNG Image):**
```bash
curl -H "Host: 127.0.0.1:8080" http://127.0.0.1:8080/test.png -o downloaded.png
```

**Test POST Request (JSON Upload):**
```bash
curl -X POST -H "Content-Type: application/json" -H "Host: 127.0.0.1:8080" -d '{"test": "data"}' http://127.0.0.1:8080/
```

#### Using Web Browser
Open your browser and navigate to: `http://127.0.0.1:8080/`

## Workflow Example

### Scenario: Testing All Server Features

1. **Start the server:**
   ```bash
   python http_server.py --host 127.0.0.1 --port 8080 --max-threads 10
   ```

2. **Test HTML serving:**
   ```bash
   curl -H "Host: 127.0.0.1:8080" http://127.0.0.1:8080/
   ```

3. **Test file downloads:**
   ```bash
   curl -H "Host: 127.0.0.1:8080" http://127.0.0.1:8080/test.txt
   curl -H "Host: 127.0.0.1:8080" http://127.0.0.1:8080/test.png -o test.png
   ```

4. **Test JSON upload:**
   ```bash
   curl -X POST -H "Content-Type: application/json" -H "Host: 127.0.0.1:8080" -d @sample.json http://127.0.0.1:8080/
   ```

5. **Test security features:**
   ```bash
   curl -H "Host: 127.0.0.1:8080" http://127.0.0.1:8080/../etc/passwd
   ```

## Advanced Usage

### Custom Configuration

```bash
# Custom host and port
python http_server.py --host 0.0.0.0 --port 9000 --max-threads 20

# High-performance configuration
python http_server.py --host 127.0.0.1 --port 8080 --max-threads 50
```

### Load Testing

```python
import requests
import threading
import time

def make_request():
    response = requests.get('http://127.0.0.1:8080/test.txt', 
                          headers={'Host': '127.0.0.1:8080'})
    return response.status_code == 200

# Test with 100 concurrent requests
threads = []
for i in range(100):
    t = threading.Thread(target=make_request)
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

## Troubleshooting

### Common Issues

**Issue: "Address already in use"**
- **Solution:** Change the port or stop the existing server
- **Check:** `netstat -an | findstr :8080` (Windows) or `lsof -i :8080` (Linux/macOS)

**Issue: "Connection refused"**
- **Solution:** Ensure the server is running and accessible
- **Check:** Verify host and port configuration

**Issue: "Permission denied" errors**
- **Solution:** Run terminal as administrator (Windows) or check file permissions
- **Check:** Ensure write permissions for the `resources/uploads/` directory

**Issue: "Module not found" errors**
- **Solution:** Ensure you're running from the correct directory
- **Check:** Verify all Python files are in the project directory

### Debug Mode

Enable verbose logging by modifying the server code:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## System Architecture

### Components

1. **HTTPRequest Class**
   - Parses incoming HTTP requests
   - Extracts method, path, headers, and body
   - Validates request format

2. **HTTPResponse Class**
   - Constructs HTTP responses
   - Handles different content types
   - Manages headers and status codes

3. **HTTPServer Class**
   - Main server implementation
   - Manages thread pool and connection queue
   - Handles client connections and request processing

4. **Thread Pool Management**
   - Configurable thread pool size
   - Connection queue for handling high load
   - Thread-safe operations with mutexes

### Communication Protocol

```
Client → Server: HTTP Request (GET/POST)
Server → Client: HTTP Response with appropriate status
Server: Logs all activities with timestamps
Server: Manages persistent connections with timeouts
```

## Testing

### Automated Test Suite

Run the comprehensive test suite:

```bash
python test_client.py
```

**Test Coverage:**
- GET requests for HTML, TXT, PNG, JPG files
- POST requests with JSON data
- Path traversal protection
- Method validation (405 for unsupported methods)
- Content type validation (415 for invalid types)
- Concurrent request handling
- Host header validation
- Keep-alive connections

### Manual Testing Checklist

- [ ] Server starts and listens on correct port
- [ ] HTML files served with correct Content-Type
- [ ] Binary files (PNG, JPG) served with Content-Disposition
- [ ] Text files served with proper encoding
- [ ] JSON uploads create timestamped files
- [ ] Path traversal attempts return 403
- [ ] Unsupported methods return 405
- [ ] Invalid content types return 415
- [ ] Host header validation works
- [ ] Keep-alive connections function properly
- [ ] Request limits enforced (100 per connection)
- [ ] Comprehensive logging with timestamps

## Performance Considerations

- **Thread Pool:** Configurable size (default: 10 threads)
- **Connection Queue:** Handles up to 100 concurrent connections
- **Request Size Limit:** 8192 bytes maximum
- **Connection Timeout:** 30 seconds for idle connections
- **Request Limit:** 100 requests per persistent connection
- **Memory Usage:** Efficient chunk-based file serving

## Security Features

- **Path Traversal Protection:** Blocks `../` and similar patterns
- **Host Header Validation:** Ensures requests match server address
- **Method Validation:** Only allows GET and POST methods
- **Content Type Validation:** Strict validation for POST requests
- **Request Size Limits:** Prevents large request attacks
- **Connection Limits:** Prevents connection exhaustion

## Logging

The server provides comprehensive logging:

- **Server startup/shutdown events**
- **File transfer activities**
- **Security violations (path traversal, invalid hosts)**
- **Thread pool status and queuing warnings**
- **Connection management events**
- **Error conditions and exceptions**

## Security Notes

- This is a demonstration system for educational purposes
- No authentication or encryption is implemented
- Use only on trusted networks
- Consider implementing additional security measures for production use

## This is a project for Computer Network Course 
