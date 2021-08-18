import sys,json
sys.path.append('/home/tjohnson/DirectoryAudit/sources')
import ldapSource
import jsondiff as jd
from jsondiff import diff

## Classes ##
## END Classes ##
## Functions ##
def loadJSON(path):
    try:
        with open(path) as f:
            data = json.load(f)
        return data
    except:
        print("Error loading " + path)
        return None

def writeJSON(data, path):
    try:
        with open(path, "w") as f:
            f.write(data)
    except:
        print("Error writing " + path)
        return None

def createConfig():
    return 1
## END Functions ##
## Global Vars ##
config = loadJSON('config.json')
first_run = False

## END Global Vars ##
## Main Routine ##
if config == None: # Check if first run.
    createConfig
    print("Please modify the default configuration.")
    exit
else:
    sources = config['sources']
    for source in sources:
        if source['type'] == 'LDAP':
            ldapConn = ldapSource.connectLDAP(source['uri'], source['user'], source['pass'])
            if ldapConn == None:
                print("Error connecting to " + source['name'])
            else:
                for dirObject in source['objects']:
                    objectValues = []
                    try:
                        ldapSearch = ldapSource.searchLDAP(ldapConn, dirObject['root'], dirObject['scope'], dirObject['filter'])
                        for num, ldapObject in ldapSearch.allResults:
                            values = []
                            dn = ldapObject[0]
                            #print(ldapObject[1])
                            for ldapField in ldapObject[1]:
                                try:
					#print(ldapValue)
                                    	for field in dirObject['fields']:
                                        	for value in ldapObject[1][ldapField]:
							try:
								#print(ldapField + ' | ' + value)
								if field == ldapField:
									jsonValue = {
                                            					'field': field,
                                            					'value': value.decode("utf-8", "ignore")
                                            				}
                                        				values.append(jsonValue)
							except:
								None
                                except:
                                    print('Error with object: ' + dn + ' | field: ' + field)
                            tempObject = {
                                'dn': dn,
                                'fields': values
                                }
                            objectValues.append(tempObject)
                        tempJSON = json.dumps(objectValues)
                        #print(tempJSON)
			writeJSON(tempJSON, dirObject['filename'])
                    except:
                        print("Error searching LDAP.")

                    


#last_users = loadJSON('last_users.json')
#last_groups = loadJSON('last_groups.json')
#last_members = loadJSON('last_members.json')
#if last_groups == None or last_users == None or last_members == None:
#    first_run = True
