#!/bin/python3

from http.client import HTTPSConnection, RemoteDisconnected
import json, ssl, time
import subprocess
import re
import shutil
import os
import datetime

def clone_repo(clone_url):
	# git clone --bare <clone_url> repo
	print('Cloning {}'.format(clone_url))
	result = subprocess.run(['git', 'clone', '--bare', clone_url, 'repo'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', errors='ignore')
	if len(result.stdout) > 0:
		print(result.stdout)

def remove_repo():
	# rm -rf repo
	print('Removing clone')
	shutil.rmtree('repo')

def collect_commits():
	print('Structuring commit data')
	# git log --oneline --pretty="%H"
	result = subprocess.run(['git', 'log', '--oneline', '--pretty=%H'], cwd='repo', stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', errors='ignore')
	commit_order = result.stdout[:-1].split('\n')
	commit_dict = {}
	for i in range(len(commit_order)):
		commit_dict[commit_order[i]] = {'position': i}
	return {"order": commit_order, "dict": commit_dict}

def collect_reverts():
	print('Finding reverts')
	# git log --grep "This reverts commit" --pretty=format:"%H"
	result = subprocess.run(['git', 'log', '--grep', 'This reverts commit', '--pretty=%H'], cwd='repo', stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', errors='ignore')
	reverts = []
	if len(result.stdout) > 0:
		reverts = result.stdout[:-1].split('\n')
	return reverts

def find_full_commit(commit):
	# git log -n1 <commit> | grep -oE "This reverts commit [0-9a-f]*" |sed "s/This reverts commit //g"
	result = subprocess.run(['git', 'log', '-n1', '--pretty=%H', commit], cwd='repo', stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', errors='ignore')
	fullhash = result.stdout[:-1]
	if len(fullhash) > 40:
		fullhash = None
	return fullhash

def reverts_what(commit):
	# git log -n1 <commit> | grep -oE "This reverts commit [0-9a-f]*" |sed "s/This reverts commit //g"
	result = subprocess.run(['git', 'log', '-n1', commit], cwd='repo', stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', errors='ignore')
	# Assume there's only one
	search = re.search('This reverts commit ([0-9a-f]*)', result.stdout) if len(result.stdout) > 0 else None
	found = search.group(1) if search else None
	return found

def traverse_log():
	print('Traversing log')
	# git log <commit> -n1 --pretty=raw
	# git log <commit> -n1 --pretty="" --cc
	result = subprocess.run(['git', 'log', 'HEAD', '-n1', '--pretty=raw'], cwd='repo', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	print(result.stdout)
	result = subprocess.run(['git', 'log', 'hEAD', '-n1', '--pretty=""', '--cc'], cwd='repo', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	print(result.stdout)

def parent_tag(commit):
	# git tag --no-contains <commet> --sort=-creatordate | head -n1
	#result = subprocess.run(['git', 'tag', '--no-contains', commit, '--sort=-creatordate'], cwd='repo', stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', errors='ignore')
	#tags = result.stdout.split('\n')[:-1]

	# git describe --tag --first-parent --abbrev=0 <commit> | cut -f1 -d"~"`
	result = subprocess.run(['git', 'describe', '--tag', '--first-parent', '--abbrev=0', commit], cwd='repo', stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', errors='ignore')
	end = result.stdout.find('~')
	if end < 0:
		end = result.stdout.find('\n')
	if end < 0:
		end = len(result.stdout)
	truncated = result.stdout[:end]
	tag = None
	if len(truncated) > 0:
		tag = truncated
	return tag

def tag_commit(tag):
	# git rev-list -n1 <tag>
	result = subprocess.run(['git', 'rev-list', '-n1', tag], cwd='repo', stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', errors='ignore')
	return result.stdout[:-1]

def count_changes(commit):
	# git log <commit> -n1 --pretty="" --cc
	result = subprocess.run(['git', 'log', commit, '-n1', '--pretty=format:""', '--cc'], cwd='repo', stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', errors='ignore')
	files_changed = 0
	blocks_changed = 0
	lines_added = 0
	lines_removed = 0
	lines = result.stdout.split('\n')[:-1]
	skip_arithmetic = False
	for line in lines:
		if line[:5] == 'diff ':
			skip_arithmetic = True
			files_changed += 1
		if line[:3] == '@@ ':
			skip_arithmetic = False
			blocks_changed += 1
		if not skip_arithmetic:
			if line[:1] == '+':
				lines_added += 1
			if line[:1] == '-':
				lines_removed += 1
	return {'files_changed': files_changed, 'blocks_changed': blocks_changed, 'lines_added': lines_added, 'lines_removed': lines_removed}

def analyse_repository():
	master = collect_commits()
	reverts = collect_reverts()
	master['reverts'] = reverts
	print("Found {} reverts".format(len(reverts)))
	for revert in reverts:
		reverted = reverts_what(revert)
		if reverted and len(reverted) > 0:
			reverted = find_full_commit(reverted)
		if reverted and len(reverted) > 0:
			master['dict'][revert]['reverts'] = reverted
			tag = parent_tag(reverted)
			base = tag_commit(tag) if tag else master['order'][-1]
			master['dict'][revert]['base'] = base
			print('{} reverts {} with base {}'.format(revert, reverted, base))

	if len(reverts) > 0:
		print('Analysing changes')
		for commit in master['order']:
			changes = count_changes(commit)
			for key in changes:
				master['dict'][commit][key] = changes[key]
	else:
		print('No reverts, skipping')
		master = None

	return master

def export_json(filename, master):
	with open(filename, 'w') as fileout:
		  json.dump(master, fileout, sort_keys=False, indent=2)

def load_index():
	index = {'count': 0, 'filecount': 0, 'repos': []}
	repos = []
	try:
		with open('results/index.json', 'r') as filein:
			index = json.load(filein)
			repos = index['repos']
	except Exception:
		print('No index on disk, starting from scratch')
	index['index'] = {}
	for i in range(len(repos)):
		index['index'][repos[i]['clone_url']] = {'pos': i}
	return index

def save_index(index):
	# Don't bother saving the index as we can reconstruct it at load time
	to_save = {'count': index['count'], 'filecount': index['filecount'], 'repos': index['repos']}
	with open('results/index.json', 'w') as fileout:
		  json.dump(to_save, fileout, sort_keys=False, indent=2)

def find_in_index(index, clone_url):
	pos = None
	if 'index' in index:
		if clone_url in index['index']:
			item = index['index'][clone_url]
			if 'pos' in item:
				pos = item['pos']
	return pos

def add_to_index(index, clone_url, filename, status):
	pos = find_in_index(index, clone_url)
	data = {'clone_url': clone_url, 'status': status}
	data['time_checked'] = str(datetime.datetime.now())
	if filename and len(filename) > 0:
		data['filename'] = filename
	if pos == None:
		pos = len(index['repos'])
		index['index'][clone_url] = {'pos': pos}
		index['repos'].append(data)
	else:
		index['repos'][pos] = data

host = 'api.github.com'
#search = '/search/repositories?q=language:c+fork:false&sort=forks'
search = '/search/repositories?q=language:c+fork:false&sort=updated'
useragent = 'bisecttest'
ssl_context = ssl.create_default_context()
connction = HTTPSConnection(host)
count = 0
filecount = 0

if os.path.exists('repo'):
	remove_repo()
if not os.path.exists('results'):
	os.mkdir('results')
index = load_index()
count = index['count']
filecount = index['filecount']

while search:
	#print("Search: {}".format(search))
	print('Starting analysis {}'.format(count))
	print('File number {}'.format(filecount))
	print('Making github request')
	connction.request('GET', search, headers={'User-Agent': useragent})

	# Continue trying until we hit a exception we can't handle
	response = None
	while not response or response.status != 200:
		try:
			response = connction.getresponse()
		except RemoteDisconnected as e:
			# That's rude. Wait 5 mins and try again
			print("Network error: {}".format(str(e)))
			print("Will try again in 5 minutes")
			time.sleep(5*60)

	data = response.read()
	links = response.headers["Link"]
	#lastlink = [link for link in links.split(',') if 'rel="last"' in link][0]
	#last = int(lastlink[lastlink.find('page=') + 5 : lastlink.find('>')])
	if links == None:
		print(response.headers)

	nexttext = [link for link in links.split(', ') if 'rel="next"' in link]
	if len(nexttext) > 0:
		search = nexttext[0][23 : -13]
	else:
		search = None

	results = json.loads(data)
	if not results or 'items' not in results or len(results['items']) == 0:
		print(results)
	else:
		for item in results['items']:
			clone_url = item['clone_url']
			filename = None
			leafname = None
			status = 'No reverts'
			print('Analysing repo: {}'.format(item['name'], clone_url))
			pos = find_in_index(index, clone_url)
			if not pos == None:
				print('Already analysed, skipping')
			else:
				clone_repo(clone_url)
				master = analyse_repository()
				if master:
					master['name'] = item['name']
					master['clone_url'] = clone_url
					leafname = 'data{:05}.json'.format(filecount)
					filename = 'results/{}'.format(leafname)
					export_json(filename, master)
					print('Exported to {}'.format(leafname))
					filecount += 1
					index['filecount'] = filecount
					status = 'Analysed'
				count += 1
				index['count'] = count
				add_to_index(index, clone_url, leafname, status)
				save_index(index)
				remove_repo()
				print('Completed analysis {}'.format(count))
			# Rate limit to avoid github cutting us off (max 60 requests per minute, 30 items per page)
			time.sleep(0.04)


