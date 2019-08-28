from xml.etree import  ElementTree
import sys
import logging
import csv
import requests
import re
import json
import loginInfo as l

def date(agent,subfields):
	datesOfExistence = {}
	datesOfExistence['jsonmodel_type'] = 'date'
	datesOfExistence['label'] = 'existence'
	dob = ''
	dod = ''
	begin = ''
	end = ''
	table = dict.fromkeys(map(ord,'[]()'),None)

	for sf in subfields:
		code = sf.get("code")
		if code == "f" or code == "s" or code == "q":
			dob = sf.text
			birth = dob.translate(table)
			birthYear = re.match(r"[0-9]{4}", birth)
			if birthYear is not None:
				begin = birthYear.group(0)
				datesOfExistence['begin'] = begin
		if code == "g" or code == "t" or code == "r":
			dod = sf.text
			death = dod.translate(table)
			deathYear = re.match(r"[0-9]{4}", death)
			if deathYear is not None:
				end = deathYear.group(0)

	if begin and end and int(end) > int(begin):
		datesOfExistence['end'] = end

	if dob and dod:
		datesOfExistence['date_type'] = 'range'
		datesOfExistence['expression'] = '%s-%s' % (dob,dod)
	else:
		datesOfExistence['date_type'] = 'single'
		datesOfExistence['expression'] = dob + dod		
	agent['dates_of_existence'].append(datesOfExistence)

def bio(agent,subfields):
	bio = {
		"jsonmodel_type":"note_bioghist",
		"subnotes":[],
		"label": "Biographical / Historical",
		"publish": True
	}
	subnote = {
		"jsonmodel_type": "note_text",
		"content": "",
		"publish": True
	}
	for sf in subfields:
		code = sf.get("code")
		if code == "a" or code == "b" or code == "u":
			subnote["content"] += "%s " % sf.text
	bio["subnotes"].append(subnote)
	agent["notes"].append(bio)

def person(agent,tree,ns,authority_id):
	# agent-person qualifiers
	qualifier_subfields = {
		'f': 'Date of work',
		'g': 'Miscellaneous information',
		'h': 'Medium',
		'j': 'Attribution qualifier',
		'k': 'Form subheading',
		'l': 'Language of a work',
		'm': 'Medium of performance for music',
		'n': 'Number of part/section of a work',
		'o': 'Arranged statement for music',
		'p': 'Name of a part/section of a work',
		'r': 'Key for music',
		's': 'Version',
		't': 'Title of work',
		'u': 'Affiliation'
	}
	for field in tree.findall(".//marcxml:datafield", ns):
		tag = field.get("tag")
		ind1 = field.get("ind1")
		subfields = field.findall(".//marcxml:subfield", ns)
		sort_name = ""
		# get dates of existence
		if tag == "046":
			date(agent,subfields)
		
		# get Biographical notes
		if tag == "678":
			bio(agent,subfields)

		# get authorized and display name for person
		if tag == "100" or tag == "400":
			name = {}
			for sf in subfields:
				code = sf.get("code")
				if code == "a":
					fullname = sf.text
					sort_name += fullname
					nameParts = fullname.split(',')
					name['primary_name'] = nameParts[0].strip()
					if len(nameParts) > 1 and nameParts[1]:
						name['rest_of_name'] = nameParts[1].strip()
				elif code == "c":
					title = sf.text
					sort_name += ' %s' % title
					name['title'] = title.strip(',')		
				elif code == "b":
					number = sf.text
					sort_name += ' %s' % number
					name['number'] = number.strip(',')
				elif code == "q":
					fullerForm = sf.text
					sort_name += ' %s' % fullerForm
					name['fuller_form'] = fullerForm.replace("(","").replace(")","")
				elif code == "d":
					dates = sf.text
					sort_name += ' %s' % dates
					name['dates'] = dates				
				elif code in qualifier_subfields:
					qualifier = qualifier_subfields[code]+': '+sf.text+'.'
					if 'qualifier' not in name:
						name['qualifier'] = qualifier
					else:
						name['qualifier'] += ' %s' % qualifier
			if 'qualifier' in name:
				sort_name += ' (%s)' % name['qualifier']

			if ind1 == '0':
				name['name_order'] = 'direct'
			elif ind1 == '1':
				name['name_order'] = 'inverted'		

			if tag == "100":
				name['authority_id'] = authority_id
				name['authorized'] = True
				name['is_display_name'] = True
				agent['title'] = sort_name
				agent['display_name'] = name
				agent['names'].append(name)

			elif tag == "400":
				name['authorized'] = False
				name['is_display_name'] = False
				agent['names'].append(name)

			name['sort_name'] = sort_name
			name['sort_name_auto_generate'] = True
			name['source'] = 'naf'
				

