#Author Pico Geyer

import time
import re

class SetupError(Exception): pass
class TestFailure(Exception): pass

required_hosts = ['e1', 'e2', 'e3', 'w1', 'w2', 'w3']

#Implementation of tests.
#Each test should clean up after itself so as not to affect the other tests

def block_east_west_port_1080(mn):
    print 'running east west test'
    failed = False
    east = ['e1', 'e2', 'e3']
    west = ['w1', 'w2', 'w3']
    for e in east:
        for w in west:
            ehost = mn.get(e)
            whost = mn.get(w)
            wIP = whost.IP()
            eIP = ehost.IP()
            print 'Starting server on {}:{}'.format(wIP, 1080)
            whost.sendCmd('python ../test-server.py {} 1080'.format(wIP), printPid=True)
            time.sleep(1)
            print 'Starting client ({}) connecting to {}:{}'.format(eIP, wIP, 1080)
            ehost.sendCmd('python ../test-client.py {} 1080'.format(wIP), printPid=True)
            time.sleep(1)
            whost.sendInt()
            ehost.sendInt()
            wdata = whost.monitor()
            edata = ehost.monitor()
            #A better way to indicate that we are no longer waiting for output?
            ehost.waiting =  whost.waiting = False
            #print 'wdata:', wdata
            m = re.search('received', edata)
            if m:
                failed = True
                print '!!! Connection established from client ({}) to server ({}:{})'.format(eIP, wIP, 1080)
            else:
                print 'edata:', edata
                print 'wdata:', wdata
                pass
            #print 'edata:', edata
    if failed:
        raise TestFailure('Connections passed through the firewall that were supposed to be blocked')
    
def check_hosts(mn):
    missing_host = False
    for r in required_hosts:
        try:
            mn.get(r)
        except KeyError:
            print 'Required host {} seems to be missing from the topology'.format(r)
            missing_host = True
    if missing_host:
        raise SetupError("Missing hosts") 

def run_tests(mn):
    #list of tests to run, edit as needed
    tests = [
            'block_east_west_port_1080'
            ]
    #first do a sanity check 
    check_hosts(mn)
    mn.pingAll()
    for t in tests:
        to = globals()[t]
        try:
            to(mn)
            print 'Test {} passed'.format(t)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print 'Test {} failed: {}'.format(t, str(e)) 
