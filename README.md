# CTF Hash Cracker Helper

A streamlined, zero-hassle CLI tool for cracking password
hashes in CTF cryptography challenges. Auto-detects hash types,
integrates with Hashcat, John the Ripper, and RainbowCrack -
all in one unified interface

# Descryption

CTF Hash Cracker Helper is a Python-based wrapper tool designed to
simplify the hash cracking workflow during CTF (Capture The Flag)
cryptography challenges. Instead of manually managing hash formats, typing
out lengthy command-line arguments, and juggling multiple tools, this tool
streamlines the entire process into an intuitive, interactive flow.

The tool automatically:

• 🔍 Identifies the hash type (MD5, SHA1, SHA256, bcrypt, etc.)
• 🛠️ Converts the hash to the correct format for your chosen tool
• 📋 Manages wordlists (auto-downloads or creates one if missing)
• 🚀 Runs the cracking tool with optimal parameters
• 🎨 Highlights results in color for easy reading
Perfect for solo CTF competitors, security students, and researchers who
want to focus on solving challenges instead of wrestling with tool syntax.

# Features

**✅ Automatic Hash Type Detection**
• Recognizes 14+ hash formats including MD5, SHA1/224/256/384/512, NTLM,
bcrypt, md5crypt, sha256crypt, sha512crypt, phpass, and more.
• Presents multiple possible matches when hash format is ambiguous.
**✅ Smart Tool Selection**
• Detects which cracking tools are installed on your system.
• Only shows options you can actually use (no "tool not found" errors).
**✅ Automatic Wordlist Management**
• Auto-detects wordlists in common locations (rockyou.txt, etc.).
• Auto-generates wordlist.txt if none exists.
• Downloads 10,000 common passwords from.
 SecLists on first run
• Falls back to built-in 90-password list if no internet (never gets stuck).
**✅ Three Cracking Backends**
• Hashcat: GPU-accelerated, blazing fast.
• John the Ripper: CPU-based, great for learning.
• RainbowCrack: Lookup-based, instant results if tables available.
**✅ Color-Coded Output**
• 🔴 RED: Hash conversion confirmation
• 🟡 YELLOW: Successfully cracked passwords
**✅ Zero Configuration**
• Sensible defaults for everything
• Minimal user input needed
• Works offline (with fallback wordlist)

# Requirements

System Requirements
• **Python 3.6+** (tested on Python 3.7, 3.8, 3.9, 3.10, 3.11)
• **Linux** (Ubuntu, Debian, Kali, Termux/proot-distro, etc.)
• At least one of: Hashcat, John the Ripper, or RainbowCrack
**Supported Hash Types**
• MD5 (32 hex characters)
• SHA1 (40 hex characters)
• SHA224 (56 hex characters)
• SHA256 (64 hex characters)
• SHA384 (96 hex characters)
• SHA512 (128 hex characters)
• NTLM
• bcrypt (Blowfish)
• md5crypt (Unix 1)
• sha256crypt (Unix 5)
• sha512crypt (Unix 6)
• phpass (WordPress, phpBB)

# Installation

**1. Install Requaired Tools**
***For Hashcat + John the Ripper
(Recommended)***
```Bash```
sudo apt update
sudo apt install hashcat john -y

***For RainbowCrack (optional)***
```Bash```
sudo apt install rainbowcrack -y







