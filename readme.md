# 🔌 Tapo Control

A simple web application to control TP-Link Tapo smart plugs with Synology NAS deployment support.

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Copy template and configure
cp env.template .env

# Edit .env with your settings:
# - SECRET_KEY (generate with: openssl rand -hex 32)
# - TAPO_EMAIL and TAPO_PASSWORD (your Tapo account)
# - PLUGS (your device configuration)
```

### 2. Start Application

**Development:**
```bash
./manage.sh dev start
# Access: http://localhost:84
# Database Admin: http://localhost:8081
```

**Production:**
```bash
./manage.sh prod start
# Access: http://localhost:84 (configured via Synology reverse proxy)
```

## 🏠 Synology NAS Deployment

### Port Configuration (Avoiding Synology Conflicts)
- **Application Direct**: `192.168.0.38:5011` (FastAPI)
- **HTTP Nginx**: `192.168.0.38:84` → Synology Reverse Proxy → `your-domain.com:443`

### Deployment Steps

1. **Prepare the Environment**
   ```bash
   # SSH to your Synology NAS
   ssh admin@192.168.0.38
   
   # Navigate to your project directory
   cd /volume1/docker/tapo-control
   
   # Copy and configure environment
   cp env.template .env
   nano .env  # Configure your settings
   ```

2. **Deploy Application**
   ```bash
   ./manage.sh prod start
   ```

3. **Configure Synology Domain Certificate**
   
   First, ensure you have a domain certificate configured in Synology:
   - Go to DSM → Control Panel → Security → Certificate
   - Set up your domain certificate (Let's Encrypt or imported certificate)

4. **Configure Synology Reverse Proxy**
   
   Go to DSM → Application Portal → Reverse Proxy → Create:
   
   **HTTP to HTTPS Rule:**
   - Source:
     - Protocol: `HTTPS`
     - Hostname: `your-domain.com` (your actual domain)
     - Port: `443`
   - Destination:
     - Protocol: `HTTP`
     - Hostname: `localhost`
     - Port: `84`  ← Points to your Docker nginx HTTP port

   **Advanced Settings:**
   - WebSocket: ✅ Enable (if needed)
   - Custom Header:
     - Create custom header: `X-Forwarded-Proto` = `https`
     - Create custom header: `X-Forwarded-Host` = `$host`

5. **Verify Deployment**
   ```bash
   # Check containers are running
   docker-compose ps
   
   # Check internal access
   curl http://localhost:84/healthz
   
   # Check external access (replace with your domain)
   curl https://your-domain.com/healthz
   ```

## 📋 Commands

```bash
./manage.sh dev start     # Start development
./manage.sh dev stop      # Stop development
./manage.sh dev logs      # View logs
./manage.sh prod start    # Start production
./manage.sh prod logs     # View production logs
```

## 🔧 Configuration

### Environment Variables (.env)
| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | JWT secret key | `abc123...` |
| `TAPO_EMAIL` | Tapo account email | `user@email.com` |
| `TAPO_PASSWORD` | Tapo account password | `password123` |
| `PLUGS` | Device configuration | `{"집컴": "192.168.45.179"}` |
| `ADMIN_USERNAME` | Admin user name | `admin` |
| `ADMIN_PASSWORD` | Admin password | `secure123` |

### Port Configuration
- **Application**: 5011 (exposed for direct access if needed)
- **HTTP**: 84 (nginx container port, mapped via Synology reverse proxy)
- **Adminer** (dev only): 8081 (avoids conflict with existing services)

## 🛠️ Development

### Local Development
```bash
# Start with hot reload and database admin
./manage.sh dev start

# View real-time logs
./manage.sh dev logs

# Access application
open http://localhost:84

# Access database admin
open http://localhost:8081
```

### Testing
```bash
# Run tests inside container
docker-compose exec web python -m pytest

# Or run locally
python -m pytest
```

## 🔒 SSL/HTTPS Configuration

**SSL/HTTPS is handled entirely by Synology DSM:**

1. **Domain Certificate Setup** (in DSM):
   - Go to Control Panel → Security → Certificate
   - Add your domain certificate (Let's Encrypt recommended)
   - Set it as default for your domain

2. **Reverse Proxy Configuration** (in Application Portal):
   - Source: `HTTPS://your-domain.com:443`
   - Destination: `HTTP://localhost:84`
   - Synology automatically handles SSL termination

3. **Benefits of this approach**:
   - ✅ Automatic certificate renewal (Let's Encrypt)
   - ✅ Centralized SSL management in DSM
   - ✅ No need to manage certificates in containers
   - ✅ Better security with Synology's SSL handling

## 🚨 Troubleshooting

### Common Issues

**1. Cannot access via domain:**
- Check Synology reverse proxy configuration
- Verify domain certificate is active
- Ensure port 84 is accessible internally

**2. Application not starting:**
```bash
# Check container status
docker-compose ps

# View logs
./manage.sh prod logs

# Rebuild if needed
./manage.sh prod build
```

**3. Database issues:**
```bash
# Reset database (caution: removes all data)
rm users.db
./manage.sh prod restart
```

**4. Permission errors:**
```bash
# Fix file permissions
sudo chown -R $(whoami):$(whoami) .
chmod +x manage.sh
```

### Health Checks
```bash
# Check application health
curl http://localhost:84/healthz

# Check FastAPI directly
curl http://localhost:5011/healthz

# Check from external (replace with your domain)
curl https://your-domain.com/healthz
```

## 📚 Architecture

- **Frontend**: Bootstrap 5 + Vanilla JavaScript
- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Authentication**: JWT tokens with role-based access
- **Smart Plugs**: plugp100 library for Tapo P100/P105/P110
- **Deployment**: Docker Compose + Nginx reverse proxy
- **SSL**: Handled by Synology DSM domain certificates

## 🔧 User Management

### Creating Admin User
```bash
# Using environment variables (recommended)
# Set ADMIN_USERNAME and ADMIN_PASSWORD in .env
./manage.sh prod restart

# Or manually
python create_admin.py
```

### Creating Regular Users
```bash
# Via admin web interface (recommended)
# Go to https://your-domain.com/admin

# Or manually
python create_user.py
```

## 📖 API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:84/docs`
- **ReDoc**: `http://localhost:84/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

## 📝 License

This project is open source. Please check the repository for license details.
