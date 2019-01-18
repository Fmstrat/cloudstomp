#!/usr/bin/env python3

import sys
import argparse
import time
import datetime
import os
import subprocess
import json
import re
import getpass
from pathlib import Path

userhome = str(Path.home())
cshome = os.path.join(userhome, ".cloudstomp")
plugindir = os.path.join(cshome, "plugins")
sshkey = os.path.join(cshome, "sshkey.pem")
sessiondir = os.path.join(cshome, "sessions")
aptupdateran = False

def showSession(session):
	print("")
	print(session["name"].title())
	print("-------------------------------------------")
	print(json.dumps(session, indent=4))
	print("-------------------------------------------")
	print("")

def getRegionName():
	regionlist = syscmd("aws configure list").split()
	nextitem = False
	for r in regionlist:
		if nextitem:
			code = r
			break
		if r == "region":
			nextitem = True
	if code == "us-east-1":
		return "US East (N. Virginia)"
	if code == "us-east-2":
		return "US East (Ohio)"
	if code == "us-west-1":
		return "US West (N. California)"
	if code == "us-west-2":
		return "US West (Oregon)"
	if code == "ca-central-1":
		return "Canada (Central)"
	if code == "eu-central-1":
		return "EU (Frankfurt)"
	if code == "eu-west-1":
		return "EU (Ireland)"
	if code == "eu-west-2":
		return "EU (London)"
	if code == "eu-west-3":
		return "EU (Paris)"
	if code == "eu-north-1":
		return "EU (Stockholm)"
	if code == "ap-northeast-1":
		return "Asia Pacific (Tokyo)"
	if code == "ap-northeast-2":
		return "Asia Pacific (Seoul)"
	if code == "ap-northeast-3":
		return "Asia Pacific (Osaka-Local)"
	if code == "ap-southeast-1":
		return "Asia Pacific (Singapore)"
	if code == "ap-southeast-2":
		return "Asia Pacific (Sydney)"
	if code == "ap-south-1":
		return "Asia Pacific (Mumbai)"
	if code == "sa-east-1":
		return "South America (São Paulo)"

def loadConfig(pluginname):
	global plugindir
	config = {}
	with open(os.path.join(plugindir, pluginname, "plugin.json")) as f:
		config = json.load(f)
	return config

def alphanum(str):
	return re.sub('[^0-9a-zA-Z]+', '_', str)

def awsjson(cmd):
	return json.loads(syscmd(cmd))

def syscmd(cmd):
	return os.popen("HOME="+cshome+";"+cmd).read()

def syscmdv(cmd):
	os.system("HOME="+cshome+";"+cmd)

def which(file):
	for path in os.environ["PATH"].split(os.pathsep):
		if os.path.exists(os.path.join(path, file)):
			return os.path.join(path, file)
	return None

def checkRequirement(executable, program, method):
	global aptupdateran
	if (which(executable) == None):
		installprog = getinput("text", program.upper() + " is required and not installed, would you like to install it?", ['y', 'n'], 'y', True);
		if installprog == 'y':
			if method == "apt":
				if not aptupdateran:
					syscmd("apt-get update")
					aptupdateran = True
				syscmdv("apt-get install -y "+program)
			else:
				syscmdv("pip install "+program)
		else:
			printD("Exiting.", 0)
			sys.exit(0)

def printD(string, indent):
    strindent = ""
    for x in range(0, indent):
        strindent = strindent + " "
    print("[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "]" + strindent + " " + string)

def getinput(qtype, message, responses, default, showresponses, helpfile=None):
	response = None
	displayresponses = []
	tmpresponses = []
	if responses:
		for i, v in enumerate(responses):
			tmpresponse = str(v)
			if showresponses:
				if default != None and tmpresponse.lower() == default.lower():
					displayresponses.append(tmpresponse.upper())
				else:
					displayresponses.append(tmpresponse.lower())
			tmpresponses.append(tmpresponse.lower())
	options = " "
	if showresponses:
		if responses:
			options += "["
			for o in displayresponses:
				options += o+"/"
			options = options[:-1]
			options += "]"
		else:
			options += "["+str(default)+"]"
	if helpfile:
		options += "(?=Help)"
	if options != " ":
		options += ": "
	while True:
		myinput = ""
		if qtype == "password":
			myinput = getpass.getpass(message + options)
		else:
			myinput = input(message + options)
		if qtype != "file":
			if myinput == "" and default != None:
				response = str(default).lower()
				break
			elif responses and myinput.lower() not in tmpresponses or (myinput == "" and default == None):
				if helpfile and myinput == '?':
					syscmdv("cat '"+helpfile+"' | column -ts '|' |less -S")
				else:
					print("  Sorry, that is not a valid input.")
			else:
				response = myinput.lower()
				break
		else:
			if os.path.isfile(myinput):
				response = myinput
				break
			else:
				print("  Sorry, that is not a valid file.")
	return response

