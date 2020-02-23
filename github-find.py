#!/bin/python3

from http.client import HTTPSConnection
import json, ssl, time
import subprocess
import re
import shutil

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
	with open(filename, 'w') as output:
		  json.dump(master, output, sort_keys=False, indent=2)

host = 'api.github.com'
#search = '/search/repositories?q=language:c+fork:false&sort=forks'
search = '/search/repositories?q=language:c+fork:false&sort=updated'
useragent = 'bisecttest'
ssl_context = ssl.create_default_context()
connction = HTTPSConnection(host)
count = 0

while search:
	#print("Search: {}".format(search))
	print('Starting analysis {}'.format(count))
	print('Making github request')
	connction.request('GET', search, headers={'User-Agent': useragent})
	response = connction.getresponse()
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
			print('Analysing repo: {}'.format(item['name'], item['clone_url']))
			clone_repo(item['clone_url'])
			master = analyse_repository()
			if master:
				master['name'] = item['name']
				master['clone_url'] = item['clone_url']
				filename = 'results/data{:05}.json'.format(count)
				export_json(filename, master)
				count += 1
			remove_repo()
			time.sleep(0.2)
			print('Completed analysis {}'.format(count))


