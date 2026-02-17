"""
SmartCompute FastAPI application.

Provides REST endpoints for monitoring, license activation,
and webhook handling.

Run with::

    smartcompute serve
    # or
    uvicorn smartcompute.api.main:app --host 0.0.0.0 --port 5000
"""

from __future__ import annotations

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import HTMLResponse, JSONResponse
except ImportError:
    raise ImportError(
        "FastAPI is required for the API server. "
        "Install with: pip install smartcompute[enterprise]"
    )

from smartcompute._version import __version__

app = FastAPI(
    title="SmartCompute API",
    version=__version__,
    description="Industrial Cybersecurity & Monitoring Platform",
)


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and Docker."""
    return {"status": "healthy", "version": __version__}


@app.get("/api/status")
async def api_status():
    """Return current system and license status."""
    from smartcompute.licensing.validator import LicenseValidator

    validator = LicenseValidator()
    info = validator.get_current_license()
    return {
        "version": __version__,
        "tier": info.tier,
        "org": info.org,
        "valid": info.valid,
    }


@app.post("/api/activate")
async def activate_license(payload: dict):
    """Activate a license token."""
    token = payload.get("token", "")
    if not token:
        raise HTTPException(status_code=400, detail="Missing 'token' field")

    from smartcompute.licensing.validator import LicenseValidator

    validator = LicenseValidator()
    info = validator.activate(token)

    if not info.valid:
        raise HTTPException(status_code=400, detail=info.error)

    return {
        "status": "activated",
        "tier": info.tier,
        "org": info.org,
        "expires_at": info.expires_at,
    }


@app.post("/api/webhook/mercadopago")
async def mercadopago_webhook(payload: dict):
    """Receive MercadoPago payment notifications."""
    return {"status": "received"}


@app.get("/api/system")
async def system_info():
    """Return real-time system resource data."""
    import psutil
    import socket
    import platform
    from datetime import datetime

    cpu_freq = psutil.cpu_freq()
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    net = psutil.net_io_counters()
    boot = psutil.boot_time()

    # Network interfaces
    interfaces = []
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    for name, addr_list in addrs.items():
        s = stats.get(name)
        ips = [a.address for a in addr_list if a.family == socket.AF_INET]
        if ips:
            interfaces.append({
                "name": name,
                "ip": ips[0],
                "speed": s.speed if s else 0,
                "up": s.isup if s else False,
            })

    # Top processes
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            info = p.info
            if info["cpu_percent"] and info["cpu_percent"] > 0.1:
                procs.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    procs.sort(key=lambda x: x["cpu_percent"] or 0, reverse=True)

    # Connections summary
    conns = psutil.net_connections(kind="inet")
    listen_ports = [c.laddr.port for c in conns if c.status == "LISTEN" and c.laddr]

    return {
        "timestamp": datetime.now().isoformat(),
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "uptime_hours": round((psutil.time.time() - boot) / 3600, 1),
        "cpu": {
            "percent": psutil.cpu_percent(interval=0),
            "per_cpu": psutil.cpu_percent(percpu=True),
            "cores": psutil.cpu_count(),
            "freq_mhz": round(cpu_freq.current) if cpu_freq else 0,
        },
        "memory": {
            "total_gb": round(mem.total / 1e9, 1),
            "used_gb": round(mem.used / 1e9, 1),
            "percent": mem.percent,
        },
        "disk": {
            "total_gb": round(disk.total / 1e9, 1),
            "used_gb": round(disk.used / 1e9, 1),
            "percent": round(disk.used / disk.total * 100, 1),
        },
        "network": {
            "bytes_sent_mb": round(net.bytes_sent / 1e6, 1),
            "bytes_recv_mb": round(net.bytes_recv / 1e6, 1),
            "interfaces": interfaces,
            "listen_ports": sorted(set(listen_ports))[:20],
        },
        "top_processes": procs[:15],
    }


@app.get("/api/network/hosts")
async def network_hosts():
    """Return discovered network hosts (passive ARP cache read)."""
    from smartcompute.core.network_scanner import get_scanner

    scanner = get_scanner()
    await scanner.read_arp_cache()
    return scanner.get_cached_hosts()


@app.post("/api/network/scan")
async def network_scan():
    """Trigger active ping sweep and return results."""
    from smartcompute.core.network_scanner import get_scanner

    scanner = get_scanner()
    await scanner.read_arp_cache()
    await scanner.ping_sweep()
    return scanner.get_cached_hosts()


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Live network monitoring dashboard."""
    return DASHBOARD_HTML


