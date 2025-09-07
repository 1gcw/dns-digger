import os
import json
import dns.resolver
import threading
from queue import Queue
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()
q = Queue()
found = []
not_found = []
cache = {}
lock = threading.Lock()

def load_cache(cache_file):
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache_file, data):
    with open(cache_file, "w") as f:
        json.dump(data, f, indent=2)

def resolve_domain(subdomain):
    try:
        dns.resolver.resolve(subdomain, "A")
        return True
    except:
        return False

def worker(domain):
    global cache
    while not q.empty():
        sub = q.get()
        full_domain = f"{sub}.{domain}"

        with lock:
            if full_domain in cache:
                q.task_done()
                continue

        if resolve_domain(full_domain):
            with lock:
                found.append(full_domain)
                cache[full_domain] = True
                console.print(f"[bold green]+ FOUND:[/bold green] {full_domain}")
        else:
            with lock:
                not_found.append(full_domain)
                cache[full_domain] = False

        q.task_done()

def ask_user_input():
    console.clear()
    console.print(Panel("[bold cyan]DNS Digger - Subdomain Finder[/bold cyan]", expand=False))

    domain = Prompt.ask("Target domain (e.g., example.com)", default="example.com").strip().lower()

    use_own = Confirm.ask("Do you have your own wordlist?")
    if use_own:
        while True:
            path = Prompt.ask("Path to your wordlist")
            if os.path.exists(path):
                break
            console.print("[red]File not found. Try again.[/red]")
    else:
        path = "wordlists/default.txt"
        console.print(f"[yellow]Using default wordlist: {path}[/yellow]")

    threads = Prompt.ask("Number of threads", default="20")
    return domain, path.strip(), int(threads)

def save_output(domain):
    safe_domain = domain.replace("http://", "").replace("https://", "").strip("/")
    out_dir = os.path.join("output", safe_domain)
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, "valid.txt"), "w") as f:
        for sub in found:
            f.write(sub + "\n")

    with open(os.path.join(out_dir, "invalid.txt"), "w") as f:
        for sub in not_found:
            f.write(sub + "\n")

    console.print(f"\n[bold cyan]Results saved in:[/bold cyan] [green]{out_dir}[/green]")

def main():
    domain, wordlist_path, num_threads = ask_user_input()
    cache_file = "cache.json"

    global cache
    cache = load_cache(cache_file)

    with open(wordlist_path, "r") as f:
        for line in f:
            sub = line.strip()
            if sub:
                q.put(sub)

    console.print(Panel(f"[bold blue]Scanning domain:[/bold blue] [green]{domain}[/green]\n"
                        f"[cyan]Subdomains:[/cyan] {q.qsize()} | [cyan]Threads:[/cyan] {num_threads}", expand=False))

    threads = []
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("[yellow]Scanning subdomains...", total=None)

        for _ in range(num_threads):
            t = threading.Thread(target=worker, args=(domain,))
            t.start()
            threads.append(t)

        q.join()

        for t in threads:
            t.join()

        progress.stop()

    save_cache(cache_file, cache)
    save_output(domain)

    if found:
        console.print("\n[bold green]Valid subdomains found:[/bold green]")
        for sub in found:
            console.print(f" - {sub}")
    else:
        console.print("\n[bold red]No subdomains were found.[/bold red]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[red]Interrupted by user.[/red]")