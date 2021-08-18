import sys,ldap,ldap.asyncsearch,json
## Classes ##
class user:
    def __init__(self, cn, uid, modifyTimestamp, manager, title):
        self.cn = cn
        self.uid = uid
        self.modifyTimestamp = modifyTimestamp
        self.manager = manager
        self.title = title
class group:
    def __init__(self, dn, modifyTimestamp, creatorsName, modifiersName):
        self.dn = dn
        self.modifyTimestamp = modifyTimestamp
        self.creatorsName = creatorsName
        self.modifiersName = modifiersName

class member:
    def __init__(self, dn, description, members):
        self.dn = dn
        self.description = description
        self.members = members
## END Classes ##
## Functions ##

def connectLDAP(uri, user, password):
    try:
        conn = ldap.initialize(uri)
        #conn.set_option(ldap.OPT_X_TLS_CACERTFILE, '/path/to/ca.pem')
        #conn.set_option(ldap.OPT_X_TLS_NEWCTX, 0)
        #conn.start_tls_s()
        conn.simple_bind_s(user, password)
        return conn
    except:
        return None

def searchLDAP(connection, root, scope, filter):
    try:
        s = ldap.asyncsearch.List(connection)
        s.startSearch(root, scope, filter, ['*','+'])
        try:
            partial = s.processResults()
        except ldap.SIZELIMIT_EXCEEDED:
            return 'Warning: Server-side size limit exceeded.'
        else:
            if partial:
                sys.stderr.write('Warning: Only partial results received.\n')
        return s
    except:
        return None
