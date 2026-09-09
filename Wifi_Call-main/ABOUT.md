
# About WiFiCall

## What is WiFiCall?

WiFiCall is a **pure-Python VoIP calling application** that enables voice calls over WiFi without any SIM card or cellular service. It was designed for penetration testers, security researchers, and developers who need programmatic voice calling capabilities.

## Why?

Traditional phone calls require a SIM card tied to a cellular carrier. This creates limitations:
- You need physical access to a SIM
- Calls are traceable to your carrier
- No API for automation
- Hard to integrate into security testing workflows

WiFiCall solves this by using **Voice over IP (VoIP)** protocols over any internet connection — WiFi, Ethernet, or even mobile data.
                                                                        ## How It Works
                                                                        ```
┌─────────────┐     SIP/HTTPS      ┌──────────────┐     PSTN/SIP      ┌──────────┐
│  WiFiCall   │ ──────────────────→ │  VoIP Provider │ ──────────────→ │  Phone   │
│ (Python)    │ ←────────────────── │ (Twilio/SIP)  │ ←────────────── │ (Target) │
└─────────────┘     RTP Audio       └──────────────┘                  └──────────┘


1. WiFiCall registers with a VoIP provider (Twilio, VoIPstudio, etc.) over your internet connection
2. It initiates a call via SIP or REST API
3. The provider bridges the call to the PSTN (public phone network) or to another SIP endpoint
4. Two-way audio flows over your internet connection via RTP

## Use Cases

- **Penetration Testing** — Vishing (voice phishing) simulations, social engineering assessments
- **Security Research** — Testing VoIP infrastructure, SIP server security
- **Automated Calling** — Alert systems, notifications, IVR testing
- **Privacy** — Make calls without exposing your personal phone number
- **Development** — Build voice-enabled applications with Python