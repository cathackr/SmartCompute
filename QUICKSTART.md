# ⚡ SmartCompute - Quick Start Guide

Get SmartCompute running in **30 seconds** or **2 minutes** (with Docker).

---

## 🚀 30-Second Demo (Express Mode)

### Step 1: Clone & Run
```bash
git clone https://github.com/cathackr/SmartCompute.git
cd SmartCompute
python3 smartcompute_express.py --auto-open
```

### Step 2: Watch the Magic ✨
- Dashboard opens automatically in your browser
- Real-time system monitoring (CPU, RAM, Disk, Network)
- Beautiful charts and metrics
- Security analysis

**That's it!** You're monitoring your system.

---

## 🐳 2-Minute Full Stack (with Grafana)

### Step 1: Start Docker Compose
```bash
docker-compose -f docker-compose.quickstart.yml up -d
```

### Step 2: Wait 60 seconds for services to start

### Step 3: Access Dashboards

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana** | http://localhost:3000 | admin / smartcompute123 |
| **Prometheus** | http://localhost:9090 | (no auth) |
| **SmartCompute API** | http://localhost:5000 | (no auth) |
| **Jaeger Tracing** | http://localhost:16686 | (no auth) |
| **AlertManager** | http://localhost:9093 | (no auth) |

### Step 4: Explore Pre-built Dashboards
1. Open Grafana (http://localhost:3000)
2. Go to **Dashboards** → **Browse**
3. Open **SmartCompute Overview**
4. See real-time metrics!

---

## 🛑 Stop Everything

```bash
# Stop services (keeps data)
docker-compose -f docker-compose.quickstart.yml down

# Stop and delete all data
docker-compose -f docker-compose.quickstart.yml down -v
```

---

## 🔧 Troubleshooting

### Express Mode Issues

**Problem:** `ModuleNotFoundError: No module named 'psutil'`
```bash
pip install psutil netifaces
```

**Problem:** Dashboard doesn't open
```bash
# Run without auto-open and copy the file path
python3 smartcompute_express.py
# Then manually open the file:/// path shown
```

### Docker Mode Issues

**Problem:** Port already in use
```bash
# Check what's using ports
sudo lsof -i :3000
sudo lsof -i :5000

# Stop conflicting services or change ports in docker-compose.quickstart.yml
```

**Problem:** Grafana not loading
```bash
# Check service status
docker-compose ps

# View Grafana logs
docker-compose logs grafana

# Restart Grafana
docker-compose restart grafana
```

**Problem:** Out of disk space
```bash
# Check Docker disk usage
docker system df

# Clean up old images/containers
docker system prune -a
```

---

## 📚 Next Steps

### Learn More
- [Full README](./README.md) - Complete documentation
- [Security Guide](./SECURITY_README.md) - Secure your installation
- [User Guide](./SMARTCOMPUTE_INDUSTRIAL_USER_GUIDE.md) - Advanced features

### Customize
- Edit `docker-compose.quickstart.yml` to change ports
- Copy `.env.example` to `.env` and configure credentials
- Add your own Grafana dashboards

### Deploy to Production
- Read [Security Guide](./SECURITY_README.md) first
- Change default passwords
- Enable HTTPS/SSL
- Set up proper authentication
- Configure backups

---

## 🆘 Need Help?

- **GitHub Issues:** https://github.com/cathackr/SmartCompute/issues
- **Email:** ggwre04p0@mozmail.com
- **LinkedIn:** https://www.linkedin.com/in/martín-iribarne-swtf/

---

**Happy Monitoring! 🎉**
