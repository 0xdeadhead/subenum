from subenum.subprocs import run_cmds, run_cmd
from argparse import ArgumentParser
from termcolor import cprint, colored
import subenum.wordlists
import asyncio
import time
import json
import sys
import os


# Function Takes configuration directory as input and returns a list of passive enumeration commands
def passive_enum(base_dir, domain):
    if os.path.exists(f"{base_dir}/subenum.json"):
        with open(f"{base_dir}/subenum.json") as file_handle:
            config_data = json.load(file_handle)
            cmds = []
            for config in config_data:
                # Check if specified file exists and config_file field is empty
                if os.path.exists(f"{base_dir}/tool_config/{config['config_file']}") and f"{config['config_file']}":
                    cmds.append(config["conf_cmd"].format(
                        config_file_path=f"{base_dir}/tool_config/{config['config_file']}", domain=domain))
                else:
                    cmds.append(config["base_cmd"].format(domain=domain))
        return cmds
    else:
        cprint("[-] Config File Not Found", color="red", file=sys.stderr)
        sys.exit(1)


# Generate subdomains from wordlist
def generate_wordlist(subdomain_file_path, root_domain):
    with open(subdomain_file_path) as wordlist:
        subdomains = wordlist.readlines()
        final_subdomain_list = [
            f"{subdomain}.{root_domain}".replace('\n', '') for subdomain in subdomains]
    return "\n".join(final_subdomain_list)


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "-c", "--config_dir", help="Directory Containing configuration", default=f"{os.environ['HOME']}/subenum_config")
    parser.add_argument("-d", "--domain", help="Domain name", required=True)
    parser.add_argument(
        "-o", "--output_dir", help="Directory for writing output", default=f"{os.environ['HOME']}/subenum_output")
    parser.add_argument("-r", "--refresh", help="Refresh resolvers list",
                        default=False, action="store_true")
    parser.add_argument("-R", "--resolve_count",
                        help="No of times to resolve", default=3)
    args = parser.parse_args()

    DOMAIN = args.domain
    RES_COUNT = args.resolve_count
    CONFIG_DIR = args.config_dir
    OUTPUT_DIR = args.output_dir

    # check for output directories
    if not os.path.exists(OUTPUT_DIR):
        os.system(f"mkdir -p {OUTPUT_DIR}")
    choice = "y"
    if os.path.exists(f"{OUTPUT_DIR}/{DOMAIN}"):
        choice = input(colored(
            f"[?] Directory '{OUTPUT_DIR}/{DOMAIN}' already exists.do you want to overwrite[y/N]?", color="red"))
    if choice == 'N' or choice == "n" or choice == "no":
        cprint("Exiting", color="red", file=sys.stderr)
        sys.exit(0)
    os.system(f"mkdir -p {OUTPUT_DIR}/{DOMAIN}")

    # Check if Refresh flag is set and resolvers.txt file exists and make a resolvers.txt file
    if args.refresh or not os.path.exists(f"{CONFIG_DIR}/resolvers.txt"):
        asyncio.run(run_cmd(
            f"dnsvalidator --silent -tL https://public-dns.info/nameservers.txt -threads 200 > {CONFIG_DIR}/resolvers.txt"))

    # Passive subdomain enumeration tasks
    tasks = passive_enum(CONFIG_DIR, DOMAIN)
    passive_subs = asyncio.run(run_cmds(*tasks))

    cprint("[*] Completed passive enumeration", color="cyan", file=sys.stderr)
    # joining output from all tools
    passive_subs = "\n".join(passive_subs)
    # Update subdomains wordlist
    subdomain_file_path = subenum.wordlists.update_wordlist(CONFIG_DIR)

    # Generating subdomains from wordlist
    brute_subs = generate_wordlist(subdomain_file_path, DOMAIN)
    subdomains = passive_subs+brute_subs

    # Removing duplicate subdomains
    cprint("[*] Removing duplicate Subdomains",
           color="yellow", file=sys.stderr)
    unique_domains = asyncio.run(
        run_cmd("urldedupe", inp_src=bytes(subdomains, "utf-8")))

    # Writing unique domains to a temp file
    unresolved_domains_file = f"/tmp/subenum_unres_{int(time.time())}.txt"
    with open(unresolved_domains_file, "w") as unresolved_domains_file_handle:
        unresolved_domains_file_handle.write(unique_domains)

    total_subs = unique_domains.split("\n")
    cprint(f"[*] Started resolving {len(total_subs)} subdomains",
           color="yellow", file=sys.stderr)

    RESOLVE_FROM_STDIN = f" | shuffledns -t 25000 -r {CONFIG_DIR}/resolvers.txt "*RES_COUNT

    asyncio.run(run_cmd(
        f"shuffledns -t 25000  -list {unresolved_domains_file} -r {CONFIG_DIR}/resolvers.txt {RESOLVE_FROM_STDIN} -d {DOMAIN} -o {OUTPUT_DIR}/{DOMAIN}/resolved.txt"))

    cprint(
        f"[*] resolved domains written to {OUTPUT_DIR}/{DOMAIN}/resolved.txt\nStarted generating Possibilities", color="yellow", file=sys.stderr)

    # set fast flag according to subdomain count
    fast_flag = ""
    with open(f"{OUTPUT_DIR}/{DOMAIN}/resolved.txt") as resolved_sub_file:
        if len(resolved_sub_file.readlines()) >= 1000:
            fast_flag = "-f"
            cprint("[*] This may take time due to large subdomains list",
                   color="cyan", file=sys.stderr)

    asyncio.run(run_cmd(
        f"dnsgen {fast_flag} {OUTPUT_DIR}/{DOMAIN}/resolved.txt {RESOLVE_FROM_STDIN} -d {DOMAIN} -o  {OUTPUT_DIR}/{DOMAIN}/resolved_possibilities.txt"))

    cprint(
        f"[*] resolved domains written to {OUTPUT_DIR}/{DOMAIN}/resolved_possibilities.txt", color="yellow", file=sys.stderr)


if __name__ == "__main__":
    main()