DASHBOARD_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SmartCompute Dashboard</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',system-ui,sans-serif;background:#0a0e17;color:#e0e0e0;overflow-x:hidden}
.header{background:linear-gradient(135deg,#0f1923,#1a2940);padding:1rem 2rem;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #1e3a5f}
.header h1{font-size:1.4rem;color:#4fc3f7}
.header .meta{font-size:.85rem;color:#78909c}
.badge{display:inline-block;padding:2px 10px;border-radius:12px;font-size:.75rem;font-weight:600;margin-left:8px}
.badge-free{background:#2e7d32;color:#fff}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:1rem;padding:1.5rem}
.card{background:linear-gradient(145deg,#111822,#162032);border:1px solid #1e3a5f;border-radius:12px;padding:1.2rem;transition:border-color .2s}
.card:hover{border-color:#4fc3f7}
.card h2{font-size:1rem;color:#4fc3f7;margin-bottom:.8rem;display:flex;align-items:center;gap:8px}
.card h2 .icon{font-size:1.2rem}
.meter{height:8px;background:#1a2940;border-radius:4px;overflow:hidden;margin:.4rem 0}
.meter-fill{height:100%;border-radius:4px;transition:width .6s ease}
.meter-ok{background:linear-gradient(90deg,#4caf50,#66bb6a)}
.meter-warn{background:linear-gradient(90deg,#ff9800,#ffa726)}
.meter-crit{background:linear-gradient(90deg,#f44336,#e57373)}
.stat{display:flex;justify-content:space-between;padding:.3rem 0;font-size:.9rem}
.stat .label{color:#90a4ae}
.stat .value{color:#fff;font-weight:600}
table{width:100%;border-collapse:collapse;font-size:.82rem}
th{text-align:left;color:#4fc3f7;padding:6px 8px;border-bottom:1px solid #1e3a5f}
td{padding:5px 8px;border-bottom:1px solid #0f1923}
tr:hover td{background:rgba(79,195,247,.05)}
.iface-row{display:flex;justify-content:space-between;padding:4px 0;font-size:.88rem}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:6px}
.dot-up{background:#4caf50}
.dot-down{background:#f44336}
.dot-warn{background:#ff9800}
.scan-btn{background:linear-gradient(135deg,#1565c0,#1e88e5);color:#fff;border:none;padding:6px 16px;border-radius:6px;cursor:pointer;font-size:.82rem;font-weight:600;transition:opacity .2s}
.scan-btn:hover{opacity:.85}
.scan-btn:disabled{opacity:.5;cursor:not-allowed}
.host-meta{display:flex;gap:1.2rem;flex-wrap:wrap;align-items:center;margin-bottom:.6rem;font-size:.82rem;color:#90a4ae}
.ports{display:flex;flex-wrap:wrap;gap:4px;margin-top:.4rem}
.port{background:#1a2940;padding:2px 8px;border-radius:4px;font-size:.78rem;color:#4fc3f7;border:1px solid #1e3a5f}
.refresh-info{text-align:center;padding:.6rem;color:#546e7a;font-size:.78rem}
.cpu-bars{display:flex;gap:3px;align-items:flex-end;height:40px;margin:.6rem 0}
.cpu-bar{flex:1;background:#1a2940;border-radius:2px 2px 0 0;position:relative;min-width:6px;transition:height .6s ease}
.cpu-bar-inner{position:absolute;bottom:0;width:100%;border-radius:2px 2px 0 0;transition:height .6s ease}
</style>
</head>
<body>
<div class="header">
  <div><h1>SmartCompute Dashboard</h1></div>
  <div class="meta">
    <span id="hostname"></span>
    <span class="badge badge-free">STARTER</span>
    <span id="clock" style="margin-left:12px"></span>
  </div>
</div>
<div class="grid">
  <!-- CPU -->
  <div class="card">
    <h2><span class="icon">&#9881;</span> CPU</h2>
    <div class="stat"><span class="label">Usage</span><span class="value" id="cpu-pct">--</span></div>
    <div class="meter"><div class="meter-fill meter-ok" id="cpu-meter" style="width:0%"></div></div>
    <div class="stat"><span class="label">Cores</span><span class="value" id="cpu-cores">--</span></div>
    <div class="stat"><span class="label">Frequency</span><span class="value" id="cpu-freq">--</span></div>
    <div class="cpu-bars" id="cpu-bars"></div>
  </div>
  <!-- Memory -->
  <div class="card">
    <h2><span class="icon">&#128190;</span> Memory</h2>
    <div class="stat"><span class="label">Used / Total</span><span class="value" id="mem-used">--</span></div>
    <div class="meter"><div class="meter-fill meter-ok" id="mem-meter" style="width:0%"></div></div>
    <div class="stat"><span class="label">Usage</span><span class="value" id="mem-pct">--</span></div>
  </div>
  <!-- Disk -->
  <div class="card">
    <h2><span class="icon">&#128451;</span> Disk</h2>
    <div class="stat"><span class="label">Used / Total</span><span class="value" id="disk-used">--</span></div>
    <div class="meter"><div class="meter-fill meter-ok" id="disk-meter" style="width:0%"></div></div>
    <div class="stat"><span class="label">Usage</span><span class="value" id="disk-pct">--</span></div>
  </div>
  <!-- Network I/O -->
  <div class="card">
    <h2><span class="icon">&#127760;</span> Network I/O</h2>
    <div class="stat"><span class="label">Sent</span><span class="value" id="net-sent">--</span></div>
    <div class="stat"><span class="label">Received</span><span class="value" id="net-recv">--</span></div>
    <div class="stat"><span class="label">Uptime</span><span class="value" id="uptime">--</span></div>
  </div>
  <!-- Interfaces -->
  <div class="card">
    <h2><span class="icon">&#128268;</span> Network Interfaces</h2>
    <div id="ifaces"></div>
  </div>
  <!-- Listening Ports -->
  <div class="card">
    <h2><span class="icon">&#128274;</span> Listening Ports</h2>
    <div class="ports" id="ports"></div>
  </div>
  <!-- Top Processes -->
  <div class="card" style="grid-column:1/-1">
    <h2><span class="icon">&#9889;</span> Top Processes</h2>
    <table>
      <thead><tr><th>PID</th><th>Name</th><th>CPU %</th><th>MEM %</th></tr></thead>
      <tbody id="procs"></tbody>
    </table>
  </div>
  <!-- Network Hosts -->
  <div class="card" style="grid-column:1/-1">
    <h2><span class="icon">&#128421;</span> Network Hosts</h2>
    <div class="host-meta">
      <span id="host-count">--</span>
      <span id="host-subnets"></span>
      <span id="host-gw"></span>
      <span id="scan-status"></span>
      <button class="scan-btn" id="scan-btn" onclick="triggerScan()">Scan Network</button>
    </div>
    <table>
      <thead><tr><th>Status</th><th>IP</th><th>Hostname</th><th>MAC</th><th>Vendor</th><th>Interface</th><th>Source</th></tr></thead>
      <tbody id="net-hosts"></tbody>
    </table>
  </div>
</div>
<div class="refresh-info">Auto-refresh every 3 seconds &mdash; SmartCompute v""" + __version__ + """</div>
<script>
function meterClass(pct){return pct>85?'meter-crit':pct>60?'meter-warn':'meter-ok'}
function setMeter(id,pct){
  const el=document.getElementById(id);
  el.style.width=pct+'%';
  el.className='meter-fill '+meterClass(pct);
}
async function refresh(){
  try{
    const r=await fetch('/api/system');
    const d=await r.json();
    document.getElementById('hostname').textContent=d.hostname+' ('+d.platform+')';
    document.getElementById('clock').textContent=new Date(d.timestamp).toLocaleTimeString();
    // CPU
    document.getElementById('cpu-pct').textContent=d.cpu.percent+'%';
    setMeter('cpu-meter',d.cpu.percent);
    document.getElementById('cpu-cores').textContent=d.cpu.cores+' cores';
    document.getElementById('cpu-freq').textContent=d.cpu.freq_mhz+' MHz';
    // Per-CPU bars
    const bars=document.getElementById('cpu-bars');
    if(!bars.children.length){
      d.cpu.per_cpu.forEach(()=>{
        const b=document.createElement('div');b.className='cpu-bar';b.style.height='40px';
        const inner=document.createElement('div');inner.className='cpu-bar-inner';
        b.appendChild(inner);bars.appendChild(b);
      });
    }
    d.cpu.per_cpu.forEach((v,i)=>{
      if(bars.children[i]){
        const inner=bars.children[i].firstChild;
        inner.style.height=Math.max(2,v)+'%';
        inner.style.background=v>85?'#f44336':v>60?'#ff9800':'#4caf50';
      }
    });
    // Memory
    document.getElementById('mem-used').textContent=d.memory.used_gb+' / '+d.memory.total_gb+' GB';
    document.getElementById('mem-pct').textContent=d.memory.percent+'%';
    setMeter('mem-meter',d.memory.percent);
    // Disk
    document.getElementById('disk-used').textContent=d.disk.used_gb+' / '+d.disk.total_gb+' GB';
    document.getElementById('disk-pct').textContent=d.disk.percent+'%';
    setMeter('disk-meter',d.disk.percent);
    // Network
    document.getElementById('net-sent').textContent=d.network.bytes_sent_mb+' MB';
    document.getElementById('net-recv').textContent=d.network.bytes_recv_mb+' MB';
    document.getElementById('uptime').textContent=d.uptime_hours+' hours';
    // Interfaces
    const ifaces=document.getElementById('ifaces');
    ifaces.innerHTML=d.network.interfaces.map(i=>
      '<div class="iface-row"><span><span class="dot '+(i.up?'dot-up':'dot-down')+'"></span>'+i.name+'</span><span>'+i.ip+(i.speed?' &middot; '+i.speed+'Mb':'')+'</span></div>'
    ).join('');
    // Ports
    const ports=document.getElementById('ports');
    ports.innerHTML=d.network.listen_ports.map(p=>'<span class="port">:'+p+'</span>').join('');
    // Processes
    const procs=document.getElementById('procs');
    procs.innerHTML=d.top_processes.map(p=>
      '<tr><td>'+p.pid+'</td><td>'+p.name+'</td><td>'+(p.cpu_percent||0).toFixed(1)+'</td><td>'+(p.memory_percent||0).toFixed(1)+'</td></tr>'
    ).join('');
  }catch(e){console.error(e)}
  refreshHosts();
}
async function refreshHosts(){
  try{
    const r=await fetch('/api/network/hosts');
    const d=await r.json();
    document.getElementById('host-count').textContent=d.total+' hosts discovered, '+d.reachable+' reachable';
    document.getElementById('host-subnets').textContent=d.subnets.length?'Subnets: '+d.subnets.join(', '):'';
    document.getElementById('host-gw').textContent=d.gateway?'Gateway: '+d.gateway:'';
    if(d.scan_in_progress){
      document.getElementById('scan-status').textContent='Scanning...';
      document.getElementById('scan-btn').disabled=true;
    }else{
      document.getElementById('scan-btn').disabled=false;
      document.getElementById('scan-status').textContent=d.last_scan_time?'Last scan: '+new Date(d.last_scan_time*1000).toLocaleTimeString():'';
    }
    const tb=document.getElementById('net-hosts');
    tb.innerHTML=d.hosts.map(h=>{
      const dotCls=h.status==='reachable'?'dot-up':h.status==='stale'?'dot-warn':'dot-down';
      return '<tr><td><span class="dot '+dotCls+'"></span>'+h.status+'</td><td>'+h.ip+'</td><td>'+(h.hostname||'—')+'</td><td>'+(h.mac||'—')+'</td><td>'+(h.vendor||'—')+'</td><td>'+(h.interface||'—')+'</td><td>'+h.source+'</td></tr>';
    }).join('');
  }catch(e){console.error('hosts',e)}
}
async function triggerScan(){
  const btn=document.getElementById('scan-btn');
  btn.disabled=true;
  document.getElementById('scan-status').textContent='Scanning...';
  try{
    const r=await fetch('/api/network/scan',{method:'POST'});
    const d=await r.json();
    document.getElementById('host-count').textContent=d.total+' hosts discovered, '+d.reachable+' reachable';
    document.getElementById('scan-status').textContent='Last scan: '+new Date(d.last_scan_time*1000).toLocaleTimeString();
    const tb=document.getElementById('net-hosts');
    tb.innerHTML=d.hosts.map(h=>{
      const dotCls=h.status==='reachable'?'dot-up':h.status==='stale'?'dot-warn':'dot-down';
      return '<tr><td><span class="dot '+dotCls+'"></span>'+h.status+'</td><td>'+h.ip+'</td><td>'+(h.hostname||'—')+'</td><td>'+(h.mac||'—')+'</td><td>'+(h.vendor||'—')+'</td><td>'+(h.interface||'—')+'</td><td>'+h.source+'</td></tr>';
    }).join('');
  }catch(e){console.error('scan',e)}finally{btn.disabled=false}
}
refresh();
setInterval(refresh,3000);
</script>
</body>
</html>
"""
