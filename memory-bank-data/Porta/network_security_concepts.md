# Network and Security Concepts

## Network Addressing

### Localhost vs External Access
- **localhost (127.0.0.1)**: Only accessible from local machine
- **0.0.0.0**: Accessible from any network interface
- **Public IP**: Accessible from internet

### Port Management
```bash
# Check what's using a port
sudo lsof -i :8111

# Find process by port
netstat -tlnp | grep 8111

# Kill process using port
kill -9 $(lsof -t -i:8111)
```

## Ngrok Understanding

### What is Ngrok?
- **Purpose**: Creates secure tunnels to localhost
- **Function**: Exposes local services to internet
- **Benefits**: 
  - No server setup required
  - Temporary public URLs
  - HTTPS support
  - Request inspection

### Ngrok Commands
```bash
# Basic tunnel
ngrok http 8111

# With custom domain (paid)
ngrok http 8111 --hostname=myapp.ngrok.io

# With authentication
ngrok http 8111 --authtoken=your_token
```

### Ngrok Features
- **Temporary URLs**: Change on each restart
- **Request Logging**: See all incoming requests
- **HTTPS**: Automatic SSL certificates
- **Custom Domains**: Available with paid plans

## Security Considerations

### Risks of Public Exposure
1. **Unauthorized Access**: Anyone with URL can access
2. **No Authentication**: No built-in security
3. **Data Exposure**: Sensitive data might be accessible
4. **Resource Abuse**: Potential for DoS attacks

### Security Solutions

#### Authentication
```python
# Token-based authentication
@app.middleware("http")
async def verify_token(request: Request, call_next):
    token = request.headers.get("Authorization")
    if not token or not validate_token(token):
        raise HTTPException(status_code=401)
    return await call_next(request)
```

#### Rate Limiting
```python
# Implement rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

#### Access Logging
```python
# Log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response
```

## Background Process Management

### Running Services in Background
```bash
# Method 1: nohup
nohup uvicorn porta:app --host 0.0.0.0 --port 8111 > porta.log 2>&1 &

# Method 2: screen
screen -S porta
uvicorn porta:app --host 0.0.0.0 --port 8111
# Ctrl+A, D to detach

# Method 3: systemd service
sudo systemctl start porta
```

### Process Monitoring
```bash
# Check running processes
ps aux | grep uvicorn
ps aux | grep ngrok

# Check port usage
netstat -tlnp | grep 8111

# Monitor logs
tail -f porta.log
```

### Process Control
```bash
# Kill by PID
kill -9 <PID>

# Kill by name
pkill -f uvicorn
pkill -f ngrok

# Graceful shutdown
kill <PID>  # SIGTERM
kill -9 <PID>  # SIGKILL
```

## Development vs Production

### Development Environment
- **Purpose**: Testing and development
- **Security**: Minimal (local access only)
- **Persistence**: Manual restart required
- **Monitoring**: Basic logging

### Production Environment
- **Purpose**: Real user access
- **Security**: Comprehensive (authentication, rate limiting)
- **Persistence**: Automatic restart, monitoring
- **Monitoring**: Advanced logging, alerting

## Best Practices

### Security
1. **Never expose without authentication**
2. **Implement rate limiting**
3. **Log all access attempts**
4. **Use HTTPS when possible**
5. **Regular security audits**

### Monitoring
1. **Track request patterns**
2. **Monitor resource usage**
3. **Alert on unusual activity**
4. **Maintain access logs**

### Maintenance
1. **Regular updates**
2. **Backup configurations**
3. **Test security measures**
4. **Document procedures**