def isint(input):
	try:
		num = int(input)
	except ValueError:
		return False
	return True

def selectSession(showextra, withext):
	global sessiondir
	print("")
	sessions = []
	session = None
	with os.scandir(sessiondir) as it:
		for entry in it:
			if not entry.name.startswith('.') and entry.is_file():
				sessions.append(entry.name)
	running = awsjson('aws ec2 describe-instances --filter "Name=tag:Name,Values=Cloudstomp - *" "Name=instance-state-name,Values=pending,running,shutting-down,stopping,stopped"')
	responses = []
	print("Sessions:")
	print("-------------------------------------------")
	for idx, val in enumerate(sessions):
		status = ""
		if len(running["Reservations"]) > 0:
			for r in running["Reservations"]:
				if len(r["Instances"]) > 0:
					for i in r["Instances"]:
						if i["Tags"] and i["State"]["Name"] != "terminated":
							for t in i["Tags"]:
								if t["Key"] == "Name":
									if t["Value"].lower() == "cloudstomp - "+val.replace('.json', '').lower():
										status = "\t["+i["State"]["Name"]+"]"
		print(" " + str(idx+1) + ") " + val.replace('.json', '').title()+status)
		responses.append(idx+1)
	if showextra:
		print(" c) Create")
		responses.append('c')
		print(" q) Quit")
		responses.append('q')
	print("-------------------------------------------")
	sessindex = getinput("text", "Select session:", responses, None, False)
	if isint(sessindex):
		if withext:
			return sessions[int(sessindex)-1]
		else:
			return sessions[int(sessindex)-1].replace('.json', '')
	else:
		return sessindex.lower()

def selectPlugin():
	global plugindir
	plugins = []
	plugin = None
	with os.scandir(plugindir) as it:
		for entry in it:
			if not entry.name.startswith('.') and entry.is_dir():
				plugins.append(entry.name)
	responses = []
	print("Plugins:")
	print("-------------------------------------------")
	for idx, val in enumerate(plugins):
		print(" " + str(idx+1) + ") " + val.title())
		responses.append(idx+1)
	print("-------------------------------------------")
	plugindex = int(getinput("text", "Please select a plugin:", responses, None, False))
	return plugins[plugindex-1]

def getVPC():
	printD("Checking VPC...", 0)
	response = awsjson("aws ec2 describe-vpcs")
	result = None
	for item in response["Vpcs"]:
		if item["State"] == "available":
			result = item["VpcId"]
			break
	if not result:
		printD("No available VPCs exist.", 2)
		sys.exit(0)
	printD("Using VPC "+result+".", 2)
	return result

def getAvailabilityZones(instance):
	printD("Checking availability zones for "+instance+"...", 0)
	today = datetime.datetime.utcnow()
	todaystr = today.strftime("%Y-%m-%d T00:00:00")
	pricing = awsjson('aws ec2 describe-spot-price-history --start-time "'+todaystr+'" --product "Linux/UNIX (Amazon VPC)" --instance-type "'+instance+'"')
	zones = []
	for p in pricing["SpotPriceHistory"]:
		if p["AvailabilityZone"] not in zones:
			zones.append(p["AvailabilityZone"])
	return zones

def getSubnet(availabilityzones):
	printD("Getting subnet...", 0)
	response = awsjson("aws ec2 describe-subnets")
	result = None
	for item in response["Subnets"]:
		if item["State"] == "available":
			if len(availabilityzones) == 0 or item["AvailabilityZone"] in availabilityzones:
				result = item["SubnetId"]
				break
	if not result:
		printD("No available subnets exist.", 2)
		sys.exit(0)
	printD("Using subnet "+result+".", 2)
	return result

def getSecurityGroup(config, vpcid):
	printD("Checking security group...", 0)
	response = awsjson("aws ec2 describe-security-groups")
	result = None
	for item in response["SecurityGroups"]:
		if item["GroupName"] == "Cloudstomp - "+config["firewall"]["securitygroup"].title():
			printD("Found existing security group.", 2)
			result = item["GroupId"]
			break
	if not result:
		printD("Creating new security group.", 2)
		response = awsjson("aws ec2 create-security-group --group-name 'Cloudstomp - "+config["firewall"]["securitygroup"].title()+"' --description 'Created by cloudstomp' --vpc-id "+vpcid)
		result = response["GroupId"]
		printD("Adding rules...", 2)
		for port in config["firewall"]["ports"]:
			syscmdv("aws ec2 authorize-security-group-ingress --group-id "+result+" --protocol "+port["protocol"]+" --port "+str(port["port"])+" --cidr 0.0.0.0/0")
			printD("Added port "+str(port["port"])+".", 4)
	printD("Using security group "+result+".", 2)
	return result

