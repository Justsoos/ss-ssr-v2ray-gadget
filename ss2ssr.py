#! /usr/bin/env python3

__author__ = 'JZ'
__webpage__ = 'https://github.com/Justsoos'

import re
import sys,os
import logging
import json
import time
import argparse
import base64
import traceback

from glob import glob


def remove_dup_jsons(json_list):
	l = json_list
	if not l:
		return
	dest_list = []
	dup_list = []
	dup_times = 0
	num = len(l)
	bad_records = {}
	good_records = []
	# Looking for None record
	for ie in range(num):
		if not ie:
			continue
		try:
			if (
				l[ie]['server'] and
				l[ie]['server_port'] and
				l[ie]['password'] and
				l[ie]['method']
				):
				good_records.append(ie)
				l[ie]['server_port'] = int(l[ie]['server_port'])
		except KeyError as err:
			bad_records[ie] = err

	if num <= 1:
		return l
	#print(bad_records, good_records)
	if bad_records and good_records:
		n = good_records
	else:
		n = list(range(num))
	# Looking for duplicate
	l_max = len(n)
	for i in range(l_max):
		for j in range((i+1), l_max):
			try:
				if (
					(l[n[i]]['server'] == l[n[j]]['server']) and 
					(int(l[n[i]]['server_port']) == int(l[n[j]]['server_port'])) and
					(l[n[i]]['password'] == l[n[j]]['password']) and
					(l[n[i]]['method'] == l[n[j]]['method'])
					):
					dup_times += 1
					#dup_list.append(l[n[i]])
					dest_found = False
					break
				else:
					dest_found = True
			except:
				raise
		if dest_found:
			dest_list.append(l[n[i]])

	if bad_records:
		for line, erro in bad_records.items():
			print('***The No.{} record seems wrong with {}...'.format(line+1, erro))
	#print('There are {} records inputed.'.format(num))
	#print('Found {} times of duplicate records.'.format(dup_times))

	return dest_list

def remove_dup_links(url_list):
	l = list({}.fromkeys(url_list).keys())
	dest_list = []
	for line in l:
		ls = line.strip()
		if len(ls) > 10:
			dest_list.append(ls)
	return dest_list

def sslink2json(single_link):
	if not single_link:
		return None
	remarks = ''
	obfs = 'plain'
	link = to_str(single_link)
	#print(link)
	try:
		if link[:5] == 'ss://':
			t = link[5:]
		elif link[:6] == 'ssr://':
			raise ValueError('Not SS, but SSR address: {}'.format(link))
		else:
			return

		if '#' in t:
			s = t.split('#',1)
			t = s[0]
			remarks = s[1]

		if '@' not in t:
			t = b64decode(t)
		elif ':' not in (t.split('@',1)[0]):
			odd_ss = b64decode(t.split('@',1)[0])
			t = '{}@{}'.format(odd_ss, t.split('@',1)[1])
		else:
			pass

		t.strip('/')
	except Exception as e:
		raise e
	
	result = {}
	d = t.split(':')

	if len(d) == 3:
		result['server'] = d[1].rsplit('@',1)[1]
		result['server_port'] = int(d[2])
		result['password'] = d[1].rsplit('@',1)[0]
		result['method'] = d[0]
		result['plugin'] = ''
		result['plugin_opts'] = ''
		result['obfs'] = 'plain'
		result['remarks'] = remarks
		result['timeout'] = 5
	elif len(d) >= 4:
		print('!!! THERE IS A BAD SS URI ??!!{} {}'.format(d, link))
		return None
	else:
		pass

	return result

def ssjsons2ssrlinks(jsons):
	d = jsons
	links = []
	try:
		if (isinstance(d, dict)) and d['configs']:
			j = d['configs']
		else:
			j = d

		for i in j:
			server = i.get('server')
			server_port = i.get('server_port')
			password = i.get('password')
			method = i.get('method')
			obfs = i.get('obfs', 'plain')
			remarks = i.get('remarks')
			uri = '{}:{}:origin:{}:{}:{}'.format(server, server_port, method, obfs, b64encode(password))
			group = b64encode('SS-2-SSR_{}'.format(time.strftime('%Y.%m.%d_%H.%M')))
			stern = '/?obfsparam=&remarks={}&group={}'.format(b64encode(remarks), group)
			links.append('ssr://{}'.format(b64encode(('{}{}'.format(uri, stern)))))
	except:
		raise
	return links

