"""
╔═══════════════════════════════════════════════════════════════╗
║                   WiFiCall v1.0 — VoIP over WiFi             ║
║         Make calls without a SIM card using Python only       ║
╚═══════════════════════════════════════════════════════════════╝

Supports:
  [1] Twilio      — Call real phone numbers via Twilio Voice API
  [2] Pure SIP    — SIP-to-SIP calls via simple-sip-client (pure Python)
  [3] PJSIP/pjsua2— SIP calls via PJSIP (requires compiling C libs)

Author: HackerAI Pentest Framework
License: MIT — For authorized security testing and educational use only.
"""

import os
import sys
import json
import time
import logging
import argparse
import textwrap
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# ──────────────────────────────────────────────────────────────
# ASCII BANNER & STYLING
# ──────────────────────────────────────────────────────────────

BANNER = r"""
██╗    ██╗██╗███████╗██╗     ██████╗ █████╗ ██╗     ██╗
██║    ██║██║██╔════╝██║    ██╔════╝██╔══██╗██║     ██📞
██║ █╗ ██║██║█████╗  ██║    ██║     ███████║██║     ██║
██║███╗██║██║██╔══╝  ██║    ██║     ██╔══██║██║     ██║
╚███╔███╔╝██║██║     ██║    ╚██████╗██║  ██║███████╗███████╗
 ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝     ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝

          Author: Imin
          Telegram: t.me/script_ill
          Github: https://github.com/script-ill
"""

# ANSI color codes
class C:
    R = '\033[91m'
    G = '\033[92m'
    Y = '\033[93m'
    B = '\033[94m'
    M = '\033[95m'
    C1 = '\033[96m'
    W = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    NC = '\033[0m'
    CLR = '\033[K'

    @staticmethod
    def red(s): return f"{C.R}{s}{C.NC}"
    @staticmethod
    def green(s): return f"{C.G}{s}{C.NC}"
    @staticmethod
    def yellow(s): return f"{C.Y}{s}{C.NC}"
    @staticmethod
    def blue(s): return f"{C.B}{s}{C.NC}"
    @staticmethod
    def magenta(s): return f"{C.M}{s}{C.NC}"
    @staticmethod
    def cyan(s): return f"{C.C1}{s}{C.NC}"
    @staticmethod
    def bold(s): return f"{C.BOLD}{s}{C.NC}"
    @staticmethod
    def dim(s): return f"{C.DIM}{s}{C.NC}"


def print_banner():
    """Display the main banner."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{C.C1}{BANNER}{C.NC}")
    print(f" {C.DIM}┌─────────────────────────────────────────────────────────────┐{C.NC}")
    print(f" {C.DIM}│{C.NC} {C.C1}WiFiCall v1.0{C.NC} — {C.G}No SIM required{C.NC} — {C.Y}Powered by Python{C.NC}{C.DIM}              │{C.NC}")
    print(f" {C.DIM}│{C.NC} {C.B}Twilio{C.NC} | {C.B}Pure SIP{C.NC} | {C.B}PJSIP{C.NC} — {C.Y}Multiple Backends{C.NC}{C.DIM}                 │{C.NC}")
    print(f" {C.DIM}│{C.NC} {C.M}Authorized security testing & educational use only{C.NC}{C.DIM}     │{C.NC}")
    print(f" {C.DIM}└─────────────────────────────────────────────────────────────┘{C.NC}")
    print()


def section_header(title):
    """Print a section header."""
    print(f"\n{C.BOLD}{C.C1}═══ {title} {C.NC}{C.DIM}{'═' * (50 - len(title))}{C.NC}\n")


def print_info(label, value, color=C. green):
    """Print an info line."""
    print(f"  {C.BOLD}{label}:{C.NC} {color(value)}{C.NC}")


def print_error(msg):
    """Print an error message."""
    print(f"  {C.R}✘ {msg}{C.NC}")


def print_success(msg):
    """Print a success message."""
    print(f"  {C.G}✔ {msg}{C.NC}")


def print_warning(msg):
    """Print a warning message."""
    print(f"  {C.Y}⚠ {msg}{C.NC}")


# ──────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────

CONFIG_DIR = Path.home() / ".wificall"
CONFIG_FILE = CONFIG_DIR / "config.json"
LOG_FILE = CONFIG_DIR / "wificall.log"
RECORDINGS_DIR = CONFIG_DIR / "recordings"

DEFAULT_CONFIG = {
    "backend": "twilio",
    "twilio": {
        "account_sid": "",
        "auth_token": "",
        "from_number": ""
    },
    "sip": {
        "server": "",
        "port": 5060,
        "transport": "udp",
        "username": "",
        "password": "",
        "domain": "",
        "from_uri": ""
    },
    "call": {
        "timeout": 60,
        "record": False,
        "say_message": "Hello, this is a test call from WiFiCall over VoIP."
    }
}


def ensure_config_dir():
    """Create config directory if it doesn't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict[str, Any]:
    """Load configuration from file or return defaults."""
    ensure_config_dir()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            merged = DEFAULT_CONFIG.copy()
            deep_update(merged, config)
            return merged
        except (json.JSONDecodeError, IOError) as e:
            print_warning(f"Config file corrupt, using defaults: {e}")
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def deep_update(base, updates):
    """Deep-update a nested dictionary."""
    for key, value in updates.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            deep_update(base[key], value)
        else:
            base[key] = value


