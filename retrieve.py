import requests
import csv
import sys
import logging
import loginInfo as l

# Authentication
def auth():
	auth = requests.post(l.baseURL + "/users/" + l.user + "/login?password=" + l.password).json()
	session = auth["session"]
	headers = {'X-ArchivesSpace-Session': session}
	return headers

def retrieve(server,agentType):
	# Authenticate
	baseURL = l.baseURL
	headers = auth()

	# Dictionary of endpoint according to type of agents
	agents = {
		"corporate": "/agents/corporate_entities",
		"family": "/agents/families",
		"person": "/agents/people",
		"software": "/agents/software"
	}

	# Get the list of all agents id in ASpace by type
	idList = requests.get(baseURL + agents[agentType] + "?all_ids=true", headers=headers).json()

	agentsList = [['ASpace_ID','Names','Authority_ID','Source']]

	for i in idList:
		data = requests.get(baseURL + agents[agentType] + "/" + str(i), headers=headers).json()
		# if 'title' in data:
		# 	name = data['title']
		if 'display_name' in data:
			if 'sort_name' in data['display_name']:
				name = data['display_name']['sort_name']
			else:
				name = None
			if 'authority_id' in data['display_name']:
				authority_id = data['display_name']['authority_id']
			else:
				authority_id = None
			if 'source' in data['display_name']:
				source = data['display_name']['source']
			else:
				source = None
		

		row = [i,name,authority_id,source]
		print(row)

		agentsList.append(row)

	f = open('./data/%s/%s.csv' % (server,agentType), 'w', encoding='utf-8-sig')
	w = csv.writer(f)
	w.writerows(agentsList)
	f.close()

	# Log out of the current session
	logout = requests.post(baseURL + '/logout', headers=headers, data={})


if __name__ == '__main__':
	retrieve(*sys.argv[1:])



