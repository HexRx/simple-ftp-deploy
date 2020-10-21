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

CONSOLE_PREFIX='[Simple FTP Deploy] '

REQUIRED_FIELDS=['host','username','password']

CONFIG_FILE_NAME='simple-ftp-deploy.json'

config = {}

FTP_sessions_cache=[]

def getSetting(name, defaultValue = None):
	if config and name in config:
		return config[name]
	else:
		return defaultValue

def cdRecursivelly(session, cdDir, prompt = True):
	if cdDir != "":
		try:
			session.cwd(cdDir)
		except ftplib.all_errors as e:
			if str(e).split(None, 1)[0]!="550":
				sublime.error_message(DIALOG_TITLE + 'Could not set current working dir to ' + cdDir + ':\n' + str(e))
				return False
			if prompt and not getSetting('autoCreateDirectory'):
				create = sublime.ok_cancel_dialog(DIALOG_TITLE + 'Directory  \'' + cdDir + '\' does not exists, do you want to create it?', 'Yes')
				if not create:
					return False
			cdRecursivelly(session, "/".join(cdDir.split("/")[:-1]), False)
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

	def checkSession(self):
		if not hasattr(self, 'session'):
			print(CONSOLE_PREFIX + 'WARNING: attempt to use session before \'connect()\', connecting')
			self.connect()

	def connect(self):
		start = time.time()

		fromCache = False
		# If cached, return from cache
		for cache in FTP_sessions_cache if getSetting("sessionCacheEnabled", True) else []:
			# Check if session expired
			if cache["timestamp"] + cache["timeout"] < time.time():
				# Delete old unused cache to free up memory
				del cache
			# Else check if entry equals to out needs
			elif cache["host"] == self.host and cache["port"] == self.port and cache["username"] == self.username and cache["password"] == self.password:
				self.session = cache["session"]
				cache["timestamp"] = time.time()
				end = time.time()
				self._connectTime = round((end - start)*1000)

				ctime = datetime.datetime.now().strftime('%X')
				msg = '[Connected {0}]: {1} ({2}ms; from cache)'.format(ctime, self.host + ":" + str(self.port), self._connectTime)
				print(CONSOLE_PREFIX + msg)
				sublime.status_message(msg)
				fromCache = True
				# Do not return yet, check for other expired connections to free up memory

		# Return if session set
		if fromCache:
			return
		# Not in cache, create new session
		self.session = ftplib.FTP(timeout=getSetting("connectionTimeout",600))
		try:
			self.session.connect(self.host, self.port)
		except ftplib.all_errors as e:
			sublime.error_message(DIALOG_TITLE + "Could not connect to " + self.host + ":" + str(self.port) + "\n" + str(e))
			return
		try:
			self.session.login(self.username, self.password)
		except ftplib.all_errors as e:
			sublime.error_message(DIALOG_TITLE + "Could not login to " + self.host + ":" + str(self.port) + "\n" + str(e))
			return
		end = time.time()
		self._connectTime = round((end - start)*1000)

		ctime = datetime.datetime.now().strftime('%X')
		msg = '[Connected {0}]: {1} ({2}ms)'.format(ctime, self.host + ":" + str(self.port), self._connectTime)
		print(CONSOLE_PREFIX + msg)
		sublime.status_message(msg)

		# Add session to cache
		if not getSetting("sessionCacheEnabled", True):
			return
		FTP_sessions_cache.append({
			"host": self.host,
			"port": self.port,
			"username": self.username,
			"password": self.password,
			"timestamp": time.time(),
			"timeout": getSetting("connectionTimeout", 600),
			"session": self.session
		})

	def parsePath(self, rootDir, fullPath):
		# Remove full path and remove \\
		localFilePath = os.path.dirname(fullPath).replace(rootDir, '')[1:]

		return os.path.join(self.ftpRootDir, localFilePath).replace('\\', '/'), os.path.basename(fullPath)

	def uploadTo(self, localRootDir, currentFullPath):
		self.checkSession()

		start = time.time()

		fullFtpPath, currentFileName = self.parsePath(localRootDir, currentFullPath)
		
		if fullFtpPath == '':
			fullFtpPath = '/'

		file = open(currentFullPath, 'rb')
		# Set ftp directory
		success = cdRecursivelly(self.session,fullFtpPath)
		if not success:
			sublime.error_message(DIALOG_TITLE + 'Could not set current working dir to \'' + fullFtpPath + '\'')
			return

		self.session.storbinary('STOR ' + currentFileName, file)

		file.close()

		end = time.time()
		ctime = datetime.datetime.now().strftime('%X')
		msg = '[Deployed {0}]: {1} ({2}ms)'.format(ctime, os.path.join(fullFtpPath, currentFileName).replace('\\', '/'), round((end - start)*1000))
		print(CONSOLE_PREFIX + msg)
		sublime.status_message(msg)

	def deleteFile(self, localRootDir, currentFullPath):
		self.checkSession()

		start = time.time()

		fullFtpPath, currentFileName = self.parsePath(localRootDir, currentFullPath)

		try:
			self.session.cwd(fullFtpPath)
		except ftplib.all_errors as e:
			sublime.error_message(DIALOG_TITLE + 'Could not delete file \'' + fullFtpPath + '/' + currentFileName + '\':\n' + str(e))

		try:
			self.session.delete(currentFileName)
		except ftplib.all_errors as e:
			sublime.error_message(DIALOG_TITLE + 'Could not delete file \'' + fullFtpPath + '/' + currentFileName + '\':\n' + str(e))
			return

		end = time.time()
		ctime = datetime.datetime.now().strftime('%X')
		msg = '[Deleted {0}]: {1} ({2}ms)'.format(ctime, os.path.join(fullFtpPath, currentFileName).replace('\\', '/'), round((end - start)*1000))
		print(CONSOLE_PREFIX + msg)
		sublime.status_message(msg)

