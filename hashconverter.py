#!/usr/bin/env python3
"""
CTF Hash Cracker Helper
========================

A helper tool for CTF cryptography challenges: automatically identifies the
hash type, prepares the correct format, then calls the official cracking
tool already INSTALLED on your system (Hashcat / John the Ripper /
RainbowCrack) - the whole flow runs end-to-end (straight into a wordlist
attack) without any manual copy-pasting.

Output colors:
- RED    : the hash after it's been "converted" / ready for the target tool
- YELLOW : the cracked result that was found

Wordlist:
- If you don't have a wordlist yet, the tool automatically creates
  'wordlist.txt' in the working directory - it first tries to download a
  common-password list (10k-most-common from SecLists), and falls back to
  a small built-in list if there's no internet connection. This wordlist
  only contains common/publicly leaked passwords - its effectiveness is
  limited compared to a large wordlist like rockyou.txt.

IMPORTANT - SCOPE & ETHICS:
- This script does NOT crack anything by itself. It's purely a wrapper /
  format converter that calls official binaries (hashcat, john, rcrack).
- Use it ONLY on hashes you own, or on legitimate CTF challenges.
- CrackStation & OnlineHashCrack are intentionally NOT included because
  both are web-only services (you'd have to upload the hash to a third
  party's server), not native Linux CLI tools.

License: MIT (see LICENSE)
"""

import subprocess
import re
import os
import sys
import tempfile
import shutil
import urllib.request
import urllib.error

# ---------------------------------------------------------------------------
# Terminal colors (ANSI)
# ---------------------------------------------------------------------------
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

CONVERT_COLOR = RED     # hash after conversion / ready for the target tool
CRACK_COLOR = YELLOW    # successfully cracked result
INFO_COLOR = GREEN
WARN_COLOR = YELLOW
CMD_COLOR = CYAN


def c(text, color):
    return f"{color}{text}{RESET}"


# ---------------------------------------------------------------------------
# 1. Hash type identification
#    Each entry: (display_name, hashcat_mode, john_format)
# ---------------------------------------------------------------------------
def identify_hash(h):
    h = h.strip()
    matches = []

    if re.match(r'^\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}$', h):
        matches.append(('bcrypt', 3200, 'bcrypt'))
    if re.match(r'^\$1\$', h):
        matches.append(('MD5 crypt - Unix ($1$)', 500, 'md5crypt'))
    if re.match(r'^\$5\$', h):
        matches.append(('SHA256 crypt - Unix ($5$)', 7400, 'sha256crypt'))
    if re.match(r'^\$6\$', h):
        matches.append(('SHA512 crypt - Unix ($6$)', 1800, 'sha512crypt'))
    if re.match(r'^\$[PH]\$', h):
        matches.append(('phpass (WordPress / phpBB)', 400, 'phpass'))
    if re.match(r'^[a-fA-F0-9]{32}$', h):
        matches.append(('MD5', 0, 'Raw-MD5'))
        matches.append(('NTLM', 1000, 'NT'))
    if re.match(r'^[a-fA-F0-9]{40}$', h):
        matches.append(('SHA1', 100, 'Raw-SHA1'))
    if re.match(r'^[a-fA-F0-9]{56}$', h):
        matches.append(('SHA224', 1300, 'Raw-SHA224'))
    if re.match(r'^[a-fA-F0-9]{64}$', h):
        matches.append(('SHA256', 1400, 'Raw-SHA256'))
    if re.match(r'^[a-fA-F0-9]{96}$', h):
        matches.append(('SHA384', 10800, 'Raw-SHA384'))
    if re.match(r'^[a-fA-F0-9]{128}$', h):
        matches.append(('SHA512', 1700, 'Raw-SHA512'))

    return matches


def which(tool):
    return shutil.which(tool)


def detect_available_tools():
    """Detect which cracking tools are already installed, so the user
    never gets stuck picking a tool that isn't actually available."""
    avail = []
    if which('hashcat'):
        avail.append(('Hashcat', 'hashcat'))
    if which('john'):
        avail.append(('John the Ripper', 'john'))
    if which('rcrack'):
        avail.append(('RainbowCrack', 'rainbowcrack'))
    return avail


