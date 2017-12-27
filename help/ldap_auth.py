import ldap3


def auth_ad(user, password, domain_server, domain_name, base_dn):
    try:
        """Simple authentication for AD"""
        server = ldap3.Server(domain_server, get_info=ldap3.ALL)
        connection = ldap3.Connection(server, user=domain_name + '\\' + user, password=password, authentication=ldap3.NTLM, auto_bind=True)

        _filter = '(objectclass=person)'
        attrs = ['SamAccountName']

        connection.search(search_base=base_dn,  search_filter=_filter, search_scope=ldap3.SUBTREE, attributes=attrs)
        usernames = list()
        for username in connection.response:
            usernames.append(username['attributes']['sAMAccountName'])

        if user not in usernames:
            print('Voce nao esta no grupo Diretoria TI!')
            return False

        return True
    except Exception as error:
        input('Erro ao tentar autenticar: {}'.format(error))
        return False