def save_config(config: Dict[str, Any]):
    """Save configuration to file."""
    ensure_config_dir()
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        print_success(f"Configuration saved to {CONFIG_FILE}")
    except IOError as e:
        print_error(f"Failed to save config: {e}")


def setup_logging():
    """Configure logging."""
    ensure_config_dir()
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
# BACKEND: TWILIO
# ──────────────────────────────────────────────────────────────

def twilio_make_call(to_number: str, config: Dict[str, Any], message: str = None) -> bool:
    """
    Make a call using Twilio Voice API.
    Requires: pip install twilio
    """
    section_header("TWILIO CALL ENGINE")

    tw_cfg = config.get("twilio", {})
    account_sid = tw_cfg.get("account_sid") or os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = tw_cfg.get("auth_token") or os.getenv("TWILIO_AUTH_TOKEN")
    from_number = tw_cfg.get("from_number") or os.getenv("TWILIO_FROM_NUMBER")
    msg = message or config.get("call", {}).get("say_message", "Hello from WiFiCall!")

    if not all([account_sid, auth_token, from_number]):
        print_error("Twilio credentials not configured!")
        print(f"  Set them in {C.Y}~/.wificall/config.json{C.NC} or environment:")
        print(f"    {C.B}TWILIO_ACCOUNT_SID{C.NC}, {C.B}TWILIO_AUTH_TOKEN{C.NC}, {C.B}TWILIO_FROM_NUMBER{C.NC}")
        print()
        print(f"  {C.DIM}Get a free Twilio account: https://www.twilio.com/try-twilio{C.NC}")
        return False

    try:
        from twilio.rest import Client
    except ImportError:
        print_error("Twilio package not installed!")
        print(f"  Install: {C.Y}pip install twilio{C.NC}")
        return False

    print_info("Provider", "Twilio Voice API")
    print_info("From", from_number)
    print_info("To", to_number)
    print_info("Message", f'"{msg}"')
    print()

    try:
        print(f"  {C.Y}Dialing...{C.NC}")
        client = Client(account_sid, auth_token)

        twiml = f'<Response><Say voice="alice">{msg}</Say></Response>'

        call = client.calls.create(
            to=to_number,
            from_=from_number,
            twiml=twiml,
            timeout=config.get("call", {}).get("timeout", 60)
        )

        print_success(f"Call initiated! SID: {call.sid}")
        print(f"  {C.DIM}Check status: https://console.twilio.com{C.NC}")

        if config.get("call", {}).get("record", False):
            print_info("Recording", "Enabled")

        return True

    except Exception as e:
        print_error(f"Call failed: {e}")
        return False