def checkSSHKey():
	if not os.path.isfile(sshkey):
		printD("No SSH key found locally, checking on AWS...", 0)
		response = awsjson("aws ec2 describe-key-pairs")
		for item in response["KeyPairs"]:
			if item["KeyName"] == "Cloudstomp":
				printD("The cloudstomp SSH key already exists.", 2)
				deletekey = getinput("text", "  Would you like to remove the existing key pair from AWS?", ['y', 'n'], 'n', True)
				if deletekey == 'n':
					printD("The cloudstomp SSH key must be deleted from AWS or the existing private key copied to "+sshkey+" to continue.", 2)
					sys.exit(0)
				else:
					syscmdv("aws ec2 delete-key-pair --key-name Cloudstomp")
				break
		printD("Creating new key pair...", 2)
		syscmdv("aws ec2 create-key-pair --key-name Cloudstomp --query 'KeyMaterial' --output text > "+sshkey)
		syscmdv("chmod 400 "+sshkey)

def checkSSH(user, publicip):
	global sshkey
	cmd = 'ssh -o "StrictHostKeyChecking no" -o ConnectTimeout=3 -i "'+sshkey+'" -q '+user+'@'+publicip+' "exit";echo -n $?'
	printD("Checking for SSH connectivity...", 0)
	result = syscmd(cmd)
	while result != "0":
		printD("Waiting for SSH to start, sleeping 15s...", 2)
		time.sleep(15)
		result = syscmd(cmd)

def ssh(user, publicip, exec, visible, terminal):
	global sshkey
	terminalstr = ""
	if terminal:
		terminalstr = "-t"
	cmd = 'ssh '+terminalstr+' -o "StrictHostKeyChecking no" -i "'+sshkey+'" '+user+'@'+publicip+' "'+exec+'"'
	result = None
	if visible:
		syscmdv(cmd)
	else:
		result = syscmd(cmd)
	return result

def scp(user, publicip, src, dest, recursive, visible):
	global sshkey
	r = ""
	if recursive:
		r = "-r"
	cmd = 'scp '+r+' -o "StrictHostKeyChecking no" -i "'+sshkey+'" '+src.replace(" ", "\\ ")+' '+user+'@'+publicip+':'+dest.replace(" ", "\\ ")
	result = None
	if visible:
		syscmdv(cmd)
	else:
		result = syscmd(cmd)
	return result

def build(plugin):
	global plugindir
	global sshkey
	global sessiondir
	print("")
	response = awsjson("aws ec2 describe-images --owners self --filters 'Name=name,Values=Cloudstomp - "+plugin.title()+"'")
	if len(response["Images"]) > 0:
		printD("The AMI for "+plugin+" has already been created. Exiting.", 0)
		sys.exit(0)
	config = loadConfig(plugin)
	printD("Build will take place on a " + config["build"]["instance"] + " instance.", 0)
	availabilityzones = getAvailabilityZones(config["build"]["instance"])
	subnetid = getSubnet(availabilityzones)
	vpcid = getVPC()
	groupid = getSecurityGroup(config, vpcid)
	instance = awsjson("aws ec2 run-instances --block-device-mapping 'DeviceName=/dev/sda1,Ebs={VolumeSize="+config["build"]["diskgb"]+"}' --image-id "+config["build"]["ami"]+" --count 1 --instance-type "+config["build"]["instance"]+" --key-name 'Cloudstomp' --security-group-ids "+groupid+" --subnet-id "+subnetid)
	instanceid = instance["Instances"][0]["InstanceId"]
	printD("Instance "+instanceid+" started.", 0)
	printD("Waiting for boot to complete...", 0)
	state = 'pending'
	while state != "running":
		printD("Instance in "+state+" state, sleeping 15s...", 2)
		time.sleep(15)
		instance = awsjson("aws ec2 describe-instances --instance-ids "+instanceid)
		state = instance["Reservations"][0]["Instances"][0]["State"]["Name"]
	printD("Instance in "+state+" state.", 2)
	publicip = instance["Reservations"][0]["Instances"][0]["NetworkInterfaces"][0]["PrivateIpAddresses"][0]["Association"]["PublicIp"]
	printD("Instance has public IP of "+publicip+".", 0)
	user = config["build"]["user"]
	checkSSH(user, publicip)
	printD("Starting build scripts...", 0)
	l = len(config["build"]["scripts"])
	for i, script in enumerate(config["build"]["scripts"]):
		printD("Running "+script+"...", 2)
		scp(user, publicip, os.path.join(plugindir, plugin, script), "~/"+script, False, False)
		printD("Uploaded.", 4)
		ssh(user, publicip, 'chmod +x ~/'+script, False, False)
		ssh(user, publicip, '~/'+script, True, False)
		if l-1 > i:
			printD("Rebooting before next script...", 2)
			syscmd("aws ec2 reboot-instances --instance-ids "+instanceid)
			state = 'pending'
			while state != "running":
				printD("Instance in "+state+" state, sleeping 15s...", 2)
				time.sleep(15)
				instance = awsjson("aws ec2 describe-instances --instance-ids "+instanceid)
				state = instance["Reservations"][0]["Instances"][0]["State"]["Name"]
				printD("Instance in "+state+" state.", 2)
				checkSSH(user, publicip)
			time.sleep(15)
	printD("Stopping instance...", 0)
	awsjson("aws ec2 stop-instances --instance-ids "+instanceid)
	state = 'stopping'
	while state != "stopped":
		printD("Instance in "+state+" state, sleeping 15s...", 2)
		time.sleep(15)
		instance = awsjson("aws ec2 describe-instances --instance-ids "+instanceid)
		state = instance["Reservations"][0]["Instances"][0]["State"]["Name"]
	time.sleep(5)
	printD("Creating AMI image...", 0)
	awsjson("aws ec2 create-image --name 'Cloudstomp - "+plugin.title()+"' --instance-id "+instanceid)
	state = 'pending'
	response = None
	while state != "available":
		printD("Build is in "+state+" state, sleeping 15s...", 2)
		time.sleep(15)
		response = awsjson("aws ec2 describe-images --owners self --filters 'Name=name,Values=Cloudstomp - "+plugin.title()+"'")
		state = response["Images"][0]["State"]
	time.sleep(5)
	printD("Tagging with build version...", 0)
	amiid = response["Images"][0]["ImageId"]
	syscmd('aws ec2 create-tags --resources '+amiid+' --tags Key=Version,Value='+str(config["build"]["version"]))
	printD("Terminating source image...", 0)
	awsjson("aws ec2 terminate-instances --instance-ids "+instanceid)
	printD("Build complete.", 0)