# ---------------------------------------------------------------------------
# Auto-detect wordlist / rainbow table, so the user doesn't need to type a
# manual path when it's already in a standard location
# ---------------------------------------------------------------------------
COMMON_WORDLISTS = [
    "wordlist.txt",
    os.path.join(os.getcwd(), "wordlist.txt"),
    "/usr/share/wordlists/rockyou.txt",
    os.path.expanduser("~/rockyou.txt"),
    os.path.expanduser("~/wordlists/rockyou.txt"),
    "/opt/wordlists/rockyou.txt",
]

COMMON_RT_DIRS = [
    "/opt/rainbowcrack/tables",
    os.path.expanduser("~/rainbowcrack/tables"),
    "./tables",
]

# Name & source of the wordlist that gets auto-generated if the user
# doesn't have one yet
DEFAULT_WORDLIST_NAME = "wordlist.txt"
DEFAULT_WORDLIST_URL = (
    "https://raw.githubusercontent.com/danielmiessler/SecLists/"
    "master/Passwords/Common-Credentials/10k-most-common.txt"
)

# Offline fallback (used if the download fails - no internet, etc.) so the
# tool can still run without needing any external wordlist.
BUILTIN_COMMON_PASSWORDS = [
    "123456", "password", "12345678", "qwerty", "123456789", "12345",
    "1234", "111111", "1234567", "dragon", "123123", "baseball",
    "abc123", "football", "monkey", "letmein", "shadow", "master",
    "696969", "michael", "mustang", "jordan", "superman", "harley",
    "1234567890", "hunter", "trustno1", "ranger", "buster", "thomas",
    "tigger", "robert", "soccer", "batman", "test", "pass", "killer",
    "hockey", "george", "andrew", "charlie", "starwars", "admin",
    "admin123", "root", "toor", "welcome", "iloveyou", "princess",
    "login", "passw0rd", "solo", "flower", "loveme", "password1",
    "qwertyuiop", "654321", "666666", "1qaz2wsx", "121212", "000000",
    "qazwsx", "michelle", "sunshine", "chocolate", "password123",
    "computer", "amanda", "internet", "samantha", "summer", "sparky",
    "corvette", "bigdog", "cheese", "matthew", "patrick", "martin",
    "freedom", "ginger", "biteme", "test123", "guest", "changeme",
    "letmein1", "qwerty123", "asdf1234", "zxcvbnm", "aaaaaa", "abcd1234",
]


def find_wordlist():
    for path in COMMON_WORDLISTS:
        if os.path.isfile(path):
            return path
    return None


