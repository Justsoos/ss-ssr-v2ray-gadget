#! /usr/bin/env python3

__author__ = 'JZ'
__webpage__ = 'https://github.com/Justsoos'

import os
import sys
import json
import time
import argparse

from glob import glob

def remove_jsons_dups(input_jsons):
	l = input_jsons
	dest_list = []
	dup_list = []

	try:
		num = len(l)
		for i in range(num):
			for j in range((i+1),num):
				if (
					(l[i]['server'] == l[j]['server']) and 
					(int(l[i]['server_port']) == int(l[j]['server_port'])) and
					(l[i]['password'] == l[j]['password']) and
					(l[i]['method'] == l[j]['method']) and
					(l[i]['protocol'] == l[j]['protocol']) and
					(l[i]['protocolparam'] == l[j]['protocolparam']) and
					(l[i]['obfs'] == l[j]['obfs']) and
					(l[i]['obfsparam'] == l[j]['obfsparam'])
					):
					dup_list.append(l[i])
					dest_found = False
					break
			else:
				dest_found = True
			if dest_found:
				dest_list.append(l[i])
	except KeyError as err:
		print('The No.{} record seems wrong with {}...'.format(j, err))
		raise

	print('There are {} total input records.'.format(num))
	print('Found {} times of duplicate records.'.format(len(dup_list)))

	return dest_list, dup_list

def read_configs_file(file):
	try:
		with open(file, 'rb') as f:
			d = json.load(f)
			if (isinstance(d, dict)) and d['configs']:
				l = d['configs']
			elif (isinstance(d, list)):
				l = d
			else:
				raise Exception('Wrong or Damaged SSR config/json file...Pls check check "{}"'.format(file))
	except KeyError as e:
		print('*** Some Config file seems get wrong ... ', e)
		return None
	except json.decoder.JSONDecodeError as err:
		print('*** {} is not correct json/config file... pls check check... '.format(file))
		raise
	return l

def main_dev():
	global only_test
	global input_files
	global target
	
	parser = argparse.ArgumentParser(description='gui-config.json de-duplicate and backup tool for ShadowsocksR-csharp, working under Python3')
	parser.add_argument('-j', dest='input_files', metavar='SSR json files', type=str, nargs='+', help='SSR gui-config.json or json-stored files')
	parser.add_argument('-o', dest='target', metavar='Target SSR gui-config.json file', type=str, nargs=1, help='Assign your own SSR gui-config.json file')
	parser.add_argument('-t', dest='only_test', action='store_true', default=False, help='Set it for just testing, no output file')
	parser.add_argument('-v',action='version', version='SSR de-duplicate 0.1')
	args = parser.parse_args()

	#print(args)
	if args.only_test:
		only_test = True
	else:
		only_test = False
	print(args)

	if (not args.input_files) and (not args.target) and (os.path.exists('gui-config.json')):
		input_files = ['gui-config.json']
		target = 'gui-config.json'
		print('*** No input file name, looking for "gui-config.json" file in current dir and do sth...')
	elif (not args.input_files) and args.target and (os.path.exists(args.target[0])):
		input_files = [args.target[0]]
		target = args.target[0]
		check_config_file(target)
	elif args.input_files:
		t = (glob(x) for x in args.input_files)
		s = [i for j in t for i in j]
		input_files = list(set(s))
		if args.target and os.path.exists(args.target[0]) and check_config_file(args.target[0]):
			target = args.target[0]
		elif not args.target:
			target = None
		else:
			pass
	else:
		print('*** Can not find SSR named "gui-config.json" file, pls assign with -o option....')
		parser.print_help()
		sys.exit(1)

def check_config_file(file):
	with open(file, 'rb') as f:
		d = json.load(f)
		if (isinstance(d, dict)) and d.get('configs'):
			return True
		else:
			print('*** Wrong or Bad SSR gui-config.json file -- {}!! Pls check check...'.format(args.target[0]))
			sys.exit(1)

def end(dest_list, dup_list, target, only_test):
	if len(dup_list) == 0:
		print('No duplicate found, Good luck! guys...')
	if only_test:
		print('Just TEST, no output file...')
		return
	if dest_list and isinstance(dest_list, list):
		pass
	else:
		print('*** Sth wrong... no processing result ... exit...')
		return

	try:
		if target:
			with open(target, 'rb') as f:
				d = json.load(f)
				d['configs'] = dest_list
			output_file = 'de_Dup_{}_gui-config.json'.format(time.strftime('%Y-%m-%d_%H-%M-%S'))
			print('*** {} de-duplicate SSR Congfig file saved as \"{}\", just copy & paste then raname it to apply to SSR...'.format(len(dest_list), output_file))
		else:
			output_file = 'de_Dup_{}.json'.format(time.strftime('%Y-%m-%d_%H-%M-%S'))
			d = dest_list
			print('*** {} de-duplicate SSR records saved to \"{}\". '.format(len(dest_list), output_file))
		with open(output_file, 'w', encoding='utf-8') as o:
			json.dump(d, o, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
	except:
		raise

	try:
		if dup_list:
			dup_file = 'Dup_{}.json'.format(time.strftime('%Y-%m-%d_%H-%M-%S'))
			with open(dup_file, 'w', encoding='utf-8') as p:
				json.dump(dup_list, p, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
			print('*** {} Duplicate SSR records saved to \"{}\" ...'.format(len(dup_list), dup_file))	
	except:
		raise
	'''
	out = json.dumps(d, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
	with open(output_file, 'wb') as o:
		o.write(out.encode('utf-8'))
	'''

def main():
	global only_test
	global input_files
	global target
	main_dev()

	input_jsons = []
	try:
		for i in input_files:
			l = read_configs_file(i)
			if l:
				input_jsons.extend(l)
	except:
		raise
	
	if input_jsons and isinstance(input_jsons, list):
		dest_list, dup_list = remove_jsons_dups(input_jsons)
		end(dest_list, dup_list, target, only_test)
	else:
		print('Something wrong, pls check check...')
		parser.print_help()
		sys.exit(1)

if __name__ == '__main__':
	main()