# ──────────────────────────────────────────────────────────────
# BACKEND: PURE SIP (simple-sip-client)
# ──────────────────────────────────────────────────────────────

def sip_make_call(destination: str, config: Dict[str, Any]) -> bool:
    """
    Make a SIP call using simple-sip-client (pure Python, no C compilation).
    Requires: pip install simple-sip-client
    """
    section_header("PURE SIP CALL ENGINE")

    sip_cfg = config.get("sip", {})
    server = sip_cfg.get("server") or os.getenv("SIP_SERVER")
    port = sip_cfg.get("port") or int(os.getenv("SIP_PORT", "5060"))
    username = sip_cfg.get("username") or os.getenv("SIP_USER")
    password = sip_cfg.get("password") or os.getenv("SIP_PASS")
    transport = sip_cfg.get("transport", "udp")

    if not all([server, username]):
        print_error("SIP configuration incomplete!")
        print(f"  Set credentials in {C.Y}~/.wificall/config.json{C.NC} or environment:")
        print(f"    {C.B}SIP_SERVER{C.NC}, {C.B}SIP_USER{C.NC}, {C.B}SIP_PASS{C.NC}")
        print()
        print(f"  {C.DIM}Need a SIP trunk? Try VoIPstudio (free trial), Callcentric, or Twilio SIP trunking{C.NC}")
        return False

    try:
        from simple_sip import SIPClient
        pure_sip = True
    except ImportError:
        pure_sip = False

    if not pure_sip:
        try:
            import sipx
            sipx_avail = True
        except ImportError:
            sipx_avail = False
    else:
        sipx_avail = False

    if not pure_sip and not sipx_avail:
        print_error("No SIP library available!")
        print(f"  Install one: {C.Y}pip install simple-sip-client{C.NC}")
        print(f"           Or: {C.Y}pip install sipx{C.NC}")
        return False

    print_info("Provider", f"{server}:{port} ({transport.upper()})")
    print_info("Username", username)
    print_info("Destination", destination)
    print()

    try:
        if pure_sip:
            print(f"  {C.Y}Using simple-sip-client...{C.NC}")
            return _sip_call_simple(destination, server, port, username, password, transport, config)
        elif sipx_avail:
            print(f"  {C.Y}Using sipx (async)...{C.NC}")
            return _sip_call_sipx(destination, server, port, username, password, transport, config)
    except Exception as e:
        print_error(f"SIP call failed: {e}")
        return False


def _sip_call_simple(dest, server, port, username, password, transport, config):
    """Make SIP call using simple-sip-client."""
    from simple_sip import SIPClient

    client = SIPClient(
        server=server,
        port=port,
        username=username,
        password=password or "",
        transport=transport
    )

    print(f"  {C.Y}Registering with {server}...{C.NC}")
    registered = client.register()

    if not registered:
        print_warning("Registration status uncertain, attempting call anyway...")

    print(f"  {C.Y}Calling {dest}...{C.NC}")
    result = client.call(dest)

    if result:
        print_success(f"Call connected to {dest}!")
        print(f"  {C.DIM}Two-way audio active... Press Ctrl+C to hang up.{C.NC}")

        try:
            while client.is_call_active():
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n  {C.Y}Hanging up...{C.NC}")
            client.hangup()

        print_success("Call ended")
        return True
    else:
        print_error("Call failed to connect")
        return False