def selectInstance(instances):
	responses = []
	print("Instances:")
	print("-------------------------------------------")
	for idx, val in enumerate(instances):
		print(" " + str(idx+1) + ") " + val["description"] + "\t[" + val["instance"] + "]")
		responses.append(idx+1)
	print("-------------------------------------------")
	index = int(getinput("text", "Please select an instance:", responses, None, False))
	instance = instances[index-1]["instance"]
	return instance

def create(plugin):
	global sshkey
	global plugindir
	global sessiondir
	print("")
	config = loadConfig(plugin)
	response = awsjson("aws ec2 describe-images --owners self --filters 'Name=name,Values=Cloudstomp - "+plugin.title()+"'")
	if len(response["Images"]) == 0:
		print("The AMI for "+plugin+" needs to be built.")
		buildami = getinput("text", "Would you like to build it now?", ['y', 'n'], 'y', True)
		if buildami== 'n':
			print("A build is required to continue.")
			sys.exit(0)
		else:
			build(plugin)
			print("")
			print("Returning to session creation.")
			print("")
	else:
		version = 0
		for tag in response["Images"][0]["Tags"]:
			if tag["Key"] == "Version":
				version = int(tag["Value"])
				break	
		if version != config["build"]["version"]:
			printD("The AMI for "+plugin+" is an old version and needs to be rebuilt. Exiting.", 0)
			sys.exit(0)
	session = {}
	session["plugin"] = plugin
	instancetype = getinput("text", "Would you like to run the instance On-Demand or as a Spot Instance?", { 'o', 's' }, 's', True)
	session["instancetype"] = instancetype
	instance = None
	if instancetype == 'o':
		if len(config["instances"]) == 1:
			instance = config["instances"][0]["instance"]
		else:
			instance = selectInstance(config["instances"])
		session["instance"] = instance
	else:
		responses = []
		spotinstances = []
		for i in config["instances"]:
			if i["spot"]:
				spotinstances.append(i)
		instance = selectInstance(spotinstances)
		session["instance"] = instance
		today = datetime.datetime.utcnow()
		twoweeks = today - datetime.timedelta(days=14)
		twoweekstr = twoweeks.strftime("%Y-%m-%d T00:00:00")
		pricing = awsjson('aws ec2 describe-spot-price-history --start-time "'+twoweekstr+'" --product "Linux/UNIX (Amazon VPC)" --instance-type "'+instance+'"')
		zones = []
		for p in pricing["SpotPriceHistory"]:
			if p["AvailabilityZone"] not in zones:
				zones.append(p["AvailabilityZone"])
		if len(zones) == 0:
			printD("This instance does not exist in any availability zones in the region you have selected.", 0)
			sys.exit(0)
		prices = []
		for z in zones:
			count = 0
			total = 0.0
			latest = 0.0
			for p in pricing["SpotPriceHistory"]:
				if p["AvailabilityZone"] == z:
					if count == 0:
						latest = float(p["SpotPrice"])
					count = count + 1
					total = total + float(p["SpotPrice"])
			average = round(total/count, 6)
			default = round(average*1.15, 6)
			prices.append({ "zone": z, "latest": latest, "average": average, "default": default })
		ondemandA = awsjson('aws pricing get-products --service-code AmazonEC2 --filters "Type=TERM_MATCH,Field=instanceType,Value='+instance+'" "Type=TERM_MATCH,Field=operatingSystem,Value=Linux" "Type=TERM_MATCH,Field=capacitystatus,Value=UnusedCapacityReservation" "Type=TERM_MATCH,Field=preInstalledSw,Value=NA" "Type=TERM_MATCH,Field=location,Value='+getRegionName()+'"')
		ondemandB = json.loads(ondemandA["PriceList"][0])
		ondemandC = ondemandB["terms"]["OnDemand"]
		ondemandD = ondemandC[list(ondemandC.keys())[0]]["priceDimensions"]
		ondemand = float(ondemandD[list(ondemandD.keys())[0]]["pricePerUnit"]["USD"])
		print("")
		print("Pricing:")
		print("--------------\t----------\t----------\t----------\t------------")
		print("Zone\t\tAverage\t\tLatest\t\tOn Demand\tReccomended")
		print("--------------\t----------\t----------\t----------\t------------")
		lowest = 9999999.99
		lowestindex = -1
		lowestzone = ''
		for i, v in enumerate(prices):
			if v["default"] < lowest:
				lowest = v["default"]
				lowestindex = i
				lowestzone = v["zone"]
		responses = []
		for i, v in enumerate(prices):
			star = ""
			if i == lowestindex:
				star = " (best)"
			print(str(i+1)+') '+v["zone"]+'\t$'+str('{0:.6f}'.format(v["average"]))+'\t$'+str('{0:.6f}'.format(v["latest"]))+'\t$'+str('{0:.6f}'.format(ondemand))+'\t$'+str('{0:.6f}'.format(v["default"]))+star)
			responses.append(i+1)
		print("--------------\t----------\t----------\t----------\t------------")
		print("(The default is 15% over the average past two week spot price to keep your instance active.)")
		print("")
		response = int(getinput("text", "Which zone would you like to run in?", responses, lowestindex+1, False))
		zone = zones[response-1]
		defaultprice = 0.0
		for p in prices:
			if p["zone"] == zone:
				defaultprice = p["default"]
		maxprice = getinput("float", "What is the max price you would pay for a spot instance?", None, defaultprice, True)
		session["zone"] = zone
		session["maxprice"] = maxprice
	sessionexists = True
	while sessionexists:
		name = getinput("text", "What would you like to call this instance?", None, None, False)
		if os.path.isfile(os.path.join(sessiondir, name+".json")):
			printD("Session already exists.", 2)
		else:
			sessionexists = False
			session["name"] = name
	session["inputs"] = []
	for question in config["inputs"]:
		ask = True
		if question["depends"]:
			for d in question["depends"]:
				found = False
				for a in session["inputs"]:
					if d["variable"] == a["variable"]:
						found = True
						if d["value"] != a["value"]:
							ask = False
							break
				if not found:
					ask = False
				if not ask:
					break
		answer = {}
		if ask:
			helpfile = None
			if question["helpfile"]:
				helpfile = os.path.join(plugindir, plugin, question["helpfile"])
			answer["variable"] = question["variable"]
			answer["questiontype"] = question["questiontype"]
			answer["value"] = getinput(question["questiontype"], question["question"], question["responses"], question["default"], question["showresponses"], helpfile)
		else:
			answer["variable"] = question["variable"]
			answer["questiontype"] = question["questiontype"]
			answer["value"] = None
		session["inputs"].append(answer)
	with open(os.path.join(sessiondir, session["name"]+".json"), 'w') as f:
		f.write(json.dumps(session))
	print("Session "+session["name"].title()+" created.")

