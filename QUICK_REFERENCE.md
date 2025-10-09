# HTTP Server - Quick Reference

## 🚀 Quick Commands

### Start Server
```powershell
cd "C:\Users\Utkarsh\Desktop\CN Project\p2p_filesharing_python"
python http_server.py --host 127.0.0.1 --port 8080 --max-threads 10
```

### Test Server
```powershell
python test_client.py
```

### Test with curl
```bash
# GET HTML
curl -H "Host: 127.0.0.1:8080" http://127.0.0.1:8080/

# GET Text File
curl -H "Host: 127.0.0.1:8080" http://127.0.0.1:8080/test.txt

# GET PNG Image
curl -H "Host: 127.0.0.1:8080" http://127.0.0.1:8080/test.png -o test.png

# POST JSON
curl -X POST -H "Content-Type: application/json" -H "Host: 127.0.0.1:8080" -d '{"test": "data"}' http://127.0.0.1:8080/
```

## 📁 File Locations
- **HTML files:** `resources/index.html`
- **Test files:** `resources/test.txt`, `resources/test.png`, `resources/test.jpg`
- **Uploads:** `resources/uploads/` directory
- **Sample JSON:** `sample.json`

## 🔧 Default Configuration
- **Host:** 127.0.0.1
- **Port:** 8080
- **Max Threads:** 10
- **Max Request Size:** 8192 bytes
- **Connection Timeout:** 30 seconds
- **Max Requests per Connection:** 100

## ⚡ Quick Test
1. Start server: `python http_server.py`
2. Open browser: `http://127.0.0.1:8080/`
3. Run test client: `python test_client.py`
4. Check server logs for activity

## 🔒 Security Features
- ✅ Path traversal protection
- ✅ Host header validation
- ✅ Method validation (GET/POST only)
- ✅ Content type validation
- ✅ Request size limits
- ✅ Connection limits

---
*For detailed instructions, see README.md*