def _sip_call_sipx(dest, server, port, username, password, transport, config):
    """Make SIP call using sipx (async)."""
    import asyncio
    from sipx import AsyncClient, AuthDigest, Settings

    async def _call():
        settings = Settings(
            from_uri=f"sip:{username}@{server}",
            timeout=config.get("call", {}).get("timeout", 60.0),
        )
        auth = AuthDigest(username=username, password=password or "")

        async with AsyncClient(settings=settings, auth=auth) as client:
            print(f"  {C.Y}Registering with {server}...{C.NC}")
            reg_response = await client.register(f"sip:{server}:{port}")
            print_info("Register", f"{reg_response.status_code} {reg_response.reason}")

            if "@" in dest:
                dest_uri = f"sip:{dest}"
            else:
                dest_uri = f"sip:{dest}@{server}"

            print(f"  {C.Y}Calling {dest}...{C.NC}")
            call_response = await client.invite(dest_uri)

            if call_response.status_code < 300:
                print_success(f"Call connected! Status: {call_response.status_code}")
                print(f"  {C.DIM}Call in progress... Press Ctrl+C to hang up.{C.NC}")

                try:
                    await asyncio.sleep(config.get("call", {}).get("timeout", 60))
                except asyncio.CancelledError:
                    pass

                await client.bye()
                print_success("Call ended")
                return True
            else:
                print_error(f"Call rejected: {call_response.status_code} {call_response.reason}")
                return False

    return asyncio.run(_call())


# ──────────────────────────────────────────────────────────────
# BACKEND: PJSIP (pjsua2)
# ──────────────────────────────────────────────────────────────

def pjsip_make_call(destination: str, config: Dict[str, Any]) -> bool:
    """
    Make a SIP call using PJSIP/pjsua2 (most robust, but needs compiled C libs).
    """
    section_header("PJSIP CALL ENGINE")

    try:
        import pjsua2 as pj
    except ImportError:
        print_error("PJSIP bindings (pjsua2) not installed!")
        print(f"  {C.Y}Installation guide:{C.NC}")
        print(f"    1. git clone https://github.com/pjsip/pjproject.git")
        print(f"    2. cd pjproject && ./configure && make dep && make")
        print(f"    3. cd pjsip-apps/src/swig/python && make && sudo make install")
        print(f"  {C.DIM}Or use the pure SIP backend (Option 2) which needs no compilation.{C.NC}")
        return False

    sip_cfg = config.get("sip", {})
    server = sip_cfg.get("server") or os.getenv("SIP_SERVER")
    port = sip_cfg.get("port") or int(os.getenv("SIP_PORT", "5060"))
    username = sip_cfg.get("username") or os.getenv("SIP_USER")
    password = sip_cfg.get("password") or os.getenv("SIP_PASS")
    transport = sip_cfg.get("transport", "udp")
    domain = sip_cfg.get("domain") or server

    if not all([server, username]):
        print_error("SIP configuration incomplete!")
        return False

    print_info("Provider", f"{server}:{port} ({transport.upper()})")
    print_info("Username", username)
    print_info("Destination", destination)
    print()

    class MyCall(pj.Call):
        """Custom call class with state callbacks."""
        def onCallState(self, prm):
            ci = self.getInfo()
            state = ci.stateText
            if ci.state == pj.PJSIP_INV_STATE_CONFIRMED:
                print_success(f"Call connected! ({state})")
            elif ci.state == pj.PJSIP_INV_STATE_DISCONNECTED:
                print(f"  {C.Y}Call disconnected: {ci.lastReason}{C.NC}")

        def onCallMediaState(self, prm):
            ci = self.getInfo()
            for i in range(ci.mediaCnt):
                mi = self.getMedia(i)
                if mi.type == pj.PJMEDIA_TYPE_AUDIO and mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE:
                    am = pj.AudioMedia.typecastFromMedia(mi)
                    pj.Endpoint.instance().audDevManager().getCaptureDevMedia().startTransmit(am)
                    am.startTransmit(pj.Endpoint.instance().audDevManager().getPlaybackDevMedia())
                    print_success("Audio media connected")

    class MyAccount(pj.Account):
        """Custom account class."""
        def onRegState(self, prm):
            if prm.code >= 200 and prm.code < 300:
                print_success(f"Registered: {prm.reason} ({prm.code})")
            else:
                print_warning(f"Registration: {prm.reason} ({prm.code})")

    try:
        ep_cfg = pj.EpConfig()
        ep_cfg.uaConfig.maxCalls = 4
        ep = pj.Endpoint()
        ep.libCreate()
        ep.libInit(ep_cfg)

        tp_cfg = pj.TransportConfig()
        tp_cfg.port = 5062
        tp_type = pj.PJSIP_TRANSPORT_UDP
        if transport.lower() == 'tcp':
            tp_type = pj.PJSIP_TRANSPORT_TCP
        elif transport.lower() == 'tls':
            tp_type = pj.PJSIP_TRANSPORT_TLS

        tp = ep.transportCreate(tp_type, tp_cfg)
        ep.libStart()

        print(f"  {C.Y}PJSIP started on port {tp_cfg.port}{C.NC}")

        acc_cfg = pj.AccountConfig()
        acc_cfg.idUri = f"sip:{username}@{domain}"
        acc_cfg.regConfig.registrarUri = f"sip:{server}:{port}"

        cred = pj.AuthCredInfo("digest", "*", username, 0, password or "")
        acc_cfg.sipConfig.authCreds.append(cred)

        print(f"  {C.Y}Registering with {server}:{port}...{C.NC}")
        acc = MyAccount()
        acc.create(acc_cfg)

        time.sleep(1)

        if "@" in destination:
            dest_uri = f"sip:{destination}"
        else:
            dest_uri = f"sip:{destination}@{domain}:{port}"

        print(f"  {C.Y}Calling {destination}...{C.NC}")
        call = MyCall(acc, -1)
        call_prm = pj.CallOpParam()
        call.makeCall(dest_uri, call_prm)

        print(f"  {C.DIM}Call active... Press Ctrl+C to hang up.{C.NC}")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n  {C.Y}Hanging up...{C.NC}")
            call.hangup(pj.CallOpParam())
            time.sleep(0.5)

        ep.libDestroy()
        print_success("Call ended")
        return True

    except pj.Error as e:
        print_error(f"PJSIP error: {e.info() if hasattr(e, 'info') else str(e)}")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