def main():
	global sshkey
	global sessiondir
	response = None
	while response != "q":
		response = selectSession(True, True)
		if response != 'q':
			if response == 'c':
				print("")
				print("Creating a new session.")
				plugin = selectPlugin()
				create(plugin)
			else:
				showMenu(response)

def showMenu(response):
	global sessiondir
	session = {}
	with open(os.path.join(sessiondir, response)) as f:
		session = json.load(f)
	index = ''
	while index.lower() != 'b':
		running = awsjson('aws ec2 describe-instances --filter "Name=tag:Name,Values=Cloudstomp - '+session["name"].title()+'" "Name=instance-state-name,Values=pending,running,shutting-down,stopping,stopped"')
		responses = []
		config = loadConfig(session["plugin"])
		print("")
		print(session["name"].title()+":")
		print("-------------------------------------------")
		state = "inactive"
		if len(running["Reservations"]) != 0:
			state = running["Reservations"][0]["Instances"][0]["State"]["Name"]
		count = 1
		commands = []
		for command in config["remote"]["commands"]:
			if command["display"] == "always" or command["display"] == state:
				print(" "+str(count)+") "+command["command"].title())
				responses.append(str(count))
				commands.append({ "command": command["command"], "terminal": command["terminal"], "type": "remote", "display": command["display"] })
				count = count+1
		for command in config["local"]["commands"]:
			if command["display"] == "always" or command["display"] == state:
				print(" "+str(count)+") "+command["command"].title())
				responses.append(str(count))
				commands.append({ "command": command["command"], "type": "local" })
		print(" s) Show variables")
		responses.append('s')
		print(" d) Delete")
		responses.append('d')
		print(" b) Back")
		responses.append('b')
		print("-------------------------------------------")
		index = getinput("text", "Choose an option:", responses, None, False)
		if index.lower() == 'd':
			confirm = getinput("text", "Are you sure?", ['y', 'n'], 'n', True)
			if confirm == 'y':
				os.remove(os.path.join(sessiondir, response))
				index = 'b'
		elif index.lower() == 's':
			showSession(session)
		elif index.lower() == 'b':
			index = 'b'
		else:
			if commands[int(index)-1]["type"] == "remote":
				if commands[int(index)-1]["display"] != "inactive":
					remote(session, commands[int(index)-1]["command"], commands[int(index)-1]["terminal"])
					if commands[int(index)-1]["command"] == "stop":
						index = 'b'
				else:
					run(session, commands[int(index)-1]["command"])
			else:
				local(session, commands[int(index)-1]["command"])

