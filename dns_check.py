import dns.resolver
from termcolor import colored  # For a colored console!!
def check_dns_records(domain):
    try:
        record_types = ['A', 'AAAA', 'MX', 'CNAME', 'TXT', 'NS', 'SOA']
        resolver = dns.resolver.Resolver()
        results = {}
        for record_type in record_types:
            try:
                answer = resolver.resolve(domain, record_type)
                results[record_type] = [str(rdata) for rdata in answer]
            except dns.resolver.NoAnswer:
                results[record_type] = []
            except dns.resolver.NXDOMAIN:
                results[record_type] = []
            except dns.resolver.NoNameservers:
                results[record_type] = []
            except Exception as e:
                results[record_type] = str(e)
        return results
    except Exception as e:
        return {'error': str(e)}

def display_results(domain, results):
    print("\n" + colored(f"DNS Records for {domain}", "cyan", attrs=["bold"]))
    print("=" * (len(f"DNS Records for {domain}") + 2))
    if 'error' in results:
        print(colored(f"Error: {results['error']}", "red"))
        return
    for record_type, record_data in results.items():
        if record_type == "A":
            record_title = "IPv4 Addresses"
        elif record_type == "AAAA":
            record_title = "IPv6 Addresses"
        elif record_type == "MX":
            record_title = "Mail Exchanger"
        elif record_type == "CNAME":
            record_title = "Canonical Name"
        elif record_type == "TXT":
            record_title = "Text Records"
        elif record_type == "NS":
            record_title = "Name Servers"
        elif record_type == "SOA":
            record_title = "Start of Authority"
        print(f"\n{colored(record_title, 'yellow', attrs=['bold'])}:")
        if record_data:
            for record in record_data:
                print(f"  - {colored(record, 'green')}")
        else:
            print(colored("  Not found", "red"))
    print("\n" + "=" * 40)
if __name__ == "__main__":
    domain = input("Enter domain to check DNS records: ").strip()
    results = check_dns_records(domain)
    display_results(domain, results)