# ──────────────────────────────────────────────────────────────
# CONFIGURATION SETUP WIZARD
# ──────────────────────────────────────────────────────────────

def setup_wizard():
    """Interactive configuration setup."""
    print_banner()
    section_header("CONFIGURATION WIZARD")

    config = load_config()

    print(f"  {C.Y}Choose your backend:{C.NC}")
    print(f"    {C.B}1{C.NC}. Twilio (call real phone numbers — requires free account)")
    print(f"    {C.B}2{C.NC}. SIP (generic SIP/VoIP — requires SIP provider)")
    print(f"    {C.B}3{C.NC}. PJSIP (advanced SIP — requires compiled libs)")
    print()

    choice = input(f"  {C.G}Select [1-3]{C.NC}: ").strip()

    if choice == "1":
        config["backend"] = "twilio"
        print(f"\n  {C.Y}Twilio Configuration:{C.NC}")
        print(f"  {C.DIM}Get these from https://console.twilio.com{C.NC}\n")

        sid = input(f"  Account SID: {C.G}{C.NC}").strip()
        token = input(f"  Auth Token: {C.G}{C.NC}").strip()
        frm = input(f"  Your Twilio number (e.g., +1234567890): {C.G}{C.NC}").strip()

        if sid: config["twilio"]["account_sid"] = sid
        if token: config["twilio"]["auth_token"] = token
        if frm: config["twilio"]["from_number"] = frm

    elif choice == "2":
        config["backend"] = "sip"
        print(f"\n  {C.Y}SIP Configuration:{C.NC}")
        print(f"  {C.DIM}Get these from your VoIP/SIP provider (e.g., VoIPstudio, Callcentric){C.NC}\n")

        server = input(f"  SIP server (e.g., sip.voipstudio.com): {C.G}{C.NC}").strip()
        port_s = input(f"  Port [5060]: {C.G}{C.NC}").strip()
        user = input(f"  Username: {C.G}{C.NC}").strip()
        pwd = input(f"  Password: {C.G}{C.NC}").strip()
        domain = input(f"  Domain [same as server]: {C.G}{C.NC}").strip()
        transp = input(f"  Transport (udp/tcp/tls) [udp]: {C.G}{C.NC}").strip().lower()

        if server: config["sip"]["server"] = server
        if port_s: config["sip"]["port"] = int(port_s)
        if user: config["sip"]["username"] = user
        if pwd: config["sip"]["password"] = pwd
        if domain: config["sip"]["domain"] = domain
        else: config["sip"]["domain"] = server
        if transp in ("udp", "tcp", "tls"): config["sip"]["transport"] = transp

        config["sip"]["from_uri"] = f"sip:{user}@{config['sip']['domain']}"

    elif choice == "3":
        config["backend"] = "pjsip"
        print(f"\n  {C.Y}PJSIP reuses SIP provider settings.{C.NC}")
        print(f"  Enter the same details as Option 2 above.\n")

        server = input(f"  SIP server: {C.G}{C.NC}").strip()
        port_s = input(f"  Port [5060]: {C.G}{C.NC}").strip()
        user = input(f"  Username: {C.G}{C.NC}").strip()
        pwd = input(f"  Password: {C.G}{C.NC}").strip()

        if server: config["sip"]["server"] = server
        if port_s: config["sip"]["port"] = int(port_s)
        if user: config["sip"]["username"] = user
        if pwd: config["sip"]["password"] = pwd
        config["sip"]["domain"] = config["sip"].get("domain") or server
        config["sip"]["from_uri"] = f"sip:{user}@{config['sip']['domain']}"

    print()
    msg = input(f"  Default voice message [Enter for default]: {C.G}{C.NC}").strip()
    if msg:
        config["call"]["say_message"] = msg

    print()
    save_config(config)

    print(f"\n  {C.G}✓ Setup complete!{C.NC}")
    print(f"  Run {C.Y}python wificall.py call +1234567890{C.NC} to make a call!")
    print(f"  Or {C.Y}python wificall.py interactive{C.NC} for interactive mode.\n")