def ensure_wordlist():
    """Find an available wordlist. If the user doesn't have one at all,
    automatically create 'wordlist.txt' - try downloading a common-password
    list first, and fall back to the built-in list if that fails (e.g. no
    internet connection)."""
    wl = find_wordlist()
    if wl:
        return wl

    target = os.path.join(os.getcwd(), DEFAULT_WORDLIST_NAME)
    print(c(f"[!] No wordlist found, auto-creating '{DEFAULT_WORDLIST_NAME}'...", WARN_COLOR))

    try:
        req = urllib.request.Request(DEFAULT_WORDLIST_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
        with open(target, 'wb') as f:
            f.write(data)
        count = data.count(b'\n')
        print(c(f"[+] Downloaded common wordlist ({count} words) -> {target}", INFO_COLOR))
    except Exception:
        with open(target, 'w') as f:
            f.write("\n".join(BUILTIN_COMMON_PASSWORDS) + "\n")
        print(c(f"[!] Download failed (check your internet connection), using the "
                f"built-in common-password list ({len(BUILTIN_COMMON_PASSWORDS)} words) -> {target}", WARN_COLOR))

    return target


def find_rt_dir():
    for d in COMMON_RT_DIRS:
        if os.path.isdir(d) and any(fn.endswith('.rt') for fn in os.listdir(d)):
            return d
    return None


# ---------------------------------------------------------------------------
# 2 & 3. "Convert" the hash -> ready-to-use format for the target tool (RED)
# ---------------------------------------------------------------------------
def prepare_hash_file(hash_value):
    f = tempfile.NamedTemporaryFile('w', suffix='.hash', delete=False)
    f.write(hash_value.strip() + "\n")
    f.close()
    return f.name


# ---------------------------------------------------------------------------
# 4 & 5. Run the tool, show the successfully cracked result in YELLOW
# ---------------------------------------------------------------------------
def run_hashcat(hash_value, mode):
    hash_file = prepare_hash_file(hash_value)
    print(c(f"[+] Hash converted -> Hashcat (-m {mode}): {hash_value.strip()}", CONVERT_COLOR))

    wl = ensure_wordlist()

    cmd = ['hashcat', '-m', str(mode), '-a', '0', hash_file, wl, '--force', '--quiet']
    print(c(f"[*] Running: {' '.join(cmd)}", CMD_COLOR))
    subprocess.run(cmd)

    show = subprocess.run(['hashcat', '-m', str(mode), hash_file, '--show'],
                           capture_output=True, text=True)
    os.unlink(hash_file)

    if show.stdout.strip():
        print(c("\n[CRACK RESULT]", BOLD))
        for line in show.stdout.strip().splitlines():
            print(c(line, CRACK_COLOR))
    else:
        print(c("[!] Hash was not cracked with this wordlist.", WARN_COLOR))


def run_john(hash_value, john_format):
    hash_file = prepare_hash_file(hash_value)
    print(c(f"[+] Hash converted -> John ({john_format}): {hash_value.strip()}", CONVERT_COLOR))

    wl = ensure_wordlist()

    cmd = ['john', f'--format={john_format}', f'--wordlist={wl}', hash_file]
    print(c(f"[*] Running: {' '.join(cmd)}", CMD_COLOR))
    subprocess.run(cmd)

    show = subprocess.run(['john', f'--format={john_format}', '--show', hash_file],
                           capture_output=True, text=True)
    os.unlink(hash_file)

    lines = [l for l in show.stdout.strip().splitlines()
             if l and not l.lower().startswith('0 password')]
    if lines:
        print(c("\n[CRACK RESULT]", BOLD))
        for line in lines:
            print(c(line, CRACK_COLOR))
    else:
        print(c("[!] Hash was not cracked with this wordlist.", WARN_COLOR))


def run_rainbowcrack(hash_value):
    print(c(f"[+] Hash converted -> RainbowCrack: {hash_value.strip()}", CONVERT_COLOR))

    td = find_rt_dir()
    if not td:
        td = input("Rainbow table folder (.rt) not found automatically, enter path: ").strip()
    if not td or not os.path.isdir(td):
        print(c("[!] Invalid rainbow table folder, aborting.", WARN_COLOR))
        return

    cmd = ['rcrack', td, '-h', hash_value.strip()]
    print(c(f"[*] Running: {' '.join(cmd)}", CMD_COLOR))
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)

    found = False
    for line in result.stdout.splitlines():
        low = line.lower()
        if 'hex:' in low and 'not found' not in low:
            found = True
            print(c(line, CRACK_COLOR))
    if not found:
        print(c("[!] Hash not found in the available rainbow table.", WARN_COLOR))


# ---------------------------------------------------------------------------
# Main - streamlined flow: minimal manual input
# ---------------------------------------------------------------------------
def main():
    print(c("=== CTF Hash Cracker Helper ===", BOLD))
    print("Use only on hashes you own, or on legitimate CTF challenges.\n")

    avail = detect_available_tools()
    if not avail:
        print(c("[!] No cracking tool detected (hashcat/john/rcrack).", WARN_COLOR))
        print("    Install at least one: sudo apt install hashcat john -y")
        return

    h = input("1) Enter the hash: ").strip()
    if not h:
        print("Empty hash, exiting.")
        return

    matches = identify_hash(h)
    if not matches:
        print(c("[!] Hash type not automatically recognized.", WARN_COLOR))
        return

    print("\nPossible hash types detected:")
    for i, (name, hc_mode, john_fmt) in enumerate(matches, 1):
        print(f"  {i}. {name}")
    idx = 0
    if len(matches) > 1:
        try:
            idx = int(input(f"Choose hash type [1-{len(matches)}]: ")) - 1
            if idx < 0 or idx >= len(matches):
                idx = 0
        except ValueError:
            idx = 0
    name, hc_mode, john_fmt = matches[idx]
    print(c(f"[+] Hash type: {name}", INFO_COLOR))

    print("\n2) Tools available on your system:")
    for i, (label, _) in enumerate(avail, 1):
        print(f"  {i}. {label}")
    choice = input(f"Choose a tool [1-{len(avail)}]: ").strip()
    try:
        _, key = avail[int(choice) - 1]
    except (ValueError, IndexError):
        print("Invalid choice.")
        return

    if key == 'hashcat':
        run_hashcat(h, hc_mode)
    elif key == 'john':
        run_john(h, john_fmt)
    elif key == 'rainbowcrack':
        run_rainbowcrack(h)


if __name__ == "__main__":
    main()