def local(session, command):
	global plugindir
	config = loadConfig(session["plugin"])
	cmd = "SESSION='"+alphanum(session["name"].lower())+"' "
	for i in session["inputs"]:
		if i["value"]:
			cmd = cmd+i["variable"].upper()+"='"+i["value"]+"' "
	cmd = cmd+os.path.join(plugindir, config["name"], config["local"]["script"]).replace(' ','\\ ')
	cmd = cmd+" "+command
	print("")
	print("Result:")
	print("-------------------------------------------")
	syscmdv(cmd)
	print("")
	print("-------------------------------------------")

def terminate(session):
	config = loadConfig(session["plugin"])
	response = awsjson("aws ec2 describe-instances --filters 'Name=tag:Name,Values=Cloudstomp - "+session["name"].title()+"' 'Name=instance-state-name,Values=pending,running,shutting-down,stopping,stopped'")
	instanceid = response["Reservations"][0]["Instances"][0]["InstanceId"]
	printD("Termintating instance "+instanceid, 0)
	syscmd("aws ec2 terminate-instances --instance-id "+instanceid)
	printD("Terminated, will be offline shortly.", 2)

def remote(session, command, terminal):
	config = loadConfig(session["plugin"])
	instance = awsjson("aws ec2 describe-instances --filters 'Name=tag:Name,Values=Cloudstomp - "+session["name"].title()+"' 'Name=instance-state-name,Values=running'")
	spotid = None
	if "SpotInstanceRequestId" in instance["Reservations"][0]["Instances"][0].keys():
		spotid = instance["Reservations"][0]["Instances"][0]["SpotInstanceRequestId"]
	publicip = instance["Reservations"][0]["Instances"][0]["NetworkInterfaces"][0]["PrivateIpAddresses"][0]["Association"]["PublicIp"]
	instanceid = instance["Reservations"][0]["Instances"][0]["InstanceId"]
	printD("Instance has public IP of "+publicip+".", 0)
	user = config["build"]["user"]
	checkSSH(user, publicip)
	cmd = "INSTANCEID='"+instanceid+"' "
	cmd = cmd + "SESSION='"+alphanum(session["name"].lower())+"' "
	if spotid:
		cmd = cmd + "SPOTID='"+spotid+"' "
	for i in session["inputs"]:
		if i["value"]:
			cmd = cmd+i["variable"].upper()+"='"+i["value"]+"' "
	cmd = cmd+'~/'+config["remote"]["script"]+' '+command
	ssh(user, publicip, cmd, True, terminal)