# ──────────────────────────────────────────────────────────────
# INTERACTIVE MODE
# ──────────────────────────────────────────────────────────────

def interactive_mode():
    """Interactive CLI mode."""
    config = load_config()

    while True:
        print_banner()
        backend = config.get("backend", "twilio")

        print(f"  {C.B}Current Backend:{C.NC} {C.Y}{backend.upper()}{C.NC}")
        print()
        print(f"  {C.B}1{C.NC}. Make a call")
        print(f"  {C.B}2{C.NC}. Check configuration")
        print(f"  {C.B}3{C.NC}. Run setup wizard")
        print(f"  {C.B}4{C.NC}. Show available backends")
        print(f"  {C.B}5{C.NC}. Install dependencies")
        print(f"  {C.B}6{C.NC}. View call logs")
        print(f"  {C.B}7{C.NC}. Exit")
        print()

        choice = input(f"  {C.G}Select [1-7]{C.NC}: ").strip()

        if choice == "1":
            number = input(f"\n  Phone number or SIP URI: {C.G}{C.NC}").strip()
            msg = input(f"  Message to speak (or Enter for default): {C.G}{C.NC}").strip()
            print()
            make_call(number, config, msg if msg else None)
            input(f"\n  {C.DIM}Press Enter to continue...{C.NC}")

        elif choice == "2":
            show_config(config)
            input(f"\n  {C.DIM}Press Enter to continue...{C.NC}")

        elif choice == "3":
            setup_wizard()
            config = load_config()
            input(f"\n  {C.DIM}Press Enter to continue...{C.NC}")

        elif choice == "4":
            show_backends()
            input(f"\n  {C.DIM}Press Enter to continue...{C.NC}")

        elif choice == "5":
            install_deps()
            input(f"\n  {C.DIM}Press Enter to continue...{C.NC}")

        elif choice == "6":
            show_logs()
            input(f"\n  {C.DIM}Press Enter to continue...{C.NC}")

        elif choice == "7":
            print(f"\n  {C.Y}Goodbye!{C.NC}\n")
            break


