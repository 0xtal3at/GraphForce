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

            # Capture Unknown field
            match1 = re.search(r"Unknown field '([^']+)'", response.text)
            if match1:
                found = match1.group(1)
                if found not in suggestions:
                    suggestions.add(found)

            # Improved: Capture all "Did you mean" suggestions
            match2 = re.search(r'Did you mean ([^?]+)\?', response.text)
            if match2:
                suggestions_str = match2.group(1)
                found_suggestions = re.findall(r'"([^"]+)"|(\w+)', suggestions_str)
                for match in found_suggestions:
                    found = match[0] if match[0] else match[1]
                    if found and found not in suggestions:
                        suggestions.add(found)

        except Exception as e:
            print(f"[-] Error: {e}")

except KeyboardInterrupt:
    print("\n[!] Interrupted by user (Ctrl+C)")

finally:
    if suggestions:
        # Clean up suggestions before saving them
        cleaned_suggestions = [item.strip("\\") for item in suggestions]

        with open("results.txt", "w") as f:
            for item in sorted(cleaned_suggestions):
                f.write(item + "\n")

        print(f"\n[✔] Done! {len(cleaned_suggestions)} suggestions saved to results.txt.")
    else:
        print("[!] No suggestions found.")

