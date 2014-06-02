#!/usr/bin/env python
# coding: utf-8
from pyzabbix import ZabbixAPI
import sys
from re import compile,IGNORECASE
reload(sys)
sys.setdefaultencoding("utf-8")
"""
Looks up a web scenario based on its name, and then create a web scenarios if it does not exits
"""

# The hostname at which the Zabbix web interface is available


def authentication(server_url,user,password):

  if server_url and user and password:
    ZABBIX_SERVER = server_url
    zapi = ZabbixAPI(ZABBIX_SERVER)
    try:
      # Login to the Zabbix API
      zapi.login(user,password)
      return zapi
    except Exception, e:
      print(e)
      sys.exit(1)
  else:
    print('Zabbix Server url , user and password are required, try use --help')
    sys.exit(1)


def create_web_scenario(self,name,url,group,url_name='Homepage',status='200'):
  request = ZabbixAPI.do_request(self, 'webcheck.get', params={ "filter": {"name": name}})
  if request['result']:
    print('Host "%s" already registered' % name)
    sys.exit(1)
  else:
    try:
      ZabbixAPI.do_request(self, 'webcheck.create',params={"name": name,"applicationid": '4761',"delay": '60',"retries": '3', "steps": [ { 'name': url_name, 'url': url,'status_codes': status, 'no': '1'} ] } )
      triggers = create_trigger(auth,name,url,group)
    except Exception, e:
      print(e)
      sys.exit(1)

def create_by_file(auth, group, filename):
  file_to_parse = open(filename,'r')
  
  for line in file_to_parse:
    values = line.split(',')
    try:
      name = values[0]
      url = values[1]
    except IndexError, e:
      print('Need at minimun 2 params Traceback %s:' % e)
      sys.exit(1)
    try:
      url_name = values[2]
    except IndexError:
      url_name = None
    if url_name:
      create_web_scenario(auth,name,url,group,url_name)
    else:
      create_web_scenario(auth,name,url,group)

def create_trigger(auth,name,url,group):
  triggers = auth.trigger.create(description=name,comments="O site abaixo não respondeu ao envio de solicitação HTTP (visitação ao site) no tempo de 120 segundos, este erro pode indicar que o site está offline ou está com instabilidade.\n%s" % url,expression='{%s:web.test.fail[%s].sum(120)}=1' % (group,name),priority=5)
  return triggers


if __name__ == '__main__':
  from optparse import OptionParser
  parser = OptionParser()
  parser.add_option("-z","--zabbix",dest="server_url",help='URL for Zabbix Server',metavar='ZABBIX_SERVER')
  parser.add_option('-n','--name',dest='name',help='Name of the Host',metavar='NAME')
  parser.add_option('-w','--url-name',dest='url_name',help='URL name',metavar='URL_NAME')
  parser.add_option('--url',dest='url',help='URL',metavar='URL')
  parser.add_option('-s','--status',dest='status',help='Status Code',metavar='STATUS_CODE')
  parser.add_option('-u','--user',dest='user',help='User for authentication',metavar='USER')
  parser.add_option('-p','--password',dest='password',help='Password for authentication',metavar='PASSWORD')
  parser.add_option('-f','--file',dest='filename',help='File with Name,URL',metavar='FILE')
  parser.add_option('-g','--group-name',dest='group',help='Host Group Name',metavar='GROUP')
  (options, args) = parser.parse_args()
  auth = authentication(options.server_url,options.user,options.password)
  if options.filename:
    create_by_file(auth, options.group, options.filename)
  else:
    if not options.group:
      print('Group must be required')
      sys.exit(1)
    if options.status:
      if options.url_name:
        web_scenario = create_web_scenario(auth, options.name,options.url,options.group, options.url_name,options.status)
      else:
        web_scenario = create_web_scenario(auth, options.name,None,options.url, options.group, options.status)
    else:
      if options.url_name:
        web_scenario = create_web_scenario(auth, options.name,options.url, options.group, options.url_name)
      else:
        web_scenario = create_web_scenario(auth, options.name,options.url, options.group)
