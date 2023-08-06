from ipify.syncronous import find_ipv4, find_ipv6
def main():
    ipv4 = find_ipv4()
    ipv6 = find_ipv6()
    print('IPv4: {}'.format(ipv4))
    print('IPv6: {}'.format(ipv6))

if __name__ == '__main__':
    main()


