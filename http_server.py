#!/usr/bin/env python3
"""
Multi-threaded HTTP Server using low-level TCP socket programming
Supports GET and POST requests with thread pool and security features
"""

import socket
import threading
import time
import json
import os
import mimetypes
import argparse
from datetime import datetime
from urllib.parse import urlparse, unquote
import queue
import re

class HTTPRequest:
    def __init__(self, raw_request):
        self.method = None
        self.path = None
        self.version = None
        self.headers = {}
        self.body = b''
        self.parse_request(raw_request)
    
    def parse_request(self, raw_request):
        """Parse HTTP request into components"""
        lines = raw_request.split('\r\n')
        if not lines:
            return
        
        # Parse request line
        request_line = lines[0].split()
        if len(request_line) >= 3:
            self.method = request_line[0]
            self.path = request_line[1]
            self.version = request_line[2]
        
        # Parse headers
        header_end = lines.index('') if '' in lines else len(lines)
        for line in lines[1:header_end]:
            if ':' in line:
                key, value = line.split(':', 1)
                self.headers[key.strip().lower()] = value.strip()
        
        # Parse body (if present)
        body_start = raw_request.find('\r\n\r\n')
        if body_start != -1:
            self.body = raw_request[body_start + 4:].encode('utf-8')

class HTTPResponse:
    def __init__(self, status_code=200, status_text="OK"):
        self.status_code = status_code
        self.status_text = status_text
        self.headers = {}
        self.body = b''
    
    def add_header(self, key, value):
        self.headers[key] = value
    
    def set_body(self, body, content_type="text/html"):
        if isinstance(body, str):
            self.body = body.encode('utf-8')
        else:
            self.body = body
        self.add_header("Content-Type", content_type)
        self.add_header("Content-Length", str(len(self.body)))
    
    def to_bytes(self):
        """Convert response to bytes for sending"""
        response_line = f"HTTP/1.1 {self.status_code} {self.status_text}\r\n"
        headers = "\r\n".join([f"{k}: {v}" for k, v in self.headers.items()])
        return f"{response_line}{headers}\r\n\r\n".encode('utf-8') + self.body