def run(session, command):
	global plugindir
	global sshkey
	global sessiondir
	print("")
	config = loadConfig(session["plugin"])
	amiid = None
	response = awsjson("aws ec2 describe-images --owners self --filters 'Name=name,Values=Cloudstomp - "+session["plugin"].title()+"'")
	if len(response["Images"]) == 0:
		print("The AMI for "+session["plugin"]+" needs to be built.")
		buildami = getinput("text", "Would you like to build it now?", ['y', 'n'], 'y', True)
		if buildami== 'n':
			print("A build is required to continue.")
			sys.exit(0)
		else:
			build(session["plugin"])
			response = awsjson("aws ec2 describe-images --owners self --filters 'Name=name,Values=Cloudstomp - "+session["plugin"].title()+"'")
			print("")
			print("Returning to session run.")
			print("")
	amiid = response["Images"][0]["ImageId"]
	version = 0
	for tag in response["Images"][0]["Tags"]:
		if tag["Key"] == "Version":
			version = int(tag["Value"])
			break	
	if version != config["build"]["version"]:
		printD("The AMI for "+session["plugin"]+" is an old version and needs to be rebuilt. Exiting.", 0)
		sys.exit(0)
	availabilityzones = []
	if session["instancetype"] == 'o':
		availabilityzones = getAvailabilityZones(session["instance"])
	else:
		availabilityzones = [ session["zone"] ]
	subnetid = getSubnet(availabilityzones)
	vpcid = getVPC()
	groupid = getSecurityGroup(config, vpcid)
	spotid = None
	instanceid = None
	instance = {}
	if session["instancetype"] == 'o':
		instance = awsjson("aws ec2 run-instances --image-id "+amiid+" --count 1 --instance-type "+session["instance"]+" --key-name 'Cloudstomp' --security-group-ids "+groupid+" --subnet-id "+subnetid)
		instanceid = instance["Instances"][0]["InstanceId"]
	else:
		spot = awsjson('aws ec2 request-spot-instances --spot-price '+session["maxprice"]+' --launch-specification '+"'"+'{ "KeyName": "Cloudstomp", "ImageId": "'+amiid+'", "InstanceType": "'+session["instance"]+'" , "Placement": {"AvailabilityZone": "'+session["zone"]+'"}, "SecurityGroupIds": ["'+groupid+'"], "SubnetId": "'+subnetid+'" }'+"'")
		spotid = spot["SpotInstanceRequests"][0]["SpotInstanceRequestId"]
		printD("Waiting on spot id "+spotid+"...", 0)
		while "InstanceId" not in spot["SpotInstanceRequests"][0].keys():
			printD("Spot request in "+spot["SpotInstanceRequests"][0]["State"]+" state, sleeping 15s...", 2)
			time.sleep(15)
			spot = awsjson("aws ec2 describe-spot-instance-requests --spot-instance-request-ids "+spotid)
		printD("Spot request in "+spot["SpotInstanceRequests"][0]["State"]+" state.", 2)
		instanceid = spot["SpotInstanceRequests"][0]["InstanceId"]
	printD("Instance "+instanceid+" started.", 0)
	printD("Waiting for boot to complete...", 0)
	state = 'pending'
	while state != "running":
		printD("Instance in "+state+" state, sleeping 15s...", 2)
		time.sleep(15)
		instance = awsjson("aws ec2 describe-instances --instance-ids "+instanceid)
		state = instance["Reservations"][0]["Instances"][0]["State"]["Name"]
	printD("Instance in "+state+" state.", 2)
	syscmd('aws ec2 create-tags --resources '+instanceid+' --tags "Key=Name,Value=Cloudstomp - '+session["name"].title()+'"')
	publicip = instance["Reservations"][0]["Instances"][0]["NetworkInterfaces"][0]["PrivateIpAddresses"][0]["Association"]["PublicIp"]
	printD("Instance has public IP of "+publicip+".", 0)
	user = config["build"]["user"]
	checkSSH(user, publicip)
	printD("Uploading cloudstomp AWS credentials...", 0)
	scp(user, publicip, "~/.aws", "~/.aws", True, False)
	printD("Uploading any supporting files...", 0)
	for i in session["inputs"]:
		if i["value"] and i["questiontype"] == "file":
			scp(user, publicip, i["value"], "~/"+os.path.basename(i["value"]), True, False)
			printD("Uploaded "+os.path.basename(i["value"])+".", 2)
	printD("Complete.", 2)
	printD("Starting init script...", 0)
	script = config["remote"]["script"]
	printD("Running "+script+"...", 2)
	scp(user, publicip, os.path.join(plugindir, session["plugin"], script), "~/"+script, False, False)
	printD("Uploaded.", 4)
	ssh(user, publicip, 'chmod +x ~/'+script, False, False)
	cmd = "INSTANCEID='"+instanceid+"' "
	cmd = cmd + "SESSION='"+alphanum(session["name"].lower())+"' "
	if spotid:
		cmd = cmd + "SPOTID='"+spotid+"' "
	for i in session["inputs"]:
		if i["value"]:
			if i["questiontype"] == "file":
				cmd = cmd+i["variable"].upper()+"='"+os.path.basename(i["value"])+"' "
			else:
				cmd = cmd+i["variable"].upper()+"='"+i["value"]+"' "
	cmd = cmd+'~/'+script+' '+command
	terminal = False
	for c in config["remote"]["commands"]:
		if c["command"] == command:
			terminal = c["terminal"]
			break
	print(cmd)
	ssh(user, publicip, cmd, True, terminal)
	printD("Launch complete.", 0)

