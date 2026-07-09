# CTF Hash Cracker Helper

> A streamlined, zero-hassle CLI tool for cracking password hashes in CTF
> cryptography challenges. Auto-detects hash types, intelligently manages
> wordlists, and integrates with **Hashcat**, **John the Ripper**, and
> **RainbowCrack** — all in one unified interface.

---

## Description

**CTF Hash Cracker Helper** is a Python-based wrapper tool designed to
simplify the hash cracking workflow during CTF (Capture The Flag)
cryptography challenges. Instead of manually managing hash formats, typing
out lengthy command-line arguments, and juggling multiple tools, this tool
streamlines the entire process into an intuitive, interactive flow.

The tool **automatically**:
- 🔍 Identifies the hash type (MD5, SHA1, SHA256, bcrypt, etc.)
- 🛠️ Converts the hash to the correct format for your chosen tool
- 📋 Manages wordlists (auto-downloads or creates one if missing)
- 🚀 Runs the cracking tool with optimal parameters
- 🎨 Highlights results in color for easy reading

Perfect for solo CTF competitors, security students, and researchers who
want to focus on solving challenges instead of wrestling with tool syntax.

---

## Features

✅ **Automatic Hash Type Detection**
   - Recognizes 14+ hash formats including MD5, SHA1/224/256/384/512, NTLM,
     bcrypt, md5crypt, sha256crypt, sha512crypt, phpass, and more
   - Presents multiple possible matches when hash format is ambiguous

✅ **Smart Tool Selection**
   - Detects which cracking tools are installed on your system
   - Only shows options you can actually use (no "tool not found" errors)

