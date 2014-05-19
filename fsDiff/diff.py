# fsDiff Module
# For now, it just compares two configs (before and after)
# Change logic later for multiple sets

import sys
import argparse
import os
from collections import defaultdict
import difflib
import re
from datadiff import diff as di

class Compute:
    def __init__(self, key, wTD, switches):
	self.key = key
	self.wTD = wTD
	self.switches = switches
	self.Bps = {}
	self.Pps = {}
	self.Fps = {}
	self.sTime = {}
	self.fTime = {}
	self.pTime = {}
	self.ra = defaultdict(list)

    def getSwitches(self):
	return self.switches

    def getKey(self):
	return self.key

    def computeFlow(self):
	for switch in self.getSwitches():
	    fName = self.getKey()+"/"+switch+"_flow.txt"
	    bps = 0
	    pps = 0
	    fat = 0
	    fct = 0
	    fpt = 0
	    counter = 1
	    with open(fName, 'r') as fi:
		for f in fi:
		    line = f.strip()
		    sd,at,ct,byte,pkt = self.regexMatchFlow(line)
		    # Do we need to differentiate sd here?
		    pt = int(ct) - int(at)
		    bps += int(byte)
		    pps += int(pkt)
		    fat += int(at)
		    fct += int(ct)
		    fpt += pt
		    counter += 1

	    self.Bps[switch] = bps/counter
	    self.Pps[switch] = pps/counter
	    self.sTime[switch] = fat/counter
	    self.fTime[switch] = fct/counter
	    self.pTime[switch] = fpt/counter

    def computeCounter(self):
	for switch in self.getSwitches():
	    fName = self.getKey()+"/"+switch+"_counters.txt"
	    bps = 0
	    pps = 0
	    fps = 0
	    counter = 1
	    with open(fName, 'r') as fi:
		for f in fi:
		    line = f.strip()
		    sd,byte,pkt,flw = self.regexMatchCounter(line)
		    # Do we need to differentiate sd here?
		    bps += int(byte)
		    fps += int(flw)
		    pps += int(pkt)
		    counter += 1

	    self.Bps[switch] = bps/counter
	    self.Pps[switch] = pps/counter
	    self.Fps[switch] = fps/counter
    
    # Very crude - needs expansion
    def computeRule(self):
	for switch in self.getSwitches():
	    fName = self.getKey()+"/"+switch+"_rules.txt"
	    with open(fName, 'r') as fi:
		for f in fi:
		    sd = None
		    rule = None
		    line = f.strip()
		    try:
		        sd,rule = line.split('. Flow table match for flowlet ')
			tmpDict = self.getRA()
			if not any(value == rule for value in tmpDict[sd]):
			    self.ra[sd].append(rule)
		    except:
			continue

    def getRA(self):
	return self.ra

    def getBps(self):
	for k,v in self.Bps.iteritems():
	    print "{} - {}".format(k,v)

    def _getBps(self):
	return self.Bps

    def getPps(self):
	for k,v in self.Pps.iteritems():
	    print "{} - {}".format(k,v)
	
    def _getPps(self):
	return self.Pps

    def getFps(self):
	for k,v in self.Fps.iteritems():
	    print "{} - {}".format(k,v)

    def _getFps(self):
	return self.Fps
			 
    def getArrival(self):
	for k,v in self.sTime.iteritems():
	    print "{} - {}".format(k,v)

    def _getArrival(self):
	return self.sTime

    def getDeparture(self):
	for k,v in self.fTime.iteritems():
	    print "{} - {}".format(k,v)

    def _getDeparture(self):
	return self.fTime

    def getProcessing(self):
	for k,v in self.pTime.iteritems():
	    print "{} - {}".format(k,v)

    def _getProcessing(self):
	return self.pTime

    def regexMatchCounter(self, txt):
	re1='.*?((?:[a-z][a-z0-9_]*)).*?((?:[a-z][a-z0-9_]*)).*?(\\d+).*?(\\d+).*?(\\d+)'
	rg = re.compile(re1,re.IGNORECASE|re.DOTALL)
	m = rg.search(txt)
	if m:
    	    var1=m.group(1)
	    var2=m.group(2)
	    int1=m.group(3)
	    int2=m.group(4)
            int3=m.group(5)
	    return var1+"-"+var2,int1,int2,int3

    def regexMatchFlow(self, txt):
	re1='.*?\\d+.*?\\d+.*?(\\d+).*?\\d+.*?(\\d+).*?'
	re2='((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))(?![\\d])'
	re3='.*?(\\d+).*?'	
	re5='.*?(\\d+).*?\\d+.*?\\d+.*?\\d+.*?\\d+.*?\\d+.*?\\d+.*?(\\d+).*?(\\d+)'

	rg = re.compile(re1+re2+re3+re2+re5,re.IGNORECASE|re.DOTALL)
	m = rg.search(txt)
        if m:
    	    int1=m.group(1)
	    int2=m.group(2)
	    ip1=m.group(3)
	    int3=m.group(4)
	    ip2=m.group(5)
	    int4=m.group(6)
	    int5=m.group(7)
            int6=m.group(8)
	    return ip1+':'+int3+'-'+ip2+':'+int4,int1,int2,int6,int5 