def checkAWS():
	while True:
		output = str(syscmd("aws configure list"))
		if output.find("access_key                <not set>") >= 0 or output.find("secret_key                <not set>") >= 0 or output.find("region                <not set>") >= 0:
			configureaws = getinput("text", "AWS CLI is not configured, would you like to do this now?", ['y', 'n'], 'n', True)
			if configureaws == 'y':
				print("Access key, Secret key, and default region must all be configured.")
				syscmdv("aws configure")
			else:
				printD("AWS CLI must be configured to continue.", 0)
				sys.exit(0)
		else:
			break

def init():
	# Make paths
	global cshome
	global plugindir
	global sessiondir
	os.makedirs(cshome, exist_ok=True)
	os.makedirs(sessiondir, exist_ok=True)
	# Check requirements
	checkRequirement("pip", "python-pip", "apt")
	checkRequirement("git", "git", "apt")
	checkRequirement("ssh", "openssh-client", "apt")
	checkRequirement("gocryptfs", "gocryptfs", "apt")
	checkRequirement("aws", "awscli", "pip")
	if not args.update:
		# Check that AWS in configured
		checkAWS()
		# Check for SSH keys
		checkSSHKey()

def update():
	if os.path.isdir(plugindir):
		syscmdv("cd " + plugindir + "; git pull")
	else:
		syscmdv("cd " + cshome + "; git clone https://github.com/Fmstrat/cloudstomp-plugins.git plugins")

def listplugins():
	global plugindir
	plugins = []
	plugin = None
	with os.scandir(plugindir) as it:
		for entry in it:
			if not entry.name.startswith('.') and entry.is_dir():
				plugins.append(entry.name)
	responses = []
	print("Plugins:")
	print("-------------------------------------------")
	for idx, val in enumerate(plugins):
		print(" " + str(idx+1) + ") " + val.title())
		responses.append(idx+1)
	print("-------------------------------------------")

def listsessions():
	global sessiondir
	print("")
	sessions = []
	session = None
	with os.scandir(sessiondir) as it:
		for entry in it:
			if not entry.name.startswith('.') and entry.is_file():
				sessions.append(entry.name)
	running = awsjson('aws ec2 describe-instances --filter "Name=tag:Name,Values=Cloudstomp - *" "Name=instance-state-name,Values=pending,running,shutting-down,stopping,stopped"')
	responses = []
	print("Sessions:")
	print("-------------------------------------------")
	for idx, val in enumerate(sessions):
		status = ""
		if len(running["Reservations"]) > 0:
			for r in running["Reservations"]:
				if len(r["Instances"]) > 0:
					for i in r["Instances"]:
						if i["Tags"] and i["State"]["Name"] != "terminated":
							for t in i["Tags"]:
								if t["Key"] == "Name":
									if t["Value"].lower() == "cloudstomp - "+val.replace('.json', '').lower():
										status = "\t["+i["State"]["Name"]+"]"
		print(" " + str(idx+1) + ") " + val.replace('.json', '').title()+status)
		responses.append(idx+1)
	print("-------------------------------------------")

parser = argparse.ArgumentParser(
    description='CLI for running high CPU/GPU programs on EC2 instances.',
    formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=80, width=80))
parser.add_argument('-u', '--update', help='download and/or update plugins', default='', action='store_true')
parser.add_argument('-p', '--list-plugins', help='list available plugins', default='', action='store_true')
parser.add_argument('-b', '--build', help='build an AMI based on a plugin', default='', metavar='PLUGIN')
parser.add_argument('-c', '--create', help='create a new session to run your plugin on the AMI', default='', metavar='PLUGIN')
parser.add_argument('-l', '--list-sessions', help='list available sessions', default='', action='store_true')
parser.add_argument('-r', '--run', help='run a command for the given session', default='', metavar='COMMAND')
parser.add_argument('-s', '--session', help='the session to use with RUN', default='')
args = parser.parse_args()

# Check arguments
if len(sys.argv) == 1:
	init()
	main() 
else:
	count=0
	if args.build:
		count += 1
	if args.create:
		count += 1
	if args.run:
		count += 1
	if args.update:
		count += 1
	if args.list_sessions:
		count += 1
	if args.list_plugins:
		count += 1
	if count > 1:
		printD("Can only use one command at a time.", 0)
		print("")
		parser.print_help()
		sys.exit(0)
	if args.update:
		init()
		update()
	elif args.list_plugins:
		init()
		listplugins()
	elif args.build:
		init()
		build(args.build)
	elif args.create:
		init()
		create(args.create)
	elif args.list_sessions:
		init()
		listsessions()
	elif args.run:
		if not args.session or args.session == '':
			printD("A session is required for RUN.", 0)
			sys.exit(0)
		init()
		if not os.path.isfile(os.path.join(sessiondir, args.session.lower()+".json")):
			printD("No session named "+sessionname+". Exiting.", 0)
			sys.exit(0)
		session = {}
		with open(os.path.join(sessiondir, args.session.lower()+".json")) as f:
			session = json.load(f)
		run(session, args.run)