def to_bytes(s):
	if type(s) == str:
		return s.encode('utf-8')
	return s

def to_str(s):
	if type(s) == bytes:
		return s.decode('utf-8')
	return s

def b64encode(data):
	if type(data) == bytes:
		return to_str(base64.urlsafe_b64encode(data)).strip('=')
	elif type(data) == str:
		return to_str(base64.urlsafe_b64encode(to_bytes(data))).strip('=')
	else:
		return data

def b64decode(data):
	if type(data) == str:
		return to_str(base64.urlsafe_b64decode(data+'='*(4-len(data)%4)))
	return data

def read_links_file(file):
	with open(file, 'rb') as f:
		links = f.readlines()
	return links

def read_configs_file(file):
	try:
		with open(file, 'rb') as f:
			d = json.load(f)
			if (isinstance(d, dict)) and d['configs']:
				l = d['configs']
			elif (isinstance(d, list)):
				l = d
			else:
				raise Exception('Wrong or Damaged SS config file...Pls check check {}'.format(file))
	except KeyError:
		pass
	return l

def func_1st(configs, links):
	if configs:
		j0 = configs
		t0 = len(j0)
	else:
		t0 = 0
		j0 = []

	if links:
		l1 = links
		l2 = remove_dup_links(l1)
		t1 = len(l1)
	else:
		t1 = 0
		l2 = []
		t12 = 0

	for li in l2:
		if sslink2json(li):
			j0.append(sslink2json(li))

	t2 = len(j0)

	#print(j0)

	j2 = remove_dup_jsons(j0)
	if j2:
		t3 = len(j2)
		links_result = ssjsons2ssrlinks(j2)
	else:
		t3 = 0
		links_result = None

	info = '*** From configs JSON file: {} records, from link URI file: {} records. Total: {}. After json-inside duplicate remove, {} links here. '.format(t0, t1, t2, t3)
	print(info)

	if links_result:
		links_file = 'SS_to_SSR_links_{}.txt'.format(time.strftime('%Y-%m-%d_%H-%M-%S'))
		with open(links_file, 'w', encoding='utf-8') as f:
			for i in links_result:
				print(i, file=f)
		print('*** {} SS to SSR Links records saved to {} ...'.format(len(links_result), links_file))


def main_dev():
	global json_files
	global uri_files
	global link_ss

	parser = argparse.ArgumentParser( description='de-duplicate, merge, convert SS to SSR uri and backup tools for Shadowsocks, working under Python3')
	parser.add_argument('-j', metavar='input JSON filenames', dest='json_files', type=str, nargs='+', help='Input json or SS config filenames')
	parser.add_argument('-l', metavar='input Link filenames', dest='uri_files', type=str, nargs='+', help='Input uri link filenames')
	parser.add_argument('-s', metavar='ss links', dest='link_ss', type=str, nargs='+', help='Input SS links...single or more')
	parser.add_argument('-v',action='version', version='ss to ssr 0.2')
	args = parser.parse_args()

	if args.json_files:
		json_files = (glob(name) for name in args.json_files)
		json_files = [i for j in json_files for i in j]
		json_files = list(set(json_files))
	else:
		json_files = None

	if args.uri_files:
		uri_files = (glob(name) for name in args.uri_files)
		uri_files = [i for j in uri_files for i in j]
		uri_files = list(set(uri_files))
	else:
		uri_files = None

	if args.link_ss:
		sign = set(((x.strip('\''))[:5] == 'ss://' for x in args.link_ss))
		if len(sign) == 1 and True in sign:
			link_ss = [y.strip('\'') for y in args.link_ss]
		else:
			parser.print_help()
			print('*** Please input correct ss:// link')
			sys.exit(1)
	elif ((len(sys.argv) < 2) or ((not json_files) and (not uri_files))):
		parser.print_help()
		sys.exit(1)
	else:
		link_ss = None

	print(args)
	print('*** Working on ... ', json_files, uri_files, link_ss)


def main():
	global json_files
	global uri_files
	global link_ss
	
	main_dev()

	if link_ss:
		for i in link_ss:
			js = sslink2json(i)
			ls = ssjsons2ssrlinks([js])
			print(''.join(ls))
		sys.exit(1)

	configs = []
	links = []

	if json_files:
		for i in json_files:
			configs.extend(read_configs_file(i))

	if uri_files:
		for j in uri_files:
			links.extend(read_links_file(j))

	func_1st(configs, links)


if __name__ == '__main__':
	main()
