# XMRT-DAO-Ecosystem 🌐⛏️

**Advanced Decentralized Autonomous Organization with Meshtastic MESHNET Integration**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-red.svg)](https://flask.palletsprojects.com/)
[![Meshtastic](https://img.shields.io/badge/Meshtastic-2.3.3-green.svg)](https://meshtastic.org/)

## 🚀 Overview

The **XMRT-DAO-Ecosystem** is a cutting-edge implementation of a decentralized autonomous organization that bridges traditional cryptocurrency mining with innovative mesh networking technology. This system combines real-world Monero mining through SupportXMR with Meshtastic mesh networking to create a resilient, decentralized ecosystem.

### 🌟 Key Features

- **🌐 Meshtastic MESHNET Integration**: Full integration with Meshtastic mesh networking hardware
- **⛏️ SupportXMR Mining Integration**: Real-time mining statistics and participant tracking
- **🏆 Enhanced Leaderboard**: Mining leaderboard with mesh connectivity bonuses
- **📡 Participant Verification**: Ping-based verification system via MESHNET
- **🔗 Dual Token System**: ERC-20 utility token + ERC-721 IP NFT
- **📊 Real-time Monitoring**: Live network and mining statistics
- **🛡️ Decentralized Governance**: On-chain voting and proposal system

## 📋 Contract Information

### **Deployed Contracts (Sepolia Testnet)**

- **XMRT Token (ERC-20)**: `0x77307DFbc436224d5e6f2048d2b6bDfA66998a15`
- **XMRT-IP NFT (ERC-721)**: `0x9d691fc136a846d7442d1321a2d1b6aaef494eda`
- **Mining Wallet**: `46UxNFuGM2E3UwmZWWJicaRPoRwqwW4byQkaTHkX8yPcVihp91qAVtSFipWUGJJUyTXgzSqxDQtNLf2bsp2DX2qCCgC5mg`

### **Token Economics**
- **Max Supply**: 20,999,990 XMRT
- **IP NFT Supply**: 1 unique NFT (represents intellectual property ownership)
- **Mining Pool**: SupportXMR integration
- **Treasury Allocation**: 85% treasury, 15% operations

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   XMRT-DAO-ECOSYSTEM                       │
├─────────────────────────────────────────────────────────────┤
│  Flask API Layer                                           │
│  ├── Mining API (/api/mining/)                            │
│  ├── MESHNET API (/api/meshnet/)                          │
│  └── System Status (/api/status)                          │
├─────────────────────────────────────────────────────────────┤
│  Service Layer                                             │
│  ├── MiningService (SupportXMR Integration)               │
│  └── MESHNETService (Meshtastic Integration)              │
├─────────────────────────────────────────────────────────────┤
│  External Integrations                                     │
│  ├── SupportXMR API                                       │
│  ├── Meshtastic Hardware                                  │
│  └── Ethereum Network (Sepolia)                           │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Installation & Setup

### **Prerequisites**
- Python 3.8+
- Git
- Optional: Meshtastic hardware (HELTEC, TBEAM, etc.)

### **Quick Start**

1. **Clone the repository**
```bash
git clone https://github.com/DevGruGold/XMRT-DAO-Ecosystem.git
cd XMRT-DAO-Ecosystem
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set environment variables**
```bash
export MESH_PORT="simulate"  # Use "simulate" for testing, "/dev/ttyUSB0" for hardware
export MESH_UPDATE_INTERVAL="30"
export FLASK_ENV="development"
export PORT="5000"
```

4. **Run the application**
```bash
python app.py
```

## 🌐 MESHNET Integration

### **Supported Hardware**
- **HELTEC WiFi LoRa 32 V3**
- **LILYGO T-Beam**
- **HELTEC WiFi LoRa 32 V2**
- **RAK WisBlock**

### **MESHNET Features**

#### **🔄 Simulation Mode**
For testing without hardware:
```python
# Automatically creates simulated mesh nodes
meshnet_service = MESHNETService({'mesh_port': 'simulate'})
```

#### **📡 Hardware Mode**
For real Meshtastic devices:
```python
# Connect to actual hardware
meshnet_service = MESHNETService({'mesh_port': '/dev/ttyUSB0'})
```

#### **⛏️ Mining Integration**
- Real-time SupportXMR pool statistics
- Mesh-connected miner verification
- 10% efficiency bonus for mesh connectivity
- Automatic participant ping verification

## 🔗 API Endpoints

### **Mining Endpoints**
```http
GET /api/mining/stats          # Current mining statistics
GET /api/mining/leaderboard    # Enhanced leaderboard with mesh status
```

### **MESHNET Endpoints**
```http
GET /api/meshnet/status        # Network status and health metrics
GET /api/meshnet/leaderboard   # Mining leaderboard with connectivity scores
GET /api/meshnet/nodes         # All discovered mesh nodes
GET /api/meshnet/mining/stats  # Combined mining and mesh statistics
POST /api/meshnet/verify/<wallet>  # Verify participant connectivity
POST /api/meshnet/initialize   # Initialize/reinitialize MESHNET
GET /api/meshnet/health        # MESHNET service health check
```

### **System Endpoints**
```http
GET /                          # System overview and information
GET /health                    # Comprehensive health check
GET /api/status               # Complete system status
```

## 📊 Enhanced Leaderboard System

The enhanced leaderboard combines traditional mining metrics with mesh connectivity:

```json
{
  "rank": 1,
  "wallet_address": "worker_001",
  "hash_rate": 150.0,
  "xmr_earned": 0.00124,
  "mesh_connected": true,
  "mesh_node_id": "mesh_001",
  "connectivity_score": 95,
  "efficiency_bonus": 1.1,
  "mesh_node_info": {
    "short_name": "ALPHA",
    "hardware_model": "HELTEC_V3",
    "signal_strength": -85,
    "snr": 12.5,
    "position": {"lat": 10.0, "lon": -84.0}
  }
}
```

## 🔧 Configuration

### **Environment Variables**
```bash
# MESHNET Configuration
MESH_PORT="simulate"           # "simulate" or hardware port like "/dev/ttyUSB0"
MESH_UPDATE_INTERVAL="30"      # Update interval in seconds

# Flask Configuration
FLASK_ENV="development"        # "development" or "production"
PORT="5000"                   # Server port
SECRET_KEY="your-secret-key"  # Flask secret key

# Optional: Override default contract addresses
XMRT_TOKEN_ADDRESS="0x77307DFbc436224d5e6f2048d2b6bDfA66998a15"
XMRT_IP_NFT_ADDRESS="0x9d691fc136a846d7442d1321a2d1b6aaef494eda"
```

## 🚀 Deployment

### **Render.com Deployment**
```bash
# Build Command
pip install -r requirements.txt

# Start Command  
gunicorn --bind 0.0.0.0:$PORT app:app

# Environment Variables
MESH_PORT=simulate
MESH_UPDATE_INTERVAL=30
```

### **Local Development**
```bash
python app.py
```

### **Production with Gunicorn**
```bash
gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
```

## 📈 Monitoring & Metrics

### **Network Health Metrics**
- **Total Nodes**: Number of discovered mesh nodes
- **Active Nodes**: Nodes active within last 5 minutes
- **Mining Nodes**: Nodes participating in mining
- **Mesh Connectivity Rate**: Percentage of miners connected to mesh
- **Network Health**: Overall network status (Excellent/Good/Fair)

### **Mining Metrics**
- **Total Hash Rate**: Combined hash rate from all participants
- **Mesh Hash Rate**: Hash rate from mesh-connected miners
- **Efficiency Bonus**: 10% bonus for mesh connectivity
- **XMR Earnings**: Real-time earnings from SupportXMR

## 🔒 Security & Privacy

- **Hardware Security**: Mesh networks operate independently of internet
- **Decentralized Verification**: Participant verification through mesh pings
- **Privacy Protection**: No personal data stored, only wallet addresses
- **Secure Communications**: Meshtastic encryption for mesh communications

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📚 Documentation

- **[API Documentation](docs/api.md)** - Complete API reference
- **[MESHNET Guide](docs/meshnet.md)** - Meshtastic integration guide
- **[Mining Integration](docs/mining.md)** - SupportXMR setup and configuration
- **[Deployment Guide](docs/deployment.md)** - Production deployment instructions

## 🗺️ Roadmap

### **Phase 1: Foundation** ✅
- [x] SupportXMR mining integration
- [x] Basic Flask API
- [x] MESHNET service implementation
- [x] Enhanced leaderboard system

### **Phase 2: Enhancement** 🔄
- [ ] Real-time WebSocket updates
- [ ] Advanced mesh routing
- [ ] Mobile application
- [ ] Cross-chain bridge integration

### **Phase 3: Scaling** 🔮
- [ ] Mainnet deployment (Polygon/Starknet)
- [ ] Advanced governance features
- [ ] AI-powered network optimization
- [ ] Global mesh network expansion

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Meshtastic Project** - For the amazing mesh networking platform
- **SupportXMR** - For reliable Monero mining pool services
- **Ethereum Community** - For the robust blockchain infrastructure
- **Flask Community** - For the excellent web framework

## 📞 Support

- **GitHub Issues**: [Create an issue](https://github.com/DevGruGold/XMRT-DAO-Ecosystem/issues)
- **Documentation**: Check the `/docs` directory
- **Community**: Join our mesh network discussions

---

**Built with ❤️ by the XMRT-DAO community**

*Bridging traditional mining with next-generation mesh networking technology*
