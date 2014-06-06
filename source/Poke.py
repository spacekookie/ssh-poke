#!/usr/bin/python

'''

Copyright (c) 2014 Katharina Sabel <katharina.sabel@2rsoftworks.de>
Copyright (c) 2014 Random Robot Softworks
www.katharinasabel.de | www.2rsoftworks.de

Licensed under the Apache License, Version 2.0 (the "License");		
you may not use this file except in compliance with the License.		
You may obtain a copy of the License at	

		http://www.apache.org/licenses/LICENSE-2.0						
									
Unless required by applicable law or agreed to in writing, software	
distributed under the License is distributed on an "AS IS" BASIS,		
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Found a bug? Report it in the repository issue tracker:

		https://github.com/SpaceKookie/Poke

'''

from Controllers import SessionController
from Controllers import CallbackController
from IOHandle import Servers
from ConfigParser import ConfigParser
from optparse import OptionParser
from optparse import OptionGroup
from datetime import datetime
from os import path
from Intro import Setup
import Poke
import sys

# This is the main application file and entry point for the Poke commandline tool.
class Poke():

	# Self variables
	home = path.expanduser("~") # Change this to move Poke-location (not recomended)
	version = "0.3.2"
	workingDirectory = ".poke" # Change this to rename working directory
	access = 1 # if 0 root is required to write and/or read ssh/ servers

	def main(self):
		# Creates a starter object to init default values. If already set these will be read from config
		start = Setup(self.home, self.version, self.workingDirectory)
		start.make()

		# Future server to connect to!
		self.con = {}

		cb = CallbackController(self.home, self.workingDirectory)

		# Server config calls
		serverIO = Servers()
		self.serverCfg = ConfigParser()
		self.serverCfg.read(self.home + "/" + self.workingDirectory + "/servers.cfg")
		self.servers = self.serverCfg.sections() # Contains server sections

		# Key config calls
		# keyCfg = ConfigParser()
		# keyCfg.read(self.home + "/" + self.workingDirectory + "/keys.cfg")

		# Callbacks are handled automatically and need no further actions.
		parser = OptionParser(version=self.version)
		parser.remove_option("-h") # Remove default help from screen. TEMP WORKAROUND!

		parser.add_option("-H", action="callback", help="Display usage information about this application", callback=cb.helpMe)
		parser.add_option("-?", action="callback", help="Open 'Vi' to editor your config files!", callback=cb.runVi)

		administrative = OptionGroup(parser, "Overwrite Settings")
		administrative.add_option("-K", action="store", help="Overwrite stored key-setting for a server. Note: this is usually not very useful. Add the apropriate key to your keys.cfg file instead!", type="string", dest="SSH_KEY")
		administrative.add_option("-X", action="store_true", default=False, help="Overwrite XTerm settings for the ssh session", dest="xterm")
		parser.add_option_group(administrative)
		
		serverGroup = OptionGroup(parser, "Your servers")
		for server in self.servers:
			section = serverIO.getSectionMap(server, self.serverCfg)

			if 'name' in section:
				name = section['name']
			else:
				name = ""

			sHand = section['shorthand']

			if 'longhand' in section:
				lHand = section['longhand']
			else:
				lHand = ""
			url = section['url']
			user = section['user']

			if 'xdef' in section:
				xdef = "'True'"
			else:
				xdef = "'False'"

			if 'key' in section:
				key = section['key']
			else:
				key = None

			serverID = name + (":[%s@%s]" % (user, url))
			if key is not None:
				helpText = "Connect to %s with key '%s'. XTerm is %s by default" % (serverID, key, xdef)
			else:
				helpText = "Connect to %s. XTerm is %s by default" % (serverID, xdef)
			serverGroup.add_option("-%s" % sHand, "--%s" % lHand, action="callback", help=helpText, callback=self.update)

			# action="store", type="string", dest="filename" 

		parser.add_option_group(serverGroup)
		(self.prefs, self.args) = parser.parse_args()

		if len(sys.argv) == 1:
			print(parser.format_help())
			sys.exit()
		else:
			self.action()

	def action(self):
		# print self.prefs
		'''if self.prefs.xterm:
			self.useX = True
		if self.prefs.SSH_KEY:
			self.useKey = True
			self.key = self.prefs.SSH_KEY
			print(self.key)'''


	# Updates the global server stored in this class to connect to later!
	def update(self, option, opt_str, value, parser):
		t = str(option)
		handle = t[1:2]
		sCheck = Servers()

		for server in self.servers:
			section = sCheck.getSectionMap(server, self.serverCfg)
			if section['shorthand'] == handle:
				self.con['name'] = section['name']
				self.con['url'] = section['url']
				self.con['user'] = section['user']
				if 'key' in section:
					self.con['key'] = section['key']
				else:
					self.con['key'] = None

				if 'xdef' in section:
					if section['xdef'] == 'True':
						self.con['xdef'] = True
					else:
						self.con['xdef'] = False
				else:
					self.con['xdef'] = False

		print("###########")
		print(self.con)
		# call("ssh " + self.user + "@" + self.server, shell=True)


	# Starts the application
	if __name__ == "__main__":
		startTime = datetime.now()
		Poke.Poke().main()
		print(datetime.now()-startTime)