# Save file event listener
class SaveEventListener(sublime_plugin.EventListener):
	def on_post_save_async(self, view):
		if view.window().project_data():
			for openFolder in view.window().folders():
				configFile = os.path.join(openFolder, CONFIG_FILE_NAME)
				# Ignore config file and check if file is in opened folder
				if os.path.basename(view.file_name()) != CONFIG_FILE_NAME and openFolder in view.file_name():
					# Deploy if exists config file in root folder
					if os.path.isfile(configFile):
						# Read the config
						with open(configFile) as data:
							global config
							try:
								config = json.load(data)
								for field in REQUIRED_FIELDS:
									if not field in config:
										raise Exception('Missing required field "{}"'.format(field))
							except Exception as e:
								sublime.error_message(DIALOG_TITLE + 'Could not load config file:\n' + str(e))
								return

							filename, extension = os.path.splitext(view.file_name())
							basename = os.path.basename(view.file_name())
							# Ignored filenames
							if basename in getSetting('ignoredFilenames', []):
								return
							# Ignored extensions
							if extension in getSetting('ignoredExtensions', []):
								return
							# Ignored folders
							for folder in getSetting('ignoredFolders', []):
								if folder in filename:
									return
							# Upload 
							ftp = Ftp(config['host'], getSetting('port', 21), config['username'], config['password'], getSetting('rootDirectory', ''))
							ftp.connect()
							ftp.uploadTo(openFolder, view.file_name())

# ==============
# Delete file and folder, new folder and rename handlers (in progress)
# To disable this feature, please set `enableDeleteHandler` setting to false in global settings
# WARNING: HIGHLY EXPERIMENTAL, OVERRIDES DEFAULT DELETE HANDLERS (imported from side_bar.py from Default.sublime-package)
# ==============
if sublime.load_settings("simple-ftp-deploy.sublime-settings").get("enableDeleteHandler", True):
	from Default.side_bar import *
	import functools

	DeleteFileCommand._original_run = DeleteFileCommand.run

	def _new_DeleteFileCommand_run(self, files):
		if len(files) == 1:
			message = "Delete file %s from FTP too?" % files[0]
		else:
			message = "Delete %d files from FTP too?" % len(files)

		deleteFromFTP = False
		if sublime.ok_cancel_dialog(message, "Delete") == True:
			deleteFromFTP = True

		for f in files:
			v = self.window.find_open_file(f)
			if v != None and not v.close():
				return

			# Delete from FTP, if user accepts
			if not deleteFromFTP:
				continue

			if self.window.project_data():
				for openFolder in self.window.folders():
					configFile = os.path.join(openFolder, CONFIG_FILE_NAME)
					# Ignore config file and check if file is in opened folder
					if os.path.basename(f) != CONFIG_FILE_NAME and openFolder in f:
						# Deploy if exists config file in root folder
						if os.path.isfile(configFile):
							# Read the config
							with open(configFile) as data:
								global config
								try:
									config = json.load(data)
									for field in REQUIRED_FIELDS:
										if not field in config:
											raise Exception('Missing required field "{}"'.format(field))
								except Exception as e:
									sublime.error_message(DIALOG_TITLE + 'Could not load config file:\n' + str(e))
									return

								filename, extension = os.path.splitext(f)
								basename = os.path.basename(f)
								# Ignored filenames
								if basename in getSetting('ignoredFilenames', []):
									return
								# Ignored extensions
								if extension in getSetting('ignoredExtensions', []):
									return
								# Ignored folders
								for folder in getSetting('ignoredFolders', []):
									if folder in filename:
										return
								# Delete
								ftp = Ftp(config['host'], getSetting('port', 21), config['username'], config['password'], getSetting('rootDirectory', ''))
								ftp.connect()
								ftp.deleteFile(openFolder, f)
		# Call original method
		DeleteFileCommand._original_run(self, files)

	DeleteFileCommand.run = _new_DeleteFileCommand_run

# Work in progress: rename and new folder handler