# change this into a file -- report
# For now, just redirect outside

def report(line):
    print line

# Check number of switches for configurations
def switchSimilarity(L_1, L_2):
    L_1 = set(intern(w) for w in L_1)
    L_2 = set(intern(w) for w in L_2)
    c2 = L_1.difference(L_2)
    c1 = L_2.difference(L_1) 
    return list(c1), list(c2)

def processFiles(d, wTD):
    key1, value1 = d.popitem()
    key2, value2 = d.popitem()

    # Basic Comparison
    # L_1 and L_2 containts only switch names
    # L1_and_L2 containts common names
    # c1 contains config 2 (or not config 1)
    # c2 contains config 1 (or not config 2)
    # key1 contains config 1's location
    # key2 contains config 2's location
 
    report("========== Comparing Number of Switches ==========")
    L_1 = [i.split('_', 1)[0] for i in value1]
    L_2 = [i.split('_', 1)[0] for i in value2]

    if wTD=='all':
	L_1 = list(set(L_1))
	L_2 = list(set(L_2))

    L1_and_L2 = list(set(L_1) & set(L_2))

    c1, c2 = switchSimilarity(L_1, L_2)

    if L_1 == L_2:
	report("** Same Switches **")
    else:
	report("** Different Swiches **")
	if len(c1):
	    report("Configuration in {} has extra switches -- {}".format(key1,','.join(c1)))
	if len(c2):
	    report("Configuration in {} has extra switches -- {}".format(key2,','.join(c2)))

    # Deep comparison
    if wTD=='all' or wTD=='counter':
        report("\n========== Performance Comparison for counters ==========")
	C1 = Compute(key1, wTD, L_1)
	C1.computeCounter()
  	report("** Average Flows Per Second for {} **".format(key1))	
	C1.getFps()
  	report("** Average Bytes Per Second {} **".format(key1))	
	C1.getBps()
  	report("** Average Packets Per Second {} **".format(key1))	
	C1.getPps()

	C2 = Compute(key2, wTD, L_2)
	C2.computeCounter()
  	report("** Average Flows Per Second {} **".format(key2))	
	C2.getFps()
  	report("** Average Bytes Per Second {} **".format(key2))	
	C2.getBps()
  	report("** Average Packets Per Second {} **".format(key2))	
	C2.getPps()

	report("\nFlows per Second")
   	report(di(C1._getFps(), C2._getFps()))
	report("\nBytes per Second")
   	report(di(C1._getBps(), C2._getBps()))
	report("\nPackets per Second")
   	report(di(C1._getPps(), C2._getPps()))
	
    if wTD=='all' or wTD=='flowlet':
        report("\n========== Performance Comparison for flowlets ==========")
	C1 = Compute(key1, wTD, L_1)
	C1.computeFlow()
  	report("** Average Flow Arrival Time {} **".format(key1))	
	C1.getArrival()
  	report("** Average Flow Departure Time {} **".format(key1))	
	C1.getDeparture()
  	report("** Average Flow Processing Time {} **".format(key1))	
	C1.getProcessing()
  	report("** Average Bytes Per Second {} **".format(key1))	
	C1.getBps()
  	report("** Average Packets Per Second {} **".format(key1))	
	C1.getPps()

	C2 = Compute(key2, wTD, L_2)
	C2.computeFlow()
  	report("** Average Flow Arrival Time {} **".format(key2))	
	C2.getArrival()
  	report("** Average Flow Departure Time {} **".format(key2))	
	C2.getDeparture()
  	report("** Average Flow Processing Time {} **".format(key2))	
	C2.getProcessing()
  	report("** Average Bytes Per Second {} **".format(key2))	
	C2.getBps()
  	report("** Average Packets Per Second {} **".format(key2))	
	C2.getPps()

  	report("\nFlow Arrival Time")	
	report(di(C1._getArrival(), C2._getArrival()))
  	report("\nFlow Departure Time")	
	report(di(C1._getDeparture(), C2._getDeparture()))
  	report("\nFlow Processing Time")	
	report(di(C1._getProcessing(), C2._getProcessing()))
	report("\nBytes per Second")
   	report(di(C1._getBps(), C2._getBps()))
	report("\nPackets per Second")
   	report(di(C1._getPps(), C2._getPps()))

    if wTD=='all' or wTD=='rule':
        report("\n========== Comparison of Rules/Actions ==========")
    	C1 = Compute(key1, wTD, L_1)
	C1.computeRule()

	C2 = Compute(key2, wTD, L_2)
	C2.computeRule()

	D1 = C1.getRA()
	D2 = C2.getRA()

  	report("\nThe following rules are different in Config D1 (w.r.t. Config D2):")	
	for key in D1.keys():
	    try:
	        tV1 = D1[key]
	        tV2 = D2[key]
   	        if tV1 != tV2 and tV1 and tV2:
		    report("Flow: {}, Rule in D1: {}, Changed Rule in D2: {}".format(key, tV1, tV2))
	    except:
		if tV1 is None:
		    report("There is no rule in Config1 for flow {}, Changed Rule in D2: {}".format(key, tV2))
		if tV2 is None:
		    report("There is no rule in Config2 for flow {}, Changed Rule in D1: {}".format(key, tV1))
		    
  	report("\nThe following rules are different in Config D2 (w.r.t. Config D1):")	
	for key in D2.keys():
	    try:
	        tV1 = D1[key]
	        tV2 = D2[key]
   	        if tV1 != tV2 and tV1 and tV2:
		    report("Flow: {}, Rule in D2: {}, Changed Rule in D1: {}".format(key, tV2, tV1))
	    except:
		if tV1 is None:
		    report("There is no rule in Config1 for flow {}, Changed Rule in D2: {}".format(key, tV2))
		if tV2 is None:
		    report("There is no rule in Config2 for flow {}, Changed Rule in D1: {}".format(key, tV1))

def main(whatToDiff, folderList):
    d = defaultdict(list)    
    for fo in folderList:
	for fi in os.listdir(fo):
            if whatToDiff == "counter" and fi.endswith("_counters.txt"):
		d[fo].append(fi)
            if whatToDiff == "flowlet" and fi.endswith("_flow.txt"):
		d[fo].append(fi)
	    if whatToDiff == "rule" and fi.endswith("_rules.txt"):
		d[fo].append(fi)
            if whatToDiff == "all":
		d[fo].append(fi)

    if whatToDiff: 
	processFiles(d, whatToDiff)
    else:
	raise Exception("Require option!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--diff',
		      help="What to diff? 'flowlet', 'counter', 'rule' or 'all'",
		      dest="diff")
    parser.add_argument("-f", "--folder", nargs='+',
		      help="Trace folders",
		      dest="folders")
    arg = parser.parse_args()
	
    if arg.diff and arg.folders:
        folderList = arg.folders
	whatToDiff = str(arg.diff)
        main(whatToDiff, folderList)
