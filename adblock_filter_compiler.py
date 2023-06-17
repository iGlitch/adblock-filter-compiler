import re
import requests
from datetime import datetime
import json

def is_valid_domain(domain):
    """Checks if a string is a valid domain."""
    domain_regex = re.compile(
        r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$"
    )
    return bool(domain_regex.match(domain))

def parse_hosts_file(content):
    """Parses a host file content into AdBlock rules."""
    lines = content.split('\n')
    adblock_rules = set()

    for line in lines:
        line = line.strip()

        # Ignore comments and empty lines
        if line.startswith('#') or line.startswith('!') or line == '':
            continue

        # Check if line follows AdBlock syntax, else create new rule
        if line.startswith('||') and line.endswith('^'):
            adblock_rules.add(line)
        else:
            parts = line.split()
            domain = parts[-1]
            if is_valid_domain(domain):
                rule = f'||{domain}^'
                adblock_rules.add(rule)

    return adblock_rules

def generate_filter(file_contents, filter_type):
    """Generates filter content from file_contents by eliminating duplicates and redundant rules."""
    duplicates_removed = 0
    redundant_rules_removed = 0
    adblock_rules_set = set()
    base_domain_set = set()

    for content in file_contents:
        adblock_rules = parse_hosts_file(content)
        for rule in adblock_rules:
            domain = rule[2:-1]  # Remove '||' and '^'
            base_domain = '.'.join(domain.split('.')[-2:])  # Get the base domain (last two parts)
            if rule not in adblock_rules_set:
                # Check for redundant rules
                if base_domain not in base_domain_set:
                    adblock_rules_set.add(rule)
                    base_domain_set.add(base_domain)
                else:
                    redundant_rules_removed += 1
            else:
                duplicates_removed += 1

    sorted_rules = sorted(list(adblock_rules_set))
    header = generate_header(len(sorted_rules), duplicates_removed, redundant_rules_removed, filter_type)
    if filter_type == 'whitelist':
        whitelist_rules = ['@@' + rule for rule in sorted_rules]
        filter_content = '\n'.join([header, '', *whitelist_rules])  # Add an empty line after the header
    else:
        filter_content = '\n'.join([header, '', *sorted_rules])  # Add an empty line after the header
    return filter_content, duplicates_removed, redundant_rules_removed

def generate_header(domain_count, duplicates_removed, redundant_rules_removed, filter_type):
    """Generates header with specific domain count, removed duplicates, and compressed domains information."""
    date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')  # Includes date, time, and timezone
    if filter_type == 'blacklist':
        title = "Glitch Compiled Blacklist"
    elif filter_type == 'whitelist':
        title = "Glitch Compiled Whitelist"
    else:
        title = "Filter"
    return f"""# Title: {title}
# Description: Python script that generates adblock filters by combining {filter_type}s, host files, and domain lists.
# Last Modified: {date_time}
# Domain Count: {domain_count}
# Duplicates Removed: {duplicates_removed}
# Domains Compressed: {redundant_rules_removed}
#=================================================================="""

def get_parent_domains(domain):
    """Generates the immediate parent domain of a given domain."""
    parts = domain.split('.')
    if len(parts) > 2:
        return ['.'.join(parts[i:]) for i in range(1, 2)]
    else:
        return []

def main():
    """Main function to fetch blocklists and generate a combined filter."""
    with open('config.json') as f:
        config = json.load(f)

    blacklist_urls = config['blacklist_urls']
    whitelist_urls = config['whitelist_urls']

    file_contents = []
    for url in blacklist_urls:
        with requests.get(url) as response:
            file_contents.append(response.text)

    whitelist_contents = []
    for url in whitelist_urls:
        with requests.get(url) as response:
            whitelist_contents.append(response.text)

    blacklist_content, duplicates_removed, redundant_rules_removed = generate_filter(file_contents, 'blacklist')
    whitelist_content, _, _ = generate_filter(whitelist_contents, 'whitelist')

    # Write the blacklist content to a file
    with open('blacklist.txt', 'w') as f:
        f.write(blacklist_content)

    # Write the whitelist content to a file
    with open('whitelist.txt', 'w') as f:
        f.write(whitelist_content)

if __name__ == "__main__":
    main()
