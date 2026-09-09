<p align="center">
  <img src="https://img.shields.io/badge/WiFiCall-v1.0%20PRO-neongreen?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/Author-IMIN-neonblue?style=for-the-badge">
  <img src="https://img.shields.io/badge/Telegram-%40script__ill-neonpurple?style=for-the-badge&logo=telegram">
</p>

```
██╗    ██╗██╗███████╗██╗     ██████╗ █████╗ ██╗     ██╗
██║    ██║██║██╔════╝██║    ██╔════╝██╔══██╗██║     ██║
██║ █╗ ██║██║█████╗  ██║    ██║     ███████║██║     ██║
██║███╗██║██║██╔══╝  ██║    ██║     ██╔══██║██║     ██║
╚███╔███╔╝██║██║     ██║    ╚██████╗██║  ██║███████╗███████╗
 ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝     ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝
```
                                                                        <p align="center">
  <b>VoIP Calling Over WiFi — No SIM Card Required</b><br>                <i>Twilio · Pure SIP · PJSIP — Three Backends, One Tool</i>
</p>

---

## ⚡ Overview

**WiFiCall** is a professional VoIP calling tool that enables voice calls over WiFi **without any SIM card or cellular service**. Built for penetration testers, security researchers, and authorized security professionals who need programmatic voice calling capabilities.

### Why WiFiCall?

Traditional phone calls require a SIM card tied to a cellular carrier. This creates limitations:
- You need physical access to a SIM
- Calls are traceable to your carrier
- No API for automation
- Hard to integrate into security testing workflows

**WiFiCall solves this** using Voice over IP (VoIP) protocols over any internet connection — WiFi, Ethernet, or mobile data.

---

## 🎯 Capabilities

| Backend | Calls Real Phone Numbers | Requires Compilation |
|---------|:------------------------:|:--------------------:|
| **Twilio** | ✅ Yes | ❌ No |
| **Pure SIP** | ✅ Via SIP trunk | ❌ No |
| **PJSIP** | ✅ Via SIP trunk | ✅ Yes (C libs) |

### Feature Set

- **No SIM required** — Works over any WiFi or data connection
- **Three backends** — Twilio (easiest), Pure SIP (no compilation), PJSIP (enterprise)
- **Call real phone numbers** — Via Twilio Voice API or any SIP trunk provider
- **SIP-to-SIP calls** — Direct device-to-device calls over VoIP
- **Beautiful CLI** — Color-coded interactive mode with ASCII art banner
- **Setup wizard** — Guided configuration for all backends
- **Dependency manager** — Auto-install required packages from within the tool
- **Call recording** — Record calls for evidence collection (authorized testing only)

---

## ⚙️ Installation

### Requirements

- Python 3.8+
- WiFi or internet connection
- One of: Twilio account / SIP provider credentials

### Quick Install

```bash
# Save the script
wget https://github.com/script-ill/Wifi_Call.git
 # or clone from authorized repo

# Install dependencies
pip install -r requirements.txt

# Run setup
python wificall.py setup

# Make a call
python wificall.py call +1234567890
```

### Backend Setup

**Option 1 — Twilio (Easiest — Call Any Phone Number):**

```bash
pip install twilio
python wificall.py setup
# Enter Account SID, Auth Token, and your Twilio number
```

Get a free Twilio account: https://www.twilio.com/try-twilio

**Option 2 — Pure SIP (No Compilation):**

```bash
pip install simple-sip-client
python wificall.py setup
# Choose SIP backend and enter your SIP provider credentials
```

---

## 🚀 Usage

```bash
# Show help
python wificall.py --help

# Run setup wizard
python wificall.py setup

# Interactive mode
python wificall.py interactive

# Call a phone number (Twilio backend)
python wificall.py call +1234567890

# Call a SIP URI
python wificall.py --backend sip call sip:user@pbx.example.com

# Speak a custom message
python wificall.py call --message "Alert system activated" +1234567890

# Override backend
python wificall.py --backend sip call +1234567890

# Check configuration and available backends
python wificall.py info
```

---

## 📋 Requirements

```
# WiFiCall — Core Dependencies
# Install one backend depending on your use case:

# Backend 1: Twilio (recommended for calling real phone numbers)
twilio>=9.0.0

# Backend 2: Pure SIP (no compilation needed)
simple-sip-client>=0.0.3

# Backend 3: Async SIP
sipx>=4.0.0

# Backend 4: PJSIP (requires compiled C libraries)
# pjsua2 — must be compiled from source
```

---

## 🔐 Authorization Notice

**I, the user of this tool, confirm that:**

✅ I have **explicit written authorization** to perform security testing on the targets I scan or call.

✅ I am using this tool **solely for authorized penetration testing, security assessment, and educational purposes**.

✅ I understand that unauthorized use against systems I do not own or have written permission to test is **illegal** and **unethical**.

✅ This tool is used in compliance with all applicable local, state, and federal laws.

---

## ⚠️ Legal Disclaimer

This tool is provided **strictly for authorized security testing and educational purposes only**. You must have explicit written permission before testing any system or making any calls. Unauthorized access or use is illegal.

**The author (IMIN) assumes NO liability** for misuse or damages caused by this software.

---

## 💰 Cost Overview

| Backend | Starting Cost | Per Minute (US) |
|---------|:------------:|:----------------:|
| **Twilio** | $15 free trial | ~$0.013 |
| **Pure SIP** | Free (SIP-to-SIP) | $0 (direct calls) |
| **SIP Trunk** | ~$0–$2/mo | ~$0.01–$0.04 |

---

## 🧠 Author

**IMIN** — Security Researcher & Penetration Tester

- Telegram: [@script_ill](https://t.me/script_ill)

---

## 📜 License

**WiFiCall** is released under a **Proprietary License**.

You may **use** this software for authorized security testing and education.
You may **NOT** copy, modify, distribute, sublicense, or sell this software without explicit written permission from the author.

See the [LICENSE](LICENSE) file for full terms.

---

*"Stay secure. Stay dangerous."*
