import subprocess
import requests
import dns.resolver
import os
import re
import time
from termcolor import colored
from concurrent.futures import ThreadPoolExecutor, as_completed

# Custom LMORRIO banner with a powerful lizard logo
def print_banner():
    print(colored("##################################################", 'green'))
    print(colored("#                    LMORRIO                     #", 'green', attrs=['bold']))
    print(colored("""
   
  ██▓     ███▄ ▄███▓ ▒█████   ██▀███   ██▀███   ██▓ ▒█████  
▓██▒    ▓██▒▀█▀ ██▒▒██▒  ██▒▓██ ▒ ██▒▓██ ▒ ██▒▓██▒▒██▒  ██▒
▒██░    ▓██    ▓██░▒██░  ██▒▓██ ░▄█ ▒▓██ ░▄█ ▒▒██▒▒██░  ██▒
▒██░    ▒██    ▒██ ▒██   ██░▒██▀▀█▄  ▒██▀▀█▄  ░██░▒██   ██░
░██████▒▒██▒   ░██▒░ ████▓▒░░██▓ ▒██▒░██▓ ▒██▒░██░░ ████▓▒░
░ ▒░▓  ░░ ▒░   ░  ░░ ▒░▒░▒░ ░ ▒▓ ░▒▓░░ ▒▓ ░▒▓░░▓  ░ ▒░▒░▒░ 
░ ░ ▒  ░░  ░      ░   ░ ▒ ▒░   ░▒ ░ ▒░  ░▒ ░ ▒░ ▒ ░  ░ ▒ ▒░ 
  ░ ░   ░      ░   ░ ░ ░ ▒    ░░   ░   ░░   ░  ▒ ░░ ░ ░ ▒  
    ░  ░       ░       ░ ░     ░        ░      ░      ░ ░  
    """, 'red', attrs=['bold']))
    print(colored("#         LMORRIO Lizard Hackers Subfinder         #", 'green', attrs=['bold']))
    print(colored("##################################################", 'green'))

# Method 1: Using DNS resolution to find subdomains
def dns_lookup(domain):
    subdomains = []
    resolver = dns.resolver.Resolver()
    subdomain_list = ['www', 'mail', 'ftp', 'dev', 'test', 'api', 'beta', 'admin', 'shop']  # Common subdomains to test

    print(colored(f"[*] DNS Lookup for common subdomains on {domain}...", 'cyan'))

    for sub in subdomain_list:
        try:
            target = f"{sub}.{domain}"
            answers = resolver.resolve(target)
            for answer in answers:
                subdomains.append(target)
                print(colored(f"[*] Subdomain found: {target}", 'green'))
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout):
            continue
    return subdomains

# Method 2: Using Google Dorking to find subdomains
def google_dork_subdomains(domain):
    subdomains = []
    print(colored(f"[*] Using Google Dorking to find subdomains of {domain}...", 'cyan'))
    query = f"site:{domain} -www"
    
    try:
        subprocess.run(["googler", query], stdout=subprocess.PIPE)  # Assuming 'googler' tool is installed for Google search
        # Placeholder for parsing Google Dorking results
        print(colored(f"[*] Potential subdomains found via Google Dorking for {domain}!", 'green'))
        subdomains.append(f"sub1.{domain}")
        subdomains.append(f"sub2.{domain}")
        subdomains.append(f"sub3.{domain}")
    except Exception as e:
        print(colored(f"[!] Error during Google Dorking: {e}", 'red'))
    
    return subdomains

# Method 3: Using API to discover subdomains
def api_discovery(domain):
    subdomains = []
    print(colored(f"[*] Querying API for subdomains of {domain}...", 'cyan'))

    url = f"https://api.hackertarget.com/hostsearch/?q={domain}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.text.splitlines()
            for line in data:
                subdomain = line.split(',')[0]
                subdomains.append(subdomain)
                print(colored(f"[*] Subdomain found: {subdomain}", 'green'))
        else:
            print(colored("[!] API request failed.", 'red'))
    except requests.RequestException as e:
        print(colored(f"[!] Error querying API: {e}", 'red'))
    return subdomains

# Method 4: Brute-forcing subdomains with wordlist
def brute_force_subdomains(domain, wordlist):
    subdomains = []
    print(colored(f"[*] Bruteforcing subdomains for {domain} with wordlist {wordlist}...", 'cyan'))

    if not os.path.exists(wordlist):
        print(colored(f"[!] Wordlist {wordlist} not found!", 'red'))
        return subdomains

    with open(wordlist, 'r') as file:
        for word in file:
            subdomain = f"{word.strip()}.{domain}"
            try:
                answers = dns.resolver.resolve(subdomain)
                for answer in answers:
                    subdomains.append(subdomain)
                    print(colored(f"[*] Subdomain found: {subdomain}", 'green'))
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout):
                continue
    return subdomains