class HTTPServer:
    def __init__(self, host='127.0.0.1', port=8080, max_threads=10):
        self.host = host
        self.port = port
        self.max_threads = max_threads
        self.server_socket = None
        self.running = False
        self.thread_pool = []
        self.connection_queue = queue.Queue(maxsize=100)
        self.active_connections = {}
        self.request_counts = {}
        self.lock = threading.Lock()
        
        # Create necessary directories
        os.makedirs('resources', exist_ok=True)
        os.makedirs('resources/uploads', exist_ok=True)
        
        self.log(f"HTTP Server initialized: {host}:{port}, max_threads={max_threads}")
    
    def log(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def start(self):
        """Start the HTTP server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(100)
            self.running = True
            
            self.log(f"Server started on {self.host}:{self.port}")
            
            # Start thread pool
            for i in range(self.max_threads):
                thread = threading.Thread(target=self.worker_thread, daemon=True)
                thread.start()
                self.thread_pool.append(thread)
            
            # Start cleanup thread for keep-alive connections
            cleanup_thread = threading.Thread(target=self.cleanup_connections, daemon=True)
            cleanup_thread.start()
            
            self.log(f"Thread pool started with {self.max_threads} threads")
            
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    client_socket.settimeout(30)  # 30-second timeout
                    
                    # Add to connection queue
                    if self.connection_queue.full():
                        self.log("Connection queue full, rejecting connection", "WARNING")
                        client_socket.close()
                    else:
                        self.connection_queue.put((client_socket, address))
                        
                except socket.error as e:
                    if self.running:
                        self.log(f"Error accepting connection: {e}", "ERROR")
                        
        except Exception as e:
            self.log(f"Server error: {e}", "ERROR")
        finally:
            self.stop()
    
    def worker_thread(self):
        """Worker thread to handle client connections"""
        while self.running:
            try:
                client_socket, address = self.connection_queue.get(timeout=1)
                self.handle_client(client_socket, address)
                self.connection_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                self.log(f"Worker thread error: {e}", "ERROR")
    
    def handle_client(self, client_socket, address):
        """Handle individual client connection"""
        client_id = f"{address[0]}:{address[1]}"
        
        try:
            with self.lock:
                if client_id not in self.active_connections:
                    self.active_connections[client_id] = {
                        'socket': client_socket,
                        'last_activity': time.time(),
                        'request_count': 0
                    }
                    self.request_counts[client_id] = 0
            
            connection_info = self.active_connections[client_id]
            
            # Check request limit (100 requests per connection)
            if connection_info['request_count'] >= 100:
                self.log(f"Request limit exceeded for {client_id}", "WARNING")
                self.send_error_response(client_socket, 429, "Too Many Requests")
                return
            
            # Receive request
            request_data = client_socket.recv(8192).decode('utf-8')
            if not request_data:
                return
            
            # Parse request
            request = HTTPRequest(request_data)
            
            # Update connection info
            connection_info['last_activity'] = time.time()
            connection_info['request_count'] += 1
            self.request_counts[client_id] += 1
            
            self.log(f"Request from {client_id}: {request.method} {request.path}")
            
            # Handle request
            response = self.process_request(request, address)
            
            # Send response
            client_socket.send(response.to_bytes())
            
            # Check for keep-alive
            connection_header = request.headers.get('connection', '')
            if (request.version == 'HTTP/1.1' and connection_header.lower() != 'close') or \
               (request.version == 'HTTP/1.0' and connection_header.lower() == 'keep-alive'):
                # Keep connection alive
                pass
            else:
                # Close connection
                client_socket.close()
                with self.lock:
                    if client_id in self.active_connections:
                        del self.active_connections[client_id]
                    if client_id in self.request_counts:
                        del self.request_counts[client_id]
                        
        except Exception as e:
            self.log(f"Error handling client {client_id}: {e}", "ERROR")
            try:
                client_socket.close()
            except:
                pass
            finally:
                with self.lock:
                    if client_id in self.active_connections:
                        del self.active_connections[client_id]
                    if client_id in self.request_counts:
                        del self.request_counts[client_id]
    
    def process_request(self, request, address):
        """Process HTTP request and return response"""
        # Validate Host header
        host_header = request.headers.get('host', '')
        if not host_header:
            self.log(f"Missing Host header from {address[0]}", "WARNING")
            return self.create_error_response(400, "Bad Request", "Missing Host header")
        # When bound to 0.0.0.0, accept any host; otherwise enforce the configured host
        if self.host != '0.0.0.0':
            expected_host = f"{self.host}:{self.port}"
            if host_header != expected_host and host_header != self.host:
                self.log(f"Invalid Host header '{host_header}' from {address[0]}", "WARNING")
                return self.create_error_response(403, "Forbidden", "Invalid Host header")
        
        # Handle different HTTP methods
        if request.method == 'GET':
            return self.handle_get(request)
        elif request.method == 'POST':
            return self.handle_post(request)
        else:
            self.log(f"Unsupported method {request.method} from {address[0]}", "WARNING")
            return self.create_error_response(405, "Method Not Allowed")
    
    def handle_get(self, request):
        """Handle GET requests"""
        # Validate path to prevent directory traversal
        if not self.validate_path(request.path):
            self.log(f"Path traversal attempt: {request.path}", "WARNING")
            return self.create_error_response(403, "Forbidden", "Path traversal not allowed")
        
        # Parse path
        parsed_path = urlparse(request.path)
        file_path = parsed_path.path
        
        # Serve index.html for root path
        if file_path == '/':
            file_path = '/index.html'
        
        # Remove leading slash and construct full path
        file_path = file_path.lstrip('/')
        full_path = os.path.join('resources', file_path)
        
        if not os.path.exists(full_path):
            return self.create_error_response(404, "Not Found")
        
        if os.path.isdir(full_path):
            return self.create_error_response(403, "Forbidden")
        
        # Determine content type
        content_type, _ = mimetypes.guess_type(full_path)
        
        try:
            if content_type and content_type.startswith('text/html'):
                # Serve HTML files
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                response = HTTPResponse(200, "OK")
                response.set_body(content, "text/html; charset=utf-8")
                self.log(f"Served HTML file: {file_path}")
                
            elif file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.txt')):
                # Serve binary files
                with open(full_path, 'rb') as f:
                    content = f.read()
                response = HTTPResponse(200, "OK")
                response.set_body(content, "application/octet-stream")
                response.add_header("Content-Disposition", f"attachment; filename=\"{os.path.basename(file_path)}\"")
                self.log(f"Served binary file: {file_path} ({len(content)} bytes)")
                
            else:
                # Unsupported file type
                return self.create_error_response(415, "Unsupported Media Type")
                
        except Exception as e:
            self.log(f"Error serving file {file_path}: {e}", "ERROR")
            return self.create_error_response(500, "Internal Server Error")
        
        return response
    
    def handle_post(self, request):
        """Handle POST requests"""
        # Check content type
        content_type = request.headers.get('content-type', '')
        if not content_type.startswith('application/json'):
            self.log(f"Invalid content type: {content_type}", "WARNING")
            return self.create_error_response(415, "Unsupported Media Type", "Only application/json is supported")
        
        # Parse JSON
        try:
            json_data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            self.log("Invalid JSON in POST request", "WARNING")
            return self.create_error_response(400, "Bad Request", "Invalid JSON")
        
        # Create timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"upload_{timestamp}.json"
        file_path = os.path.join('resources', 'uploads', filename)
        
        try:
            # Write JSON to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2)
            
            # Create response
            response_data = {
                "status": "success",
                "message": "File created successfully",
                "file_path": f"uploads/{filename}"
            }
            
            response = HTTPResponse(201, "Created")
            response.set_body(json.dumps(response_data), "application/json")
            
            self.log(f"Created file: {filename}")
            return response
            
        except Exception as e:
            self.log(f"Error creating file: {e}", "ERROR")
            return self.create_error_response(500, "Internal Server Error")
    
    def validate_path(self, path):
        """Validate path to prevent directory traversal"""
        decoded_path = unquote(path)

        dangerous_patterns = ['../', '..\\', '..%2f', '..%5c']
        for pattern in dangerous_patterns:
            if pattern in decoded_path.lower():
                return False

        # Strip leading slash (all URL paths start with /) then check the remainder
        stripped = decoded_path.lstrip('/')
        if os.path.isabs(stripped):
            return False

        return True
    
    def create_error_response(self, status_code, status_text, message=""):
        """Create error response"""
        response = HTTPResponse(status_code, status_text)
        if message:
            response.set_body(f"<html><body><h1>{status_code} {status_text}</h1><p>{message}</p></body></html>")
        else:
            response.set_body(f"<html><body><h1>{status_code} {status_text}</h1></body></html>")
        return response
    
    def send_error_response(self, client_socket, status_code, status_text):
        """Send error response and close connection"""
        response = self.create_error_response(status_code, status_text)
        try:
            client_socket.send(response.to_bytes())
        except:
            pass
        finally:
            client_socket.close()
    
    def cleanup_connections(self):
        """Cleanup idle connections"""
        while self.running:
            time.sleep(10)  # Check every 10 seconds
            current_time = time.time()
            
            with self.lock:
                to_remove = []
                for client_id, info in self.active_connections.items():
                    if current_time - info['last_activity'] > 30:  # 30-second timeout
                        to_remove.append(client_id)
                
                for client_id in to_remove:
                    try:
                        self.active_connections[client_id]['socket'].close()
                    except:
                        pass
                    del self.active_connections[client_id]
                    if client_id in self.request_counts:
                        del self.request_counts[client_id]
                    self.log(f"Cleaned up idle connection: {client_id}")
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        
        # Close all active connections
        with self.lock:
            for client_id, info in self.active_connections.items():
                try:
                    info['socket'].close()
                except:
                    pass
            self.active_connections.clear()
            self.request_counts.clear()
        
        self.log("Server stopped")

def main():
    parser = argparse.ArgumentParser(description='Multi-threaded HTTP Server')
    parser.add_argument('--host', default='127.0.0.1', help='Server host (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8080, help='Server port (default: 8080)')
    parser.add_argument('--max-threads', type=int, default=10, help='Maximum thread pool size (default: 10)')
    
    args = parser.parse_args()
    
    server = HTTPServer(args.host, args.port, args.max_threads)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop()

if __name__ == "__main__":
    main()