def corp(agent,tree,ns,authority_id):
	# agent-corporate  qualifiers
	qualifier_subfields = {
		'c': 'Location of meeting',
		'd': 'Date of meeting or treaty signing',
		'f': 'Date of work',
		'g': 'Miscellaneous information',
		'h': 'Medium',
		'k': 'Form subheading',
		'l': 'Language of a work',
		'o': 'Arranged statement for music',
		'p': 'Name of a part/section of a work',
		'r': 'Key for music',
		's': 'Version',
		't': 'Title of work',
		'u': 'Affiliation'
	}
	for field in tree.findall(".//marcxml:datafield", ns):
		tag = field.get("tag")
		ind1 = field.get("ind1")
		subfields = field.findall(".//marcxml:subfield", ns)
		sort_name = ""

		# get dates of existence
		if tag == "046":
			date(agent,subfields)
		# get Biographical notes
		if tag == "678":
			bio(agent,subfields)

		# get authorized and display name for corporate entity
		if tag == "110" or tag == "111" or tag == "410" or tag == "411":
			name = {}			
			for sf in subfields:
				code = sf.get("code")
				if code == "a":
					primary_name = sf.text
					name['primary_name'] = primary_name
					sort_name += primary_name	
				elif code == "b":
					if 'subordinate_name_1' not in name:
						subordinate_name_1 = sf.text
						name['subordinate_name_1'] = subordinate_name_1
						sort_name += subordinate_name_1
					else:
						name['subordinate_name_2'] = ""
						name['subordinate_name_2'] += "%s " % sf.text
						name['subordinate_name_2'].strip()
				elif code == "n":
					number = sf.text				
					name['number'] = number.replace("(","").replace(")","")			
				elif code in qualifier_subfields:
					qual = sf.text
					qualifier = qualifier_subfields[code]+': ' + qual.replace("(","").replace(")","") + '.'
					if 'qualifier' not in name:
						name['qualifier'] = qualifier
					else:
						name['qualifier'] += ' %s' % qualifier
			if 'subordinate_name_2' in name:
				sort_name += name['subordinate_name_2']
			if 'number' in name:
				sort_name += ' (%s)' % name['number']
			if 'qualifier' in name:
				sort_name += ' (%s)' % name['qualifier']

			if tag == "110" or tag == "111":
				name['authority_id'] = authority_id
				name['authorized'] = True
				name['is_display_name'] = True
				agent['title'] = sort_name
				agent['display_name'] = name
				agent['names'].append(name)

			elif tag == "410" or tag == "411":
				name['authorized'] = False
				name['is_display_name'] = False
				agent['names'].append(name)

			name['sort_name'] = sort_name
			name['sort_name_auto_generate'] = True
			name['source'] = 'naf'
				

def converter(uri,agentType):
	# Data
	agent = {
		"title": "",
	    "dates_of_existence": [],
	    "display_name": "",
	    "names": [],
	    "notes": [],
	    "publish": True,
	}

	# parsing marcxml	
	url = uri + ".marcxml.xml"
	response = requests.get(url)
	data = response.text

	tree = ElementTree.fromstring(data)

	# namespace
	ns = {'marcxml': 'http://www.loc.gov/MARC21/slim'}

	# get authority id
	authority_id = uri.split("/")[-1]
	
	if agentType == "person":
		person(agent,tree,ns,authority_id)
	elif agentType == "corporate":
		corp(agent,tree,ns,authority_id)
	
	return(json.dumps(agent))

def auth():
	auth = requests.post(l.baseURL + "/users/" + l.user + "/login?password=" + l.password).json()
	session = auth["session"]
	headers = {'X-ArchivesSpace-Session': session}
	return headers

def create(env,filename,agentType):
	headers = auth()
	agentAPI = {
		"corporate": "/agents/corporate_entities",
		"family": "/agents/families",
		"person": "/agents/people",
		"software": "/agents/software"
	}

	IDS = {}
	output = []

	f = open('./data/%s/%s.csv' % (env,filename), 'r', encoding='utf-8-sig')
	r = csv.reader(f)
	next(r)

	for row in r:
		name = row[1]
		uri = row[-1]
		lcnaf_id = uri.split("/")[-1]
		if lcnaf_id not in IDS:
			data = converter(uri,agentType)
			
			try:
				rq = requests.post(l.baseURL + agentAPI[agentType],
										headers=headers, 
										data=data).json()
				logging.info('%s, Name: %s, locID: %s',rq,name,lcnaf_id)
			except Exception as e:
				logging.exception('Failed, Name: %s, locID: %s',name,lcnaf_id)
				continue

			# Get aspace id of newly create agent record
			if 'id' in rq:
				newID = rq['id']
				# add id to the csv file 
				row.append(newID)
				# add new kay/value pair to IDS to check for duplicates
				IDS[lcnaf_id] = newID

		# or agent with LCNAF id has already created and add to the dict
		else:
			newID = IDS[lcnaf_id]
			row.append(newID)
		print(row)
		output.append(row)

	# write edited csv file with newly created aspace records
	# so the matched id can be merged
	fn = open('./data/%s/%s_imported.csv' % (env,filename), 'w', encoding='utf-8-sig')
	w = csv.writer(fn)
	w.writerow(['ASpace_ID','Names','Authority_ID','Source','Name_Recon','uri','New_ID'])
	w.writerows(output)
	fn.close()

def merge(env,filename,agentType):
	headers = auth()
	agentAPI = {
		"corporate": "/agents/corporate_entities",
		"family": "/agents/families",
		"person": "/agents/people",
		"software": "/agents/software"
	}
	mergeAPI = "/merge_requests/agent"
	mergeData = {
		"jsonmodel_type": "merge_request",
	  	"victims": [
		    {
		      "ref": ""
		    }
	  	],
	  	"target": {
	    	"ref": ""
	  	}
	}

	f = open('./data/%s/%s.csv' % (env,filename), 'r', encoding='utf-8-sig')
	r = csv.reader(f)
	next(r)
	for row in r:
		victim = row[0]
		target = row[-1]
		mergeData['victims'][0]['ref'] = agentAPI[agentType]+'/'+victim
		if target and 'http' not in target:
			mergeData['target']['ref'] = agentAPI[agentType]+'/'+target
			data = json.dumps(mergeData)
			try:
				rq = requests.post(l.baseURL + mergeAPI, headers=headers, data=data).json()
				logging.info('%s,%s,%s,%s',rq,victim,target,row[1])
			except Exception as e:
				logging.exception('%s,%s,%s',victim,target,row[1])
				continue
			print(rq)

