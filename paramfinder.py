import requests
import random
import json
import logging
import time
import sys
import argparse
import os
import colorama
from colorama import Fore, Style
from urllib.parse import urlparse, parse_qs, urlencode
from requests.exceptions import RequestException

# Initialize colorama for colored output and set up logging
colorama.init(autoreset=True)
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Constants
MAX_RETRIES = 3
HARDCODED_EXTENSIONS = [
    ".jpg", ".jpeg", ".png", ".gif", ".pdf", ".svg", ".json",
    ".css", ".js", ".webp", ".woff", ".woff2", ".eot", ".ttf", ".otf", ".mp4", ".txt"
]

# Load User-Agent strings
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 Safari/603.3.8",
    # Add more User-Agents as needed
]

# Utility functions
def fetch_url_content(url, proxy=None):
    """
    Fetches the content of a URL with retries and random User-Agent.
    
    Args:
        url (str): The URL to fetch.
        proxy (str): Proxy address for the request.

    Returns:
        response (Response): The HTTP response from the server.
    """
    session = requests.Session()
    proxies = {'http': proxy, 'https': proxy} if proxy else None
    
    for attempt in range(1, MAX_RETRIES + 1):
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        try:
            response = session.get(url, headers=headers, proxies=proxies)
            response.raise_for_status()
            return response
        except RequestException as e:
            logging.warning(f"Attempt {attempt}/{MAX_RETRIES} failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)
    logging.error(f"Failed to fetch URL {url} after {MAX_RETRIES} attempts.")
    sys.exit(1)

def has_extension(url, extensions=HARDCODED_EXTENSIONS):
    """
    Checks if the URL has a file extension matching any in the provided list.
    
    Args:
        url (str): The URL to check.
        extensions (list): List of file extensions to match against.

    Returns:
        bool: True if the URL has a matching extension, False otherwise.
    """
    extension = os.path.splitext(urlparse(url).path)[1].lower()
    return extension in extensions

def clean_url(url):
    """
    Cleans the URL by removing unnecessary port information.
    
    Args:
        url (str): The URL to clean.

    Returns:
        str: Cleaned URL.
    """
    parsed_url = urlparse(url)
    if (parsed_url.port == 80 and parsed_url.scheme == "http") or (parsed_url.port == 443 and parsed_url.scheme == "https"):
        parsed_url = parsed_url._replace(netloc=parsed_url.netloc.rsplit(":", 1)[0])
    return parsed_url.geturl()

def clean_urls(urls, extensions, placeholder):
    """
    Cleans and sanitizes a list of URLs by removing unwanted parameters.
    
    Args:
        urls (list): List of URLs to clean.
        extensions (list): List of file extensions to ignore.

    Returns:
        list: List of cleaned URLs.
    """
    cleaned_urls = set()
    for url in urls:
        if has_extension(url, extensions):
            continue
        cleaned_url = clean_url(url)
        parsed_url = urlparse(cleaned_url)
        query_params = parse_qs(parsed_url.query)
        cleaned_params = {key: placeholder for key in query_params}
        cleaned_query = urlencode(cleaned_params, doseq=True)
        final_url = parsed_url._replace(query=cleaned_query).geturl()
        cleaned_urls.add(final_url)
    return list(cleaned_urls)

def fetch_and_clean_urls(domain, extensions, stream_output, proxy, placeholder):
    """
    Fetches URLs from the Wayback Machine for a domain, then cleans them.
    
    Args:
        domain (str): The domain to fetch URLs for.
        extensions (list): List of extensions to ignore in URLs.
        stream_output (bool): If True, streams URLs to the terminal.
        proxy (str): Proxy address for web requests.
        placeholder (str): Placeholder for query parameters.
    """
    logging.info(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Fetching URLs for {Fore.CYAN + domain + Style.RESET_ALL}")
    wayback_uri = f"https://web.archive.org/cdx/search/cdx?url={domain}/*&output=txt&collapse=urlkey&fl=original&page=/"
    response = fetch_url_content(wayback_uri, proxy)
    urls = response.text.split()
    
    logging.info(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Found {Fore.GREEN + str(len(urls)) + Style.RESET_ALL} URLs.")
    cleaned_urls = clean_urls(urls, extensions, placeholder)
    logging.info(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Cleaned URLs: {Fore.GREEN + str(len(cleaned_urls)) + Style.RESET_ALL}")

    result_file = os.path.join("results", f"{domain}.txt")
    os.makedirs("results", exist_ok=True)
    with open(result_file, "w") as f:
        for url in cleaned_urls:
            if "?" in url:
                f.write(url + "\n")
                if stream_output:
                    print(url)
    
    logging.info(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Saved cleaned URLs to {Fore.CYAN + result_file + Style.RESET_ALL}")

def main():
    """
    Main function to parse command-line arguments and start URL mining.
    """
    log_text = """
░██████╗██╗░█████╗░███╗░░░███╗    ██╗░░██╗██╗███╗░░██╗░██████╗░
██╔════╝██║██╔══██╗████╗░████║    ██║░██╔╝██║████╗░██║██╔════╝░
╚█████╗░██║███████║██╔████╔██║    █████═╝░██║██╔██╗██║██║░░██╗░
░╚═══██╗██║██╔══██║██║╚██╔╝██║    ██╔═██╗░██║██║╚████║██║░░╚██╗
██████╔╝██║██║░░██║██║░╚═╝░██║    ██║░╚██╗██║██║░╚███║╚██████╔╝
╚═════╝░╚═╝╚═╝░░╚═╝╚═╝░░░░░╚═╝    ╚═╝░░╚═╝╚═╝╚═╝░░╚══╝░╚═════╝░
    """
    print(f"{Fore.YELLOW}{log_text}{Style.RESET_ALL}")

    parser = argparse.ArgumentParser(description="Mine URLs from Web Archives.")
    parser.add_argument("-d", "--domain", help="Domain name to fetch related URLs for.")
    parser.add_argument("-l", "--list", help="File containing a list of domain names.")
    parser.add_argument("-s", "--stream", action="store_true", help="Stream URLs on the terminal.")
    parser.add_argument("--proxy", help="Proxy address for web requests.", default=None)
    parser.add_argument("-p", "--placeholder", help="Placeholder for parameter values", default="xss<>")
    args = parser.parse_args()

    domains = []
    if args.domain:
        domains = [args.domain]
    elif args.list:
        with open(args.list, "r") as f:
            domains = list({line.strip().lower() for line in f if line.strip()})

    if not domains:
        parser.error("Please provide either the -d option or the -l option.")

    for domain in domains:
        fetch_and_clean_urls(domain, HARDCODED_EXTENSIONS, args.stream, args.proxy, args.placeholder)

if __name__ == "__main__":
    main()
