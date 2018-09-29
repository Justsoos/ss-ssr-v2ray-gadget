#! /usr/bin/env python3

__author__ = 'JZ'
__webpage__ = 'https://github.com/Justsoos'

import re
import sys,os
# import socks
import socket
import multiprocessing
import threading
import logging
import json
import time
import requests
import argparse
import subprocess
import base64

from glob import glob

from pprint import pprint
from requests.adapters import HTTPAdapter
from multiprocessing import Pool

logging.getLogger().setLevel(logging.DEBUG)
logging.debug('')

def run_v(conf, t_conf):
	if int(conf.get('configType')) != 1:
		return None
	try:
		users = {}
		users['id'] = conf.get('id')
		users['alterId'] = int(conf.get('alterId', '0'))
		users['security'] = conf.get('security', 'aes-128-gcm')
		u = []
		u.append(users)

		vnext = {}
		vnext['address'] = conf.get('address')
		vnext['port'] = int(conf.get('port'))
		vnext['users'] = u

		v = []
		v.append(vnext)

		t_conf['outbound']['settings']['vnext'] = v

		t_conf['outbound']['streamSettings']['network'] = conf.get('network')

		t_conf['outbound']['streamSettings']['wsSettings'] = None
		t_conf['outbound']['streamSettings']['kcpSettings'] = None
		t_conf['outbound']['streamSettings']['tcpSettings'] = None
		
		network = conf.get('network')
		if network == 'ws':
			t_conf['outbound']['streamSettings']['wsSettings'] = \
				{
					'connectionReuse': True,
					'path': None,
					'headers': None
				}
			t_conf['outbound']['streamSettings']['wsSettings']['headers'] = (conf.get('headerType'), None)[conf.get('headerType') == 'none']

			re = conf.get('requestHost')
			if ';' in re:
				r = re.split(';')
				t_conf['outbound']['streamSettings']['wsSettings']['path'] = r[0]
				t_conf['outbound']['streamSettings']['wsSettings']['headers']['Host'] = r[1]
			else:
				t_conf['outbound']['streamSettings']['wsSettings']['path'] = re

		elif network == 'kcp':
			t_conf['outbound']['streamSettings']['kcpSettings'] = \
				{
					'mtu': 1350,
					'tti': 10,
					'uplinkCapacity': 20,
					'downlinkCapacity': 100,
					'congestion': True,
					'readBufferSize': 4,
					'writeBufferSize': 4,
					'header': {
						'type': None,
						'request': None,
						'response': None
					}
				}

			t_conf['outbound']['streamSettings']['kcpSettings']['header']['type'] = (conf.get('headerType'), 'none')[conf.get('headerType') == 'none']

		elif network == 'tcp':
			t_conf['outbound']['streamSettings']['tcpSettings'] = \
				{
					'connectionReuse': True,
					'header': {
						'type': None,
						'request': {
							'version': '1.1',
							'method': 'GET',
							'path': [
								'/'
							],
							'headers': {
								'Host': [
									''
								],
								'User-Agent': [
									'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36',
									'Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_2 like Mac OS X) AppleWebKit/601.1 (KHTML, like Gecko) CriOS/53.0.2785.109 Mobile/14A456 Safari/601.1.46'
								],
								'Accept-Encoding': [
									'gzip,deflate'
								],
								'Connection': [
									'keep-alive'
								],
								'Pragma': 'no-cache'
							}
						},
						'response': {
							'version': '1.1',
							'status': '200',
							'reason': 'OK',
							'headers': {
								'Content-Type': [
									'application/octet-stream',
									'video/mpeg'
								],
								'Transfer-Encoding': [
									'chunked'
								],
								'Connection': [
									'keep-alive'
								],
								'Pragma': 'no-cache'
							}
						}
					}
				}
			if conf.get('headerType') == 'none' or conf.get('headerType') == '':
				t_conf['outbound']['streamSettings']['tcpSettings'] = None
			else:
				t_conf['outbound']['streamSettings']['tcpSettings']['header']['type'] = (conf.get('headerType'), None)[conf.get('headerType') == 'none']
				t_conf['outbound']['streamSettings']['tcpSettings']['header']['request']['headers']['Host'] = conf.get('requestHost', '').split(',')

		elif network == 'h2' or network == 'http':

			t_conf['outbound']['streamSettings']['httpSettings'] = \
				{
					'path': None,
					'host': []
				}

			t_conf['outbound']['streamSettings']['httpSettings']['path'] = conf.get('path')
			t_conf['outbound']['streamSettings']['httpSettings']['Host'] = list(conf.get('requestHost'))

		else:
			raise NameError("unkonwn network", network)

		t_conf['outbound']['streamSettings']['security'] = (conf.get('streamSecurity'), '')[conf.get('streamSecurity') == None]

		t_conf['outbound']['protocol'] = 'vmess'

		port = get_free_tcp_port()
		if not port:
			raise Exception('Error getting local port.')
		t_conf['inbound']['port'] = int(port)
		
		t_conf['inbound']['listen'] = '127.0.0.1'
		t_conf['inbound']['protocol'] = 'socks'
		t_conf['inbound']['settings']['auth'] = 'noauth'
		t_conf['inbound']['settings']['ip'] = '127.0.0.1'
	except:
		raise
	#remarks = conf.get('remarks', None)
	temp_file = 'temp_file_{}_{}.json'.format(int(round(time.time() * 1000)), port)
	with open(temp_file, 'w') as f:
		json.dump(t_conf, f)

	if not os.path.isfile(temp_file):
		logging.debug('here missing missing: '.format(temp_file))

	cmd_line = 'v2ray.exe --config={}'.format(temp_file)
	logging.debug('checking id: {} with port {}'.format(users['id'], port))
	try:
		p = subprocess.Popen(cmd_line, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
	except:
		raise
	time.sleep(0.8)
	return p, port, temp_file

def test_connect(port):
	perfect = 9
	sum_r = 0
	time.sleep(2)
	get_latency(port)
	time.sleep(2)
	for i in range(1,10):
		time.sleep(0.1)
		r, p = get_latency(port)
		if p is True:
			print('.', end='')
			sum_r += r
			perfect -= 1
	if perfect != 9:
		times = 9 - int(perfect)
		s = sum_r / times
		latency = format(s, '0.2f')
	else:
		latency = 0
	return perfect, latency

def get_latency(port):
	test_urls = 'https://www.google.com/'
	headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'}
	proxies = {}
	proxies['http'] = 'socks5h://127.0.0.1:{}'.format(port)
	proxies['https'] = 'socks5h://127.0.0.1:{}'.format(port)

	start_time = time.time()
	s = requests.Session()
	try:
		s.mount(test_urls, HTTPAdapter(max_retries=0))
		r = s.get(test_urls, proxies=proxies, headers=headers, verify=True, timeout=(7,15), allow_redirects=False, cookies={'':''})
		r.raise_for_status()
		connectivity = True
	except Exception as err:
		print(err)
		connectivity = False
	end_time = time.time()
	
	latency_time = end_time - start_time
	return latency_time, connectivity

def sub_proc(proc, single_json, t_conf):
	proc, port, temp_file = run_v(single_json, t_conf)

	try:
		perfect, latency = test_connect(port)
	except:
		raise
	
	proc.kill()

	logging.debug('process what ? {}'.format(proc))
	stdout, stderr = proc.communicate()
	logging.debug('stdout of process{}'.format(stdout))
	logging.debug('stdERR of process{}'.format(stderr))

	if not os.path.isfile(temp_file):
		logging.debug('missing temp config file: {}'.format(temp_file))
		raise ValueError('config file missing...')

	os.remove(temp_file)

	return single_json, perfect, latency

def multi_proc(configs):
	global t_conf
	multiprocessing.freeze_support()
	proc = multiprocessing.Pool(16)

	proc_result = []
	if isinstance(configs, dict):
		t = []
		t.append(configs.copy())
		configs = t

	for i, ei in enumerate(configs):
		r = proc.apply_async(sub_proc, args=(i, ei, t_conf))
		proc_result.append(r)

	proc.close()
	proc.join()

	configs_all = []
	for k in proc_result:
		configs_all.append(k.get())
	
	info = []
	configs_good_temp = []
	configs_bad_temp = []
	configs_bad = []
	configs_good = []
	for j in configs_all:
		info.append((j[1],j[2]))
		if j[1] == 9:
			configs_bad_temp.append(j[0])
		else:
			configs_good_temp.append(j)

	if configs_good_temp:
		configs_good_temp.sort(key = lambda x:x[2])
		configs_good_temp.sort(key = lambda x:x[1])
		for i in configs_good_temp:
			r = re.match('^\d_\d\.\d{2}_(.*)', i[0].get('remarks'))
			if r:
				remarks = r.group(1)
			else:
				remarks = i[0].get('remarks')
			remarks = '{}_{}_{}'.format(i[1], i[2], remarks)
			i[0]['remarks'] = remarks[:60]
			configs_good.append(i[0])

	if configs_bad_temp:
		for k in configs_bad_temp:
			r = re.match('^\d_\d\.\d{2}_(.*)', k.get('remarks'))
			if r:
				remarks = r.group(1)
			else:
				remarks = k.get('remarks')
			remarks = '{}_{}_HCR_{}'.format('9', '9.99', remarks)
			k['remarks'] = remarks[:60]
			configs_bad.append(k)
	
	return configs_good, configs_bad, info

def deDup(conf):
	dest_list = []
	dup_list = []
	global other_list
	other_list = []
	try:
		for i, ei in enumerate(conf):
			if int(ei.get('configType')) != 1:
				other_list.append(ei)
				continue
			for j, ej in enumerate(conf[i+1:]):
				if (
					(ei['address'] == ej['address']) and
					(int(ei['port']) == int(ej['port'])) and
					(ei['id'] == ej['id']) and
					(int(ei['alterId']) == int(ej['alterId'])) and
					(ei['network'] == ej['network']) and
					(ei['headerType'] == ej['headerType']) and
					(ei['requestHost'] == ej['requestHost']) and
					(ei['streamSecurity'] == ej['streamSecurity']) and
					(int(ei['configType']) == int(ej['configType']))
					):
					dup_list.append(ei)
					dest_found = False
					break
				else:
					dest_found = True
			if dest_found:
				dest_list.append(ei)
	except KeyError as err:
		print('The No.{} record seems wrong with {}...'.format((i+j), err))
		raise
	deDup_info = '**** All records: {}, found dups: {}, unique VMESS records: {}, non VMESS records: {}'.format(len(conf), len(dup_list), len(dest_list), len(other_list))
	return dest_list, dup_list, deDup_info

def get_free_tcp_port():
	tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	tcp.bind(('', 0))
	addr, port = tcp.getsockname()
	tcp.close()
	return port

def rewrite_socks_dns(address, timeout=None, source_address=None):
	sock = socks.socksocket()
	sock.connect(address)
	return sock

def kill():
	cmd_task = 'taskkill /f /t /im'
	kill_list = ['v2rayN.exe', 'v2ray.exe', 'v2ctl.exe', 'wv2ray.exe']
	try:
		for i in kill_list:
			cmd = '{} {}'.format(cmd_task, i)
			s = subprocess.call(cmd)
			print(s)
	except:
		pass

def files(wildcard_file_args):
	if wildcard_file_args:
		file_list = (glob(name) for name in wildcard_file_args)
		file_list = [i for j in file_list for i in j]
		file_list = list(set(file_list))
	else:
		file_list = None
	return file_list

def main_dev():

	global json_files
	global uri_files
	global only_test

	parser = argparse.ArgumentParser( description='de-duplicate, merge, test, benchmark and backup tools for v2ray with v2rayN, M$ Windows')
	parser.add_argument('-j', metavar='input JSON filenames', dest='json_files', default=False, type=str, nargs='+', help='Input json filenames')
	parser.add_argument('-l', metavar='input Link filenames', dest='uri_files', default=False, type=str, nargs='+', help='Input uri link filenames')
	parser.add_argument('-t', dest='only_test', action='store_true', default=False, help='Just test, no output file')
	parser.add_argument('-v',action='version', version='0.2')
	args = parser.parse_args()

	json_files = files(args.json_files)
	uri_files = files(args.uri_files)
	only_test = args.only_test

	if not args.json_files and not args.uri_files:
		json_files = ['guiNConfig.json']

def main():
	# socket.socket = socks.socksocket
	# socket.create_connection = rewrite_socks_dns

	global json_files
	global uri_files
	global only_test
	global other_list

	main_dev()

	kill()

	global t_conf
	t_conf = \
	{
		'log': {
			'access': None,
			'error': None,
			'loglevel': None
		},
		'inbound': {
			'port': 48080,
			'listen': '127.0.0.1',
			'protocol': 'socks',
			'settings': {
				'auth': 'noauth',
				'udp': False,
				'ip': '127.0.0.1',
				'clients': None
			},
			'streamSettings': None
		},
		'outbound': {
			'tag': 'agentout',
			'protocol': 'vmess',
			'settings': {
				'vnext': [
					{
						'address': '213.213.213.213',
						'port': 23333,
						'users': [
							{
								'id': 'dddda000-bbbb-4444-2222-fffff6666666',
								'alterId': 100,
								'security': 'aes-128-gcm'
							}
						]
					}
				],
				'servers': None
			},
			'streamSettings': {
				'network': None,
				'security': None,
				'tcpSettings': None,
				'kcpSettings': None,
				'wsSettings': None
			},
			'mux': {
				'enabled': False
			}
		},
		'inboundDetour': None,
		'outboundDetour': [
			{
				'protocol': 'freedom',
				'settings': {
					'response': None
				},
				'tag': 'direct'
			},
			{
				'protocol': 'blackhole',
				'settings': {
					'response': {
						'type': 'http'
					}
				},
				'tag': 'blockout'
			}
		],
		'dns': {
			'servers': [
				'8.8.8.8',
				'8.8.4.4',
				'114.114.114.114'
			]
		},
		'routing': {
			'strategy': 'rules',
			'settings': {
				'domainStrategy': 'IPIfNonMatch',
				'rules': [
					{
						'type': 'field',
						'port': None,
						'outboundTag': 'direct',
						'ip': [
							'0.0.0.0/8',
							'10.0.0.0/8',
							'100.64.0.0/10',
							'127.0.0.0/8',
							'169.254.0.0/16',
							'172.16.0.0/12',
							'192.0.0.0/24',
							'192.0.2.0/24',
							'192.168.0.0/16',
							'198.18.0.0/15',
							'198.51.100.0/24',
							'203.0.113.0/24',
							'::1/128',
							'fc00::/7',
							'fe80::/10'
						],
						'domain': None
					}
				]
			}
		}
	}

	t_guiNConfig = \
		{
			"inbound": [{
				"localPort": 28080,
				"protocol": "socks",
				"udpEnabled": False
			}],
			"logEnabled": False,
			"loglevel": "error",
			"index": 78,
			"vmess": [],
			"muxEnabled": False,
			"chinasites": False,
			"chinaip": False,
			"useragent": [],
			"userdirect": [],
			"userblock": [],
			"kcpItem": {
				"mtu": 1350,
				"tti": 10,
				"uplinkCapacity": 20,
				"downlinkCapacity": 100,
				"congestion": True,
				"readBufferSize": 4,
				"writeBufferSize": 4
			},
			"autoSyncTime": False,
			"sysAgentEnabled": False,
			"listenerType": 1,
			"urlGFWList": ""
		}
	
	configs = []
	links = []
	guiNConfig = None
	data = None
	vmess = None

	if json_files:
		try:
			for i in json_files:
				if not os.path.isfile(i):
					print('****Bad file path or name: {} ...'.format(i))
					break
				else:
					with open(i, 'r', encoding='utf-8') as f:
						data = json.load(f)
					if not data:
						print('can not found specified format on {}'.format(i))
						break

				if isinstance(data, dict) and data.get('inbound') and data.get('vmess'):
					vmess = data.get('vmess')
					configs.extend(vmess)
					guiNConfig = data
				elif isinstance(data, list) and data[0].get('address'):
					configs.extend(data)
				else:
					print('can not found specified format on {}'.format(i))
		except:
			raise

	guiNConfig = t_guiNConfig if not guiNConfig else guiNConfig

	if configs:
		conf, _, deDup_info = deDup(configs)
	else:
		print('No legal data input...')
		sys.exit()

	print(deDup_info)
	try:
		input('**** Waiting for comfirm, Ctrl+C to interrupt or continue with Enter...')
	except KeyboardInterrupt:
		sys.exit()

	configs_good, configs_bad, _ = multi_proc(conf)

	kill()
	
	all_list = []
	if configs_good:
		all_list.extend(configs_good)
	if configs_bad:
		all_list.extend(configs_bad)
	if other_list:
		all_list.extend(other_list)

	if deDup_info:
		print(deDup_info)

	if only_test:
		print('**** Only test, result: deDuped records {}, good ones {}, bad ones {}.'.format(len(all_list), len(configs_good), len(configs_bad)))
	else:
		guiNConfig['vmess'] = all_list
		guiNConfig_new = 'guiNConfig_{}_.json'.format(time.strftime('%Y-%m-%d_%H-%M-%S'))
		with open(guiNConfig_new, 'w') as f:
			json.dump(guiNConfig, f)
			print('***** Output to {}, {} records. good ones {}, bad ones {}. *****'.format(guiNConfig_new, len(all_list), len(configs_good), len(configs_bad)))


if __name__ == '__main__':
	run_start = time.time()
	main()
	run_end = time.time()
	duration = run_end - run_start
	m, s = divmod(duration, 60)
	print('Cost time: {:.0f} mins {:.0f} seconds. '.format(m, s))
