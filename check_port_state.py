#!/usr/bin/env python
#
# Copyright (C) 2015 Cisco Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# The following script check if port are down and have description across different switches.
# If , then this script will shutdown the ports not to create errors in managment systems like HP NetworkNodeManager

import sys
import json
import requests
import ast
from string import Template

switch = [
          ['192.168.10.94', 'admin', 'TestMe']
         ]

my_headers = {'content-type': 'application/json-rpc'}

jsonrpc_template = Template("{'jsonrpc': '2.0', 'method': '$method', 'params': ['$params', 1], 'id': '$jrpc_id'}")


#conf_vlan_payload = 
def check_port_updown_description(row):
        ports = []
        switch_ip = row[0]
        username = row[1]
        password = row[2]

        payload = [{'jsonrpc': '2.0', 'method': 'cli', 'params': ['show interface',1], 'id': '1'}]
        my_data = json.dumps(payload)
        
        url = "http://"+switch_ip+"/ins"
        response = requests.post(url, data=my_data, headers=my_headers, auth=(username, password))

        #parse information of show interface status for ports without description and in down state  
        port_table = response.json()['result']['body']['TABLE_interface']['ROW_interface']
        print "following interfaces are down and have no description:"
        for port in port_table: 
           if 'desc' not in port and port['state'] == "down":
                print port['interface']
                ports.append(port['interface'])
        if ports:
                shutdown_ports(row,ports)
        else:
                print "nothing to do!!!"

def shutdown_ports(row, ports):   

    switch_ip = row[0]
    username = row[1]
    password = row[2]

    print "Configuring On Switch:  "+switch_ip+" the following ports  "+str(ports)

    url = "http://"+switch_ip+"/ins"
    
    batch_cmd = "["
    id_counter = 1
    
    command = "conf t"
    batch_cmd = batch_cmd + jsonrpc_template.substitute(params=command, jrpc_id=id_counter, method='cli')
    
    for port in ports:
        batch_cmd += ','
        command = 'interface ' + str(port)
        id_counter += 1
        batch_cmd = batch_cmd + jsonrpc_template.substitute(params=command, jrpc_id=id_counter, method='cli')
        batch_cmd += ','
        command = 'shutdown'
        id_counter += 1
        batch_cmd = batch_cmd + jsonrpc_template.substitute(params=command, jrpc_id=id_counter, method='cli')

    batch_cmd = batch_cmd + "]"
    #my_data = json.dumps(ast.literal_eval(batch_cmd))

    #response = requests.post(url, data=my_data, headers=my_headers, auth=(username, password))
    print (my_data)
                                              
def main():
    print "**** Calling port up/down checker ***" 
    for row in switch:    
        check_port_updown_description(row)

    print "*** port up/donw checker complete ***"
if __name__ == "__main__":
    main()