def show_config(config):
    """Display current configuration."""
    section_header("CURRENT CONFIGURATION")
    print(f"  {C.B}Active backend:{C.NC} {C.Y}{config.get('backend', 'twilio')}{C.NC}\n")

    for section, values in config.items():
        if isinstance(values, dict):
            print(f"  {C.BOLD}[{section}]{C.NC}")
            for k, v in values.items():
                if v:
                    display = "****" if "password" in k.lower() or "token" in k.lower() else str(v)
                    print(f"    {k}: {C.G}{display}{C.NC}")
            print()

    print(f"  Config file: {C.C1}{CONFIG_FILE}{C.NC}")
    print(f"  Log file:    {C.C1}{LOG_FILE}{C.NC}")


def show_backends():
    """Show available backends and their status."""
    section_header("AVAILABLE BACKENDS")

    twilio_ok = False
    try:
        import twilio
        twilio_ok = True
    except ImportError:
        pass
    print(f"  {C.B}Twilio{C.NC}      — Real phone calls via API")
    print(f"    Status: {C.G}Available ✓{C.NC}  ({C.Y}pip install twilio{C.NC})" if twilio_ok else
          f"    Status: {C.R}Not installed ✗{C.NC}  ({C.Y}pip install twilio{C.NC})")
    print()

    sip_ok = False
    try:
        from simple_sip import SIPClient
        sip_ok = True
    except ImportError:
        pass
    print(f"  {C.B}Pure SIP{C.NC}    — SIP via simple-sip-client (pure Python)")
    print(f"    Status: {C.G}Available ✓{C.NC}  ({C.Y}pip install simple-sip-client{C.NC})" if sip_ok else
          f"    Status: {C.R}Not installed ✗{C.NC}  ({C.Y}pip install simple-sip-client{C.NC})")
    print()

    sipx_ok = False
    try:
        import sipx
        sipx_ok = True
    except ImportError:
        pass
    print(f"  {C.B}sipx{C.NC}        — Modern async SIP library")
    print(f"    Status: {C.G}Available ✓{C.NC}  ({C.Y}pip install sipx{C.NC})" if sipx_ok else
          f"    Status: {C.R}Not installed ✗{C.NC}  ({C.Y}pip install sipx{C.NC})")
    print()

    pjsip_ok = False
    try:
        import pjsua2 as pj
        pjsip_ok = True
    except ImportError:
        pass
    print(f"  {C.B}PJSIP{C.NC}       — Enterprise SIP via compiled C libs")
    print(f"    Status: {C.G}Available ✓{C.NC}  (compiled from source)" if pjsip_ok else
          f"    Status: {C.R}Not installed ✗{C.NC}  (requires compilation)")
    print()


def install_deps():
    """Install Python dependencies."""
    section_header("DEPENDENCY INSTALLER")

    packages = {
        "twilio": "Twilio Voice API (call real phone numbers)",
        "simple-sip-client": "Pure Python SIP client",
        "sipx": "Modern async SIP library"
    }

    print(f"  {C.Y}Available packages:{C.NC}\n")
    for i, (pkg, desc) in enumerate(packages.items(), 1):
        installed = False
        try:
            __import__(pkg.replace("-", "_"))
            installed = True
        except ImportError:
            pass
        status = f"{C.G}[✓] Installed{C.NC}" if installed else f"{C.R}[✗] Not installed{C.NC}"
        print(f"  {C.B}{i}.{C.NC} {pkg:25s} — {desc:40s} {status}")

    print(f"\n  {C.B}a{C.NC}. Install all")
    print(f"  {C.B}q{C.NC}. Cancel")
    print()

    choice = input(f"  {C.G}Select package to install [1-3/a/q]{C.NC}: ").strip().lower()

    if choice == "q":
        return

    targets = []
    if choice == "a":
        targets = list(packages.keys())
    elif choice in ("1", "2", "3"):
        targets = [list(packages.keys())[int(choice) - 1]]

    if not targets:
        print_warning("No valid selection")
        return

    for pkg in targets:
        print(f"\n  {C.Y}Installing {pkg}...{C.NC}")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", pkg],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print_success(f"{pkg} installed successfully!")
        else:
            print_error(f"Failed to install {pkg}: {result.stderr[:200]}")


