import requests
import argparse
import re

print(r"""
  ____                 _     _____
 / ___|_ __ __ _ _ __ | |__ |  ___|__  _ __ ___ ___
| |  _| '__/ _` | '_ \| '_ \| |_ / _ \| '__/ __/ _ \
| |_| | | | (_| | |_) | | | |  _| (_) | | | (_|  __/
 \____|_|  \__,_| .__/|_| |_|_|  \___/|_|  \___\___|
                |_|
            GraphQL Suggestion Brute Forcer
                  Coded by Tal3at
""")

# =========== PARSE ARGUMENTS ==========
parser = argparse.ArgumentParser(description="GraphForce - GraphQL Suggestion Brute Forcer (Intruder-style)")
parser.add_argument('-r', '--request', required=True, help='Path to raw HTTP request file')
parser.add_argument('-w', '--fuzzlist', required=True, help='Path to fuzzing wordlist file')
args = parser.parse_args()

request_file_path = args.request
wordlist_path = args.fuzzlist

# =========== LOAD DATA ==========
with open(wordlist_path, "r") as f:
    mutations = [line.strip() for line in f if line.strip()]

with open(request_file_path, "r") as f:
    raw_request = f.read()

# Split raw request into lines
lines = raw_request.splitlines()
method, path, _ = lines[0].split()

# Extract headers
headers = {}
i = 1
while i < len(lines):
    line = lines[i]
    if line.strip() == '':
        i += 1
        break
    if ':' in line:
        key, value = line.split(':', 1)
        headers[key.strip()] = value.strip()
    i += 1

# Extract body
body = '\n'.join(lines[i:])

# Host and protocol
if 'Host' not in headers:
    raise Exception("Host header is required in request file")
host = headers['Host']
protocol = "https" if "HTTP/2" in raw_request else "http"
url = f"{protocol}://{host}{path}"

# =========== BRUTEFORCE ==========
suggestions = set()

# Find placeholder pattern(s) like $example$
placeholders = re.findall(r'\$(\w+)\$', body)
if not placeholders:
    print("[-] No placeholders like $example$ found in the request body.")
    exit()

try:
    for mutation in mutations:
        # Replace all placeholders with current mutation
        mutated_body = body
        for placeholder in placeholders:
            mutated_body = mutated_body.replace(f"${placeholder}$", mutation)

        try:
            response = requests.post(url, headers=headers, data=mutated_body.encode())

            # Capture all "Unknown field" suggestions
            unknown_fields = re.findall(r"Unknown field '([^']+)'", response.text)
            for found in unknown_fields:
                if found not in suggestions:
                    suggestions.add(found)
                    print(f"[+] Suggestion found: {found}")

            # Capture all "Did you mean" suggestions
            did_you_mean_matches = re.findall(r'Did you mean ([^?]+)\?', response.text)
            for suggestions_str in did_you_mean_matches:
                found_suggestions = re.findall(r'"([^"]+)"|(\w+)', suggestions_str)
                for match in found_suggestions:
                    found = match[0] if match[0] else match[1]
                    if found and found not in suggestions:
                        suggestions.add(found)
                        print(f"[+] Suggestion found: {found}")

        except Exception as e:
            print(f"[-] Error: {e}")

except KeyboardInterrupt:
    print("\n[!] Interrupted by user (Ctrl+C)")

finally:
    if suggestions:
        cleaned_suggestions = [item.strip("\\") for item in suggestions]
        with open("results.txt", "w") as f:
            for item in sorted(cleaned_suggestions):
                f.write(item + "\n")
        print(f"\n[✔] Done! {len(cleaned_suggestions)} suggestions saved to results.txt.")
    else:
        print("[!] No suggestions found.")
