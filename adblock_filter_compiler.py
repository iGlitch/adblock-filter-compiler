import requests
from datetime import datetime

def parse_hosts_file(content):
    """Parses a host file content into AdBlock rules."""
    lines = content.split('\n')
    adblock_rules = []

    for line in lines:
        line = line.strip()
        # Ignore comments and empty lines
        if line.startswith('#') or line.startswith('!') or line == '':
            continue

        # Check if line follows AdBlock syntax, else create new rule
        if line.startswith('||') and line.endswith('^'):
            adblock_rules.append(line)
        else:
            parts = line.split()
            domain = parts[-1]
            rule = f'||{domain}^'
            adblock_rules.append(rule)

    return adblock_rules

def generate_filter(blocklist_contents, whitelist_urls):
    """Generates filter content from file_contents by eliminating duplicates."""
    duplicates_removed = 0
    adblock_rules_set = set()

    for content in blocklist_contents:
        adblock_rules = parse_hosts_file(content)
        for rule in adblock_rules:
            if rule not in adblock_rules_set:
                adblock_rules_set.add(rule)
            else:
                duplicates_removed += 1

    sorted_rules = sorted(list(adblock_rules_set))
    header = generate_header(len(sorted_rules), duplicates_removed)
    filter_content = '\n'.join([header, '', *sorted_rules])  # Added empty line after the header

    whitelist_rules = []
    for url in whitelist_urls:
        with requests.get(url) as response:
            whitelist_content = response.text
            whitelist_rules.extend(whitelist_content.splitlines())

    whitelist_header = generate_whitelist_header(len(whitelist_rules))
    whitelist_content = '\n'.join([whitelist_header, '', *whitelist_rules])

    return filter_content, duplicates_removed, whitelist_content

def generate_header(domain_count, duplicates_removed):
    return f"""# Title: AdBlock Blacklist Compiler
# Description: A Python script that generates AdBlock syntax filters by combining and processing multiple blocklists, host files, and domain lists.
# Created: {datetime.now().strftime('%Y-%m-%d')}
# Domain Count: {domain_count}
# Duplicates Removed: {duplicates_removed}
#==============================================================="""

def generate_whitelist_header(domain_count):
    return f"""# Title: AdBlock Whitelist Compiler
# Description: List of whitelisted domains for AdBlock filters.
# Created: {datetime.now().strftime('%Y-%m-%d')}
# Domain Count: {domain_count}
#==============================================================="""

def main():
    """Main function to fetch blocklists and generate a combined filter."""
    blocklist_urls = [
        'https://github.com/sjhgvr/oisd/blob/main/abp_full.txt?raw=true',
        'https://raw.githubusercontent.com/sjhgvr/oisd/main/abp_extra.txt',
        'https://badmojr.github.io/1Hosts/Pro/adblock.txt',
        'https://raw.githubusercontent.com/notracking/hosts-blocklists/master/adblock/adblock.txt',
        'https://block.energized.pro/extensions/regional/formats/filter',
        'https://raw.githubusercontent.com/jerryn70/GoodbyeAds/master/Formats/GoodbyeAds-AdBlock-Filter.txt',
        'https://hblock.molinero.dev/hosts_adblock.txt',
        'https://gist.githubusercontent.com/iGlitch/7f49db0bb9038938249cfd7edef19b54/raw/30ffbf4d60a6b24ba3e8f44d4b49ac123348f415/firefox.txt',
        'https://raw.githubusercontent.com/BlackJack8/iOSAdblockList/master/Hosts.txt'
    ]

    whitelist_urls = [
        'https://raw.githubusercontent.com/AhaDNS/Aha.Dns.Domains/master/Domains/whitelist.txt',
        'https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt',
        'https://box.glitchery.jp/whitelist.txt'
    ]

    blocklist_contents = []
    for url in blocklist_urls:
        with requests.get(url) as response:
            blocklist_contents.append(response.text)

    filter_content, duplicates_removed, whitelist_content = generate_filter(blocklist_contents, whitelist_urls)

    # Write the filter content to a file
    with open('blocklist.txt', 'w') as f:
        f.write(filter_content)

    with open('whitelist.txt', 'w') as f:
        f.write(whitelist_content)

if __name__ == "__main__":
    main()