def show_logs():
    """Display recent call logs."""
    section_header("CALL LOGS")
    if LOG_FILE.exists():
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
        for line in lines[-20:]:
            print(f"  {C.DIM}{line.strip()}{C.NC}")
        print(f"\n  {C.DIM}Full log: {LOG_FILE}{C.NC}")
    else:
        print(f"  {C.Y}No logs yet.{C.NC}")


# ──────────────────────────────────────────────────────────────
# MAIN CALL DISPATCHER
# ──────────────────────────────────────────────────────────────

def make_call(destination: str, config: Dict[str, Any], message: str = None) -> bool:
    """Dispatch a call to the configured backend."""
    backend = config.get("backend", "twilio")

    if not destination:
        print_error("No destination specified!")
        return False

    print_banner()

    print(f"  {C.B}Backend:{C.NC}   {C.Y}{backend.upper()}{C.NC}")
    print(f"  {C.B}To:{C.NC}       {destination}")
    print(f"  {C.B}Time:{C.NC}     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    if backend == "twilio":
        return twilio_make_call(destination, config, message)
    elif backend == "sip":
        return sip_make_call(destination, config)
    elif backend == "pjsip":
        return pjsip_make_call(destination, config)
    else:
        print_error(f"Unknown backend: {backend}")
        return False


# ──────────────────────────────────────────────────────────────
# CLI ENTRY POINT
# ──────────────────────────────────────────────────────────────

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="WiFiCall — Make VoIP calls over WiFi without a SIM card",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(f"""
        {C.Y}Examples:{C.NC}
          python wificall.py setup                    Run interactive setup wizard
          python wificall.py call +1234567890          Call a phone number (Twilio backend)
          python wificall.py call sip:user@domain.com  Call a SIP URI (SIP backend)
          python wificall.py call --message "Hi!" +1234567890
          python wificall.py interactive               Launch interactive mode
          python wificall.py --backend sip call +1234567890
          python wificall.py info                      Show configuration & backends

        {C.DIM}Configuration stored in: ~/.wificall/config.json{C.NC}
        """)
    )

    parser.add_argument('--backend', '-b', choices=['twilio', 'sip', 'pjsip'],
                        help='Override backend for this call')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    parser.add_argument('--message', '-m', type=str,
                        help='Message to speak (Twilio backend)')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    call_parser = subparsers.add_parser('call', help='Make a call')
    call_parser.add_argument('destination', type=str,
                             help='Phone number (+1234567890) or SIP URI')
    call_parser.add_argument('--message', '-m', type=str,
                             help='Message to speak')

    subparsers.add_parser('setup', help='Run configuration wizard')

    subparsers.add_parser('interactive', aliases=['i', 'tui'],
                          help='Interactive mode')

    inf_parser = subparsers.add_parser('info', help='Show configuration and backends')

    subparsers.add_parser('install', help='Install dependencies')

    if len(sys.argv) == 1:
        parser.print_help()
        print()
        print(f"  {C.Y}Tip:{C.NC} Run {C.B}python wificall.py setup{C.NC} to configure, or")
        print(f"       Run {C.B}python wificall.py interactive{C.NC} for interactive mode.")
        print()
        return

    args = parser.parse_args()

    config = load_config()

    if args.backend:
        config['backend'] = args.backend

    if args.verbose:
        setup_logging()

    if args.command == 'setup':
        setup_wizard()

    elif args.command in ('interactive', 'i', 'tui'):
        interactive_mode()

    elif args.command == 'call':
        msg = args.message or config.get("call", {}).get("say_message")
        make_call(args.destination, config, msg)

    elif args.command == 'info':
        show_config(config)
        show_backends()

    elif args.command == 'install':
        install_deps()

    else:
        parser.print_help()


# ──────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {C.Y}Interrupted by user.{C.NC}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n  {C.R}Unexpected error: {e}{C.NC}\n")
        sys.exit(1)
