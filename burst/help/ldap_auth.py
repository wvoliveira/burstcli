import ldap3


def auth_ad(user, password, domain_server, domain_prefix, base_dn):
    try:
        server = ldap3.Server(domain_server, get_info=ldap3.ALL)
        connection = ldap3.Connection(server, user=domain_prefix + '\\' + user, password=password, authentication=ldap3.NTLM, auto_bind=True)

        _filter = '(objectclass=person)'
        attrs = ['SamAccountName']

        connection.search(search_base=base_dn,  search_filter=_filter, search_scope=ldap3.SUBTREE, attributes=attrs)
        usernames = list()
        for username in connection.response:
            usernames.append(username['attributes']['sAMAccountName'])

        if user not in usernames:
            print('Need to be in the IT Management group!')
            return False
        return True

    except Exception as error:
        input('Error to authenticate: {}'.format(error))
        return False
