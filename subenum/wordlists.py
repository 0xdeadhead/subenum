from termcolor import cprint
import requests
import os
import sys
import json
import time


def update_wordlist(base_dir):
    try:
        with open(f"{base_dir}/wordlist_config.json") as config_file:
            configuration = json.load(config_file)
    except FileNotFoundError as e:
        cprint(f"Wordlist configuration doesn't exists\n{e}",
               color="red", file=sys.stderr)
        sys.exit(1)
    subdomain_file_path = f"/tmp/subenum_subdomains_{int(time.time())}.txt"
    with open(subdomain_file_path, "w") as subdomain_file:
        subdomains_list = []
        for conf in configuration:
            resp = requests.head(conf["url"])
            etag = resp.headers["etag"].replace('"', '')
            if etag != conf["etag"]:
                cprint(
                    f"[*] Updating wordlist: {conf['name'] }", color="cyan", file=sys.stderr)
                resp = requests.get(conf["url"])
                with open(f"{base_dir}/wordlists/{conf['name']}", "w") as wordlist:
                    wordlist.write(resp.text)
                    # Write etag changes back to configuration file
                    with open(f"{base_dir}/wordlist_config.json", "w") as config_file:
                        index = configuration.index(conf)
                        configuration[index]["etag"] = etag
                        config_file.write(json.dumps(configuration))
            # Reading from individual wordlists
            with open(f"{base_dir}/wordlists/{conf['name']}") as wordlist:
                subdomains_list += wordlist.readlines()
        unique_domains = set(subdomains_list)
        # Writing to temporarary subdomain_file
        subdomain_file.write("".join(unique_domains))
    return subdomain_file_path


if __name__ == "__main__":
    print(update_wordlist(sys.argv[1]))