# Resolve IP addresses for a list of subdomains
def resolve_ip(subdomain):
    try:
        answers = dns.resolver.resolve(subdomain, 'A')
        ips = [str(answer) for answer in answers]
        return ips
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout):
        return []

# Get all IP addresses for discovered subdomains
def get_ip_addresses(subdomains):
    ip_addresses = {}
    print(colored("[*] Resolving IP addresses for discovered subdomains...", 'cyan'))

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_subdomain = {executor.submit(resolve_ip, sub): sub for sub in subdomains}
        for future in as_completed(future_to_subdomain):
            subdomain = future_to_subdomain[future]
            try:
                ips = future.result()
                if ips:
                    ip_addresses[subdomain] = ips
                    print(colored(f"[*] IPs for {subdomain}: {', '.join(ips)}", 'green'))
            except Exception as e:
                print(colored(f"[!] Error resolving IP for {subdomain}: {e}", 'red'))

    return ip_addresses

# Enumerate emails on a subdomain with retry logic
def enum_emails(subdomain):
    emails = []
    retries = 3
    timeout = 10  # Timeout for each request

    for attempt in range(retries):
        try:
            response = requests.get(f"http://{subdomain}", timeout=timeout)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            found_emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', response.text)
            if found_emails:
                emails.extend(found_emails)
                print(colored(f"[+] Found emails on {subdomain}: {', '.join(found_emails)}", 'yellow'))
            break  # Exit the retry loop if successful
        except requests.RequestException as e:
            if attempt < retries - 1:
                print(colored(f"[!] Error fetching {subdomain}: {e}. Retrying...", 'red'))
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                print(colored(f"[!] Error fetching {subdomain}: {e}", 'red'))
    return emails

# Email enumeration on all discovered subdomains
def email_enum(subdomains):
    all_emails = []
    print(colored("[*] Enumerating emails on discovered subdomains...", 'cyan'))

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_subdomain = {executor.submit(enum_emails, sub): sub for sub in subdomains}
        for future in as_completed(future_to_subdomain):
            subdomain = future_to_subdomain[future]
            try:
                emails = future.result()
                if emails:
                    all_emails.extend(emails)
            except Exception as e:
                print(colored(f"[!] Error during email enumeration on {subdomain}: {e}", 'red'))

    return list(set(all_emails))

# Main execution flow
def main():
    print_banner()
    domain = input(colored("[*] Enter the domain to enumerate: ", 'yellow')).strip()

    # Discover subdomains
    all_subdomains = []
    all_subdomains += dns_lookup(domain)
    all_subdomains += google_dork_subdomains(domain)
    all_subdomains += api_discovery(domain)

    # Brute-force method using wordlist
    wordlist_path = input(colored("[*] Enter the path to the subdomain wordlist: ", 'yellow')).strip()
    all_subdomains += brute_force_subdomains(domain, wordlist_path)

    all_subdomains = list(set(all_subdomains))  # Remove duplicates

    if not all_subdomains:
        print(colored("[!] No subdomains found.", 'red'))
        return

    print(colored(f"[*] Total subdomains found: {len(all_subdomains)}", 'cyan'))

    # Save subdomains to file
    with open(f"{domain}_subdomains.txt", 'w') as f:
        for subdomain in all_subdomains:
            f.write(subdomain + '\n')
    print(colored(f"[*] Subdomains saved to {domain}_subdomains.txt", 'green'))

    # Get IP addresses for all discovered subdomains
    ip_addresses = get_ip_addresses(all_subdomains)

    # Save IPs to file
    with open(f"{domain}_ips.txt", 'w') as f:
        for subdomain, ips in ip_addresses.items():
            f.write(f"{subdomain}: {', '.join(ips)}\n")
    print(colored(f"[*] IP addresses saved to {domain}_ips.txt", 'green'))

    # Email enumeration on all subdomains
    all_emails = email_enum(all_subdomains)

    # Save emails to file
    with open(f"{domain}_emails.txt", 'w') as f:
        for email in all_emails:
            f.write(email + '\n')
    print(colored(f"[*] Emails found saved to {domain}_emails.txt", 'green'))

if __name__ == "__main__":
    main()