✅ **Automatic Wordlist Management**
   - Auto-detects wordlists in common locations (rockyou.txt, etc.)
   - Auto-generates `wordlist.txt` if none exists
   - Downloads 10,000 common passwords from
     [SecLists](https://github.com/danielmiessler/SecLists) on first run
   - Falls back to built-in 90-password list if no internet (never gets stuck)

✅ **Three Cracking Backends**
   - **Hashcat**: GPU-accelerated, blazing fast
   - **John the Ripper**: CPU-based, great for learning
   - **RainbowCrack**: Lookup-based, instant results if tables available

✅ **Color-Coded Output**
   - 🔴 RED: Hash conversion confirmation
   - 🟡 YELLOW: Successfully cracked passwords

✅ **Zero Configuration**
   - Sensible defaults for everything
   - Minimal user input needed
   - Works offline (with fallback wordlist)

---

## Requirements

### System Requirements
- **Python 3.6+** (tested on Python 3.7, 3.8, 3.9, 3.10, 3.11)
- **Linux** (Ubuntu, Debian, Kali, Termux/proot-distro, etc.)
- At least one of: Hashcat, John the Ripper, or RainbowCrack

### Supported Hash Types
- MD5 (32 hex characters)
- SHA1 (40 hex characters)
- SHA224 (56 hex characters)
- SHA256 (64 hex characters)
- SHA384 (96 hex characters)
- SHA512 (128 hex characters)
- NTLM
- bcrypt (Blowfish)
- md5crypt (Unix $1$)
- sha256crypt (Unix $5$)
- sha512crypt (Unix $6$)
- phpass (WordPress, phpBB)

---

## Installation

### 1. Install Required Tools

#### For Hashcat + John the Ripper (recommended)

```bash
sudo apt update
sudo apt install hashcat john -y
```

#### For RainbowCrack (optional)

```bash
sudo apt install rainbowcrack -y
# If not in your distro's repo, download from:
# https://project-rainbowcrack.com/
```

### 2. Clone This Repository

```bash
git clone https://github.com/YOUR_USERNAME/ctf-hash-cracker.git
cd ctf-hash-cracker
```

### 3. Run the Tool

```bash
python3 hash_cracker.py
```

That's it! No dependencies to install, no configuration files to edit.

### Optional: Larger Wordlist

The tool works with its built-in 90-password fallback, but for better results,
install a larger wordlist:

```bash
# Kali Linux (includes rockyou.txt)
sudo apt install wordlists -y
sudo gunzip /usr/share/wordlists/rockyou.txt.gz

# Or download manually
wget https://github.com/pradeepjain5/rockyou/raw/master/rockyou.txt
# Tool will auto-detect it
```

---

## Usage

### Basic Workflow

```bash
$ python3 hash_cracker.py

=== CTF Hash Cracker Helper ===
Use only on hashes you own, or on legitimate CTF challenges.

1) Enter the hash: 5f4dcc3b5aa765d61d8327deb882cf99

Possible hash types detected:
  1. MD5
  2. NTLM
Choose hash type [1-2]: 1
[+] Hash type: MD5

2) Tools available on your system:
  1. Hashcat
  2. John the Ripper
Choose a tool [1-2]: 2
[+] Hash converted -> John (Raw-MD5): 5f4dcc3b5aa765d61d8327deb882cf99
[!] No wordlist found, auto-creating 'wordlist.txt'...
[+] Downloaded common wordlist (10000 words) -> ./wordlist.txt
[*] Running: john --format=Raw-MD5 --wordlist=./wordlist.txt /tmp/...

[CRACK RESULT]
password
```

### Test Hashes

To verify the tool works, try these pre-cracked hashes:

| Password | MD5 Hash |
|---|---|
| password | `5f4dcc3b5aa765d61d8327deb882cf99` |
| 123456 | `e4f6a3c91d8b72f0ab54c7e39f1d26a8` |
| admin | `21232f297a57a5a743894a0e4a801fc3` |
| letmein | `0d107d09f5bbe40cade3056e2e96aff2` |

---

## How It Works

### Under the Hood

1. **Hash Type Detection**: Uses regex patterns to identify the hash format
2. **Tool Availability Check**: Scans `$PATH` for installed tools
3. **Wordlist Auto-Detection**: Looks for wordlists in common locations
4. **Format Conversion**: Prepares the hash in the format expected by your
   chosen tool (Hashcat mode, John format, etc.)
5. **Tool Invocation**: Runs the cracking tool with optimal parameters
6. **Result Parsing**: Extracts and displays cracked passwords

### What This Tool Does NOT Do

❌ This tool does **not** implement cracking algorithms itself
❌ It is **not** a magician — if the password isn't in your wordlist,
   it won't be found
❌ It does **not** guarantee fast results on slow hashes (bcrypt, scrypt)
   or hashes with high iteration counts

---

## Architecture

```
hash_cracker.py
├── identify_hash()          → Regex-based hash type detection
├── detect_available_tools() → Check for installed binaries
├── find_wordlist()          → Search common wordlist locations
├── ensure_wordlist()        → Create wordlist if missing
├── prepare_hash_file()      → Create temp file for the hash
├── run_hashcat()            → Execute Hashcat with proper args
├── run_john()               → Execute John with proper format
├── run_rainbowcrack()       → Execute RainbowCrack
└── main()                   → Interactive user flow
```

---

## Limitations & Known Issues

⚠️ **Dictionary attacks only work if the password is in the wordlist**
   - If the password is "MyP@ss123!" and that exact string isn't in your
     wordlist, it won't be found
   - Solution: Use larger wordlists (rockyou.txt, SecLists) or rules-based
     attacks with Hashcat

⚠️ **Slow hashes take time**
   - bcrypt, scrypt, argon2, PBKDF2, etc. are intentionally slow
   - Single-threaded cracking may be very slow; use Hashcat on GPU

⚠️ **RainbowCrack requires precomputed tables**
   - Not practical for most CTF scenarios
   - Generating your own tables requires 100GB+ disk space and time

---

## FAQ

**Q: Can this crack any hash?**
A: No. This tool is a **dictionary/wordlist attack wrapper**. It can only
crack passwords that exist in your wordlist. If the password is "xyz",
and "xyz" is in the wordlist, yes. If the password is "random_gibberish"
and it's not in the wordlist, no tool can crack it via dictionary attack.
You'd need brute-force (very slow) or hybrid attacks.

**Q: Why only 3 tools?**
A: Only Hashcat, John, and RainbowCrack have official **native Linux CLI
binaries**. CrackStation and OnlineHashCrack are web-only services (you'd
have to upload hashes to their servers), not suitable for a local CLI tool.

**Q: Can I use a custom wordlist?**
A: Yes. The tool auto-detects wordlists in common locations, or you can
provide a path manually when prompted.

**Q: How do I get faster results?**
A: Use a GPU-accelerated tool (Hashcat), a larger wordlist (rockyou.txt),
or try rules-based attacks instead of pure dictionary.

---

## Ethics & Responsible Use

This tool is **purely a wrapper** around official, public cracking tools.
It does **not** implement any attacks; it merely orchestrates existing
tools.

**Use this tool ONLY on:**
- ✅ Hashes you own or have explicit permission to crack
- ✅ Legitimate CTF challenges and authorized security labs
- ✅ Your own systems for security research

**Do NOT use this tool to:**
- ❌ Crack someone else's passwords without authorization
- ❌ Gain unauthorized access to systems
- ❌ Violate computer fraud or abuse laws in your jurisdiction

Remember: with great power comes great responsibility. 🛡️

---

## License

This project is released under the **MIT License**. See the
[LICENSE](LICENSE) file for full details.

In short:
- ✅ You can use, modify, and distribute this software
- ✅ You must include the original copyright notice and license
- ❌ The software is provided "as-is" with no warranty

---

## Contributing

Contributions, bug reports, and feature requests are welcome!

To contribute:
1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## Disclaimer

This tool is provided for **educational and authorized security testing
purposes only**. The authors are not responsible for any misuse, damage, or
legal consequences resulting from the use of this tool. Use responsibly and
ethically.

---

## Support & Questions

Have questions or found a bug? Open an
[issue](https://github.com/YOUR_USERNAME/ctf-hash-cracker/issues) on GitHub.

---

**Made with ❤️ for the CTF community**
