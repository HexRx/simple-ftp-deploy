"""
The MIT License (MIT)

Copyright (c) 2015 HexRx

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import sublime, sublime_plugin
import ftplib
import os
import datetime
import json
import time

DIALOG_TITLE='[Simple FTP Deploy]\n'

def cdRecursivelly(session, cdDir, config, prompt = True):
	if cdDir != "":
		try:
			session.cwd(cdDir)
		except ftplib.all_errors as e:
			if str(e).split(None, 1)[0]!="550":
				sublime.error_message(DIALOG_TITLE + 'Could not set current working dir to ' + cdDir + ':\n' + e)
				return False
			if prompt and not config['autoCreateDirectory'] if 'autoCreateDirectory' in config else True:
				create = sublime.ok_cancel_dialog(DIALOG_TITLE + 'Directory  \'' + cdDir + '\' does not exists, do you want to create it?', 'Yes')
				if not create:
					return False
			cdRecursivelly(session, "/".join(cdDir.split("/")[:-1]), config, False)
			session.mkd(cdDir)
			session.cwd(cdDir)
		return True

class Ftp(object):
	def __init__(self, host, port, username, password, ftpRootDir):
		self.host = host
		self.port = port
		self.username = username
		self.password = password
		self.ftpRootDir = ftpRootDir

	def uploadTo(self, localRootDir, currentFullPath, config):
		start = time.time()
		session = ftplib.FTP()
		try:
			session.connect(self.host, self.port)
		except ftplib.all_errors as e:
			sublime.error_message(DIALOG_TITLE + "Could not connect to " + self.host + ":" + str(self.port) + "\n" + str(e))
			return
		try:
			session.login(self.username, self.password)
		except ftplib.all_errors as e:
			sublime.error_message(DIALOG_TITLE + "Could not login to " + self.host + ":" + str(self.port) + "\n" + str(e))
			return

		currentPath = os.path.dirname(currentFullPath)
		# Remove full path and remove \\
		localFilePath = currentPath.replace(localRootDir, '')[1:]

		# Replace win path to unix path
		fullFtpPath = os.path.join(self.ftpRootDir, localFilePath).replace('\\', '/')

		file = open(currentFullPath, 'rb')
		# Set ftp directory
		success = cdRecursivelly(session,fullFtpPath,config)
		if not success:
			sublime.error_message(DIALOG_TITLE + 'Could not set current working dir to \'' + fullFtpPath + '\'')
			return

		currentFileName = os.path.basename(currentFullPath)
		session.storbinary('STOR ' + currentFileName, file)

		file.close()
		session.quit()

		end = time.time()
		ctime = datetime.datetime.now().strftime('%X')
		msg = '[Deployed {0}]: {1} ({2}ms)'.format(ctime, os.path.join(fullFtpPath, os.path.basename(currentFullPath)).replace('\\', '/'), round((end - start)*1000))
		print(msg)
		sublime.status_message(msg)

# Save file event listener
class SaveEventListener(sublime_plugin.EventListener):
	def on_post_save_async(self, view):
		if view.window().project_data():
			for openFolder in view.window().folders():
				configFileName = 'simple-ftp-deploy.json'
				configFile = os.path.join(openFolder, configFileName)
				# Ignore config file and check if file is in opened folder
				if os.path.basename(view.file_name()) != configFileName and openFolder in view.file_name():
					# Deploy if exists config file in root folder
					if os.path.isfile(configFile):
						# Read the config
						with open(configFile) as data:
							try:
								config = json.load(data)
							except Exception as e:
								sublime.error_message(DIALOG_TITLE + 'Could not load config file:\n' + str(e))
								return

							filename, extension = os.path.splitext(view.file_name())
							basename = os.path.basename(view.file_name())
							# Ignored filenames
							if basename in config['ignoredFilenames'] if 'ignoredFilenames' in config else False:
								return
							# Ignored extensions
							if extension in config['ignoredExtensions'] if 'ignoredExtensions' in config else False:
								return
							#Ignored folders
							for folder in config['ignoredFolders'] if 'ignoredFolders' in config else []:
								if folder in filename:
									return
							# Upload 
							ftp = Ftp(config['host'], config['port'] if 'port' in config else 21, config['username'], config['password'], config['rootDirectory'] if 'rootDirectory' in config else '')
							ftp.uploadTo(openFolder, view.file_name(), config)
