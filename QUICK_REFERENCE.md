# P2P File Sharing - Quick Reference

## 🚀 Quick Commands

### Start Tracker
```powershell
cd "C:\Users\Utkarsh\Desktop\CN Project\p2p_filesharing_python"
$env:ROLE="tracker"
python main.py
```

### Start Peer
```powershell
cd "C:\Users\Utkarsh\Desktop\CN Project\p2p_filesharing_python"
$env:ROLE="peer"
python main.py
```

### Start Client
```powershell
cd "C:\Users\Utkarsh\Desktop\CN Project\p2p_filesharing_python"
$env:ROLE="client"
python main.py
```

## 📁 File Locations
- **Shared files:** `shared/` directory
- **Downloaded files:** `downloads/` directory
- **Test file:** `shared/test_file.txt` (525 bytes)

## 🔑 Test File Info
- **Hash:** `74ef768475f5b2d124d3571d09ff684bc97e09c8`
- **Size:** `525` bytes
- **Filename:** `test_file.txt`

## 🔧 Default Ports
- **Tracker:** 8000
- **Peer:** 9001

## ⚡ Quick Test
1. Start tracker in Terminal 1
2. Start peer in Terminal 2  
3. Start client in Terminal 3
4. Enter test file info when prompted
5. Check `downloads/` folder for result

---
*For detailed instructions, see README.md*

