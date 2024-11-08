from requests import get, exceptions
from argparse import ArgumentParser, FileType
from threading import Thread, Lock
from time import time, sleep
from queue import Queue
from colorama import Fore, Style, init
import sys

# Initialize colorama
init(autoreset=True)

def make_args():
    pars = ArgumentParser(
        description="My First subdomain finder",
        usage="%(prog)s -w wordlist.txt",
        epilog="Example: python3 %(prog)s -w wordlist.txt -t 20 -o output.txt",
    )
    pars.add_argument(
        "-w",
        "--wordlist",
        dest="wordlist",
        metavar="",
        required=True,
        type=FileType("r"),
        help="List of words",
    )
    pars.add_argument(
        "-t",
        "--threads",
        dest="threads",
        metavar="",
        type=int,
        help="Threads to make the process faster",
        default=10,
    )
    pars.add_argument(
        "-o",
        "--output",
        dest="output",
        metavar="",
        type=FileType("w"),
        help="File to save vulnerable URLs",
        required=True
    )
    pars.add_argument(
        "-V",
        "--version",
        action="version",
        version="%(prog)s 2.0 latest",
        help="Show version",
    )
    args = pars.parse_args()
    return args

subdomain = []
words_queue = Queue()
processed_count = 0
lock = Lock()

def make_thread(total_words, threads):
    thread_list = []
    for _ in range(threads):
        thread = Thread(target=scan_subdomain, args=(total_words,))
        thread.start()
        thread_list.append(thread)
    for thread in thread_list:
        thread.join()

def make_word(wordlist):
    wordlist = wordlist.read().splitlines()
    for word in wordlist:
        words_queue.put(word)

def scan_subdomain(total_words):
    global processed_count
    while not words_queue.empty():
        try:
            urls = words_queue.get_nowait()
            req = get(urls)

            if "xss<>" in req.text:
                print(f"{Fore.RED}[Vulnerable]    {Style.RESET_ALL}{urls}")
                if urls not in subdomain:
                    subdomain.append(urls)
                    if args.output:  # Write to output file if specified
                        with lock:
                            args.output.write(urls + "\n")
            else:
                print(f"{Fore.GREEN}[Not Vulnerable] {Style.RESET_ALL}{urls}")
        except exceptions.RequestException:
            continue
        finally:
            words_queue.task_done()
            with lock:
                processed_count += 1
                print_progress(processed_count, total_words)

def print_progress(processed, total):
    percentage = (processed / total) * 100
    spinner = ['|', '/', '-', '\\']
    sys.stdout.write(f"\rProgress: {percentage:.2f}% {spinner[processed % 4]}")  # Spinner effect
    sys.stdout.flush()

def print_banner():
    banner = """
░██████╗██╗░█████╗░███╗░░░███╗        ██╗░░██╗██╗███╗░░██╗░██████╗░
██╔════╝██║██╔══██╗████╗░████║        ██║░██╔╝██║████╗░██║██╔════╝░
╚█████╗░██║███████║██╔████╔██║        █████═╝░██║██╔██╗██║██║░░██╗░
░╚═══██╗██║██╔══██║██║╚██╔╝██║        ██╔═██╗░██║██║╚████║██║░░╚██╗
██████╔╝██║██║░░██║██║░╚═╝░██║        ██║░╚██╗██║██║░╚███║╚██████╔╝
╚═════╝░╚═╝╚═╝░░╚═╝╚═╝░░░░░╚═╝        ╚═╝░░╚═╝╚═╝░░╚══╝░╚═════╝░
    """
    print(Fore.YELLOW + banner + Style.RESET_ALL)

if __name__ == "__main__":
    print_banner()  # Print the banner when the program starts
    start = time()
    args = make_args()
    make_word(args.wordlist)
    total_words = words_queue.qsize()
    make_thread(total_words, args.threads)
    if subdomain:
        print("\nvuln URL(s) found:")
        for i in subdomain:
            print(i)
    else:
        print("\nNo vulnerable URLs found.")
    end_time = time()
    print(f"\nTime: {round(end_time - start, 2)} seconds")

