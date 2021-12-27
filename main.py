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

import datetime
import ftplib
import json
import os
import sys
import time

REQUIRED_FIELDS = ['host', 'username', 'password']

CONFIG_FILE_NAME = 'simple-ftp-deploy.json'

FTP_SESSIONS = []

def ignored(path, config):
	filename, extension = os.path.splitext(path)

	# Ignored filenames
	if os.path.basename(path) in config.get('ignoredFilenames', []):
		return True

	# Ignored extensions
	elif extension in config.get('ignoredExtensions', []):
		return True

	# Ignored folders
	for folder in config.get('ignoredFolders', []):
		if folder in filename:
			return True

	return False

def trigger_match(path, trigger):
	filename, extension = os.path.splitext(path)

	# Filenames
	if 'filenames' in trigger and not os.path.basename(path) in trigger['filenames']:
		return False

	# Extensions
	if 'extensions' in trigger and not extension in trigger['extensions']:
		return False

	return True

def process_triggers(triggers, folder, filename, event, env = {}):
	env['folder'], env['filename'] = folder, filename

	for trigger in triggers:

		if not 'on' in trigger or not 'execute' in trigger:
			error('Missing required "on" and/or "file" option(s) in trigger configuration')
			continue

		if trigger['on'] == event and trigger_match(filename, trigger):
			try:
				env['__file__'] = os.path.join(folder, trigger['execute'])
				with open(env['__file__'], 'r') as file:
					try:
						exec(file.read(), env)
					except Exception as e:
						error('Error executing trigger:\n' + str(e))
			except Exception as e:
				error('Error loading trigger file:\n' + str(e))


def msg(message, *args):
	message = message.format(datetime.datetime.now().strftime('%X'), *args)
	print('[Simple FTP Deploy] ' + str(message))
	sublime.status_message(message)

def warning(message):
	print('[Simple FTP Deploy] [WARNING] ' + str(message))
	sublime.error_message('Simple FTP Deploy\n\n' + str(message))

def error(message):
	print('[Simple FTP Deploy] [ERROR] ' + str(message))
	sublime.error_message('Simple FTP Deploy\n\n' + str(message))

def ask(question, okLabel = 'Ok'):
	return sublime.ok_cancel_dialog('Simple FTP Deploy\n\n' + str(question), okLabel)

useFixedTLS = False
if sys.version_info.major >= 3 and sys.version_info.minor >= 6:
	useFixedTLS = True
	# https://stackoverflow.com/a/43301750
	class Fixed_FTP_TLS(ftplib.FTP_TLS):
		def ntransfercmd(self, cmd, rest=None):
			conn, size = ftplib.FTP.ntransfercmd(self, cmd, rest)
			if self._prot_p:
				conn = self.context.wrap_socket(conn, server_hostname=self.host, session=self.sock.session)
			return conn, size
else:
	unfixedTLS = 'You are using TLS mode, but there are some known issues with this mode in older versions of Python bundled with Sublime Text 3.\n\n\
In case something is not working correctly, either disable TLS mode or upgrade to Sublime Text 4.\n\n\
However if everything is working correctly, add following line to you configuration to hide this message.\n\n\
"noUnfixedTLSWarning": true'

class FTP(object):
	def __init__(self, config):
		self.config = config

		self.host = config.get('host')
		self.port = config.get('port', 21)
		self.username = config.get('username')
		self.password = config.get('password')
		self.rootDir = config.get('rootDirectory', '')
		self.timeout = config.get('connectionTimeout', 600)
		self.TLS = config.get('useTLS', False)

		self.reuseSessions = config.get('reuseSessions', config.get('sessionCacheEnabled', True))

	def checkSession(self):
		if not hasattr(self, 'session'):
			self.connect()

	# I think, there is easier way to do this...
	# CDs to given directory, creating directories if needed
	def cdRecursivelly(self, path, prompt = True, step = 1, splitPath = None):
		self.checkSession()

		if not splitPath:
			splitPath = path.split('/')

		directory = '/'.join(splitPath[:step])

		try:
			self.session.cwd(directory)
		except ftplib.all_errors as e:
			if str(e).split(None, 1)[0] != '550':
				error('Could not set current working directory to "' + directory + '"\n' + str(e))
				return False
			if prompt:
				if not ask('Directory "' + path + '" does not exists, do you want to create it?', 'Yes'):
					return False
				# Ask only once for whole directory structure creation
				prompt = False
			self.session.mkd(directory)
			self.session.cwd(directory)

		if step < len(splitPath):
			return self.cdRecursivelly(path, prompt, step + 1, splitPath)
		else:
			return True

	def connect(self):
		start = time.time()

		# If cached, return from cache
		if self.reuseSessions:
			global FTP_SESSIONS

			# Remove expired sessions
			FTP_SESSIONS = [session for session in FTP_SESSIONS if session['timestamp'] + session['timeout'] > time.time()]

			for session in FTP_SESSIONS:
				# Check if it is correct entry
				if session['host'] == self.host and session['port'] == self.port and session['username'] == self.username and session['password'] == self.password and session['TLS'] == self.TLS:
					self.session = session['session']

					# This assumes, that we will use this session, maybe needs some change
					session['timestamp'] = time.time()

					# As the session is ready to use, we are done
					return

		# Create new session
		if self.TLS:
			global useFixedTLS
			if useFixedTLS:
				self.session = Fixed_FTP_TLS(timeout = self.timeout)
			else:
				global unfixedTLS
				if unfixedTLS and not self.config.get('noUnfixedTLSWarning', False):
					warning(unfixedTLS)
					unfixedTLS = None
				self.session = ftplib.FTP_TLS(timeout = self.timeout)
		else:
			self.session = ftplib.FTP(timeout = self.timeout)

		# Set passive mode based on setting or default to true
		self.session.set_pasv(self.config.get('passive', True))

		# Try to connect
		try:
			self.session.connect(self.host, self.port)
		except ftplib.all_errors as e:
			error('Could not connect to ' + self.host + ':' + str(self.port) + '\n' + str(e))
			return

		# Secure with TLS
		if self.TLS:
			try:
				self.session.auth()
				self.session.prot_p()
			except ftplib.all_errors as e:
				error('Could not secure data connection\n' + str(e))
				return

		# Try to login
		try:
			self.session.login(self.username, self.password)
		except ftplib.all_errors as e:
			error('Could not login to ' + self.host + ':' + str(self.port) + '\n' + str(e))
			return

		end = time.time()

		msg('[Connected {0}]: {1}:{2} ({3}ms)', self.host, str(self.port), round((end - start) * 1000))

		# Add session to our session list (if not disabled in settings); sessionCacheEnable is for compatibility
		if self.config.get('reuseSessions', self.config.get('sessionCacheEnabled', True)):
			FTP_SESSIONS.append({
				'host': self.host,
				'port': self.port,
				'username': self.username,
				'password': self.password,
				'timestamp': time.time(),
				'timeout': self.timeout,
				'TLS': self.TLS,
				'session': self.session
			})

	def parsePath(self, rootDir, fullPath):
		# Remove full path and remove \
		localFilePath = os.path.dirname(fullPath).replace(rootDir, '')[1:]

		return os.path.join(self.rootDir, localFilePath).replace('\\', '/'), os.path.basename(fullPath)

	def exit(self, force = False):
		if force or (self.session and not self.config.get('reuseSessions', self.config.get('sessionCacheEnabled', True))):
			# Remove session
			for session in FTP_SESSIONS:
				if session.session == self.session:
					del session
			self.session.quit()

	def upload(self, localRootDir, currentFullPath):
		self.checkSession()

		start = time.time()

		fullFtpPath, currentFileName = self.parsePath(localRootDir, currentFullPath)

		if fullFtpPath == '':
			fullFtpPath = '/'

		# Set FTP directory recursively, so we ensure that directory exists
		prompt = not ('createDirectory' in self.config.get('noPromptEvents', []) or 'createFolder' in self.config.get('noPromptEvents', []))
		if not self.cdRecursivelly(fullFtpPath, prompt = prompt):
			error('Could not set working directory to "' + fullFtpPath + '"')
			return

		file = open(currentFullPath, 'rb')

		self.session.storbinary('STOR ' + currentFileName, file)

		file.close()

		# Go back to root, if we will reuse session
		if self.config.get('reuseSessions', self.config.get('sessionCacheEnabled', True)):
			self.session.cwd('/')

		end = time.time()

		msg('[Deployed {0}]: {1} ({2}ms)', os.path.join(fullFtpPath, currentFileName).replace('\\', '/'), round((end - start) * 1000))

	def delete(self, localRootDir, currentFullPath):
		self.checkSession()

		start = time.time()

		fullFtpPath, currentFileName = self.parsePath(localRootDir, currentFullPath)

		try:
			self.session.delete(fullFtpPath + '/' + currentFileName)
		except ftplib.all_errors as e:
			error('Could not delete "' + fullFtpPath + '/' + currentFileName + '"\n' + str(e))
			return

		end = time.time()

		msg('[Deleted {0}]: {1} ({2}ms)', os.path.join(fullFtpPath, currentFileName).replace('\\', '/'), round((end - start)*1000))

class Config():
	def __init__(self, configFileName):
		self.config = {}
		self.configFileName = configFileName
		file = open(configFileName)
		# Not sure, if this try expect is needed, but we need to throw exception in case of failure...
		try:
			self.config = json.load(file)
			for field in REQUIRED_FIELDS:
				if not field in self.config:
					raise Exception('Missing required field "{}"'.format(field))
		except Exception as e:
			file.close()
			raise e
		file.close()

	def save(self):
		with open(self.configFileName, 'w') as file:
			json.dump(self.config, file)

	def set(self, name, value):
		self.config[name] = value

	def get(self, name, defaultValue = None):
		return self.config[name] if self.config and name in self.config else defaultValue

# Save file event listener
class EventListener(sublime_plugin.EventListener):
	def on_post_save_async(self, view):
		window, filename = view.window(), view.file_name()
		if not window.project_data():
			return

		for folder in window.folders():
			configFile = os.path.join(folder, CONFIG_FILE_NAME)
			# Ignore config file, check if file is in opened folder and if config file exists in root folder
			if folder in filename and os.path.basename(filename) != CONFIG_FILE_NAME and os.path.isfile(configFile):
				# Read the config
				try:
					config = Config(configFile)
				except Exception as e:
					error('Could not load config file:\n' + str(e))
					return False

				if not ignored(filename, config):
					# Upload
					ftp = FTP(config)
					ftp.connect()
					ftp.upload(folder, filename)

					process_triggers(config.get('triggers', []), folder, filename, 'save', {'ftp': ftp, 'config': config, 'sublime': sublime, 'msg': msg, 'error': error, 'ask': ask})

					ftp.exit()

	def on_post_window_command(self, window, command, args):
		if not window.project_data():
			return

		if command == 'delete_file':
			for filename in args['files']:
				for folder in window.folders():
					configFile = os.path.join(folder, CONFIG_FILE_NAME)
					# Ignore config file, check if file is in opened folder and if config file exists in root folder
					if folder in filename and os.path.basename(filename) != CONFIG_FILE_NAME and os.path.isfile(configFile):
						try:
							config = Config(configFile)
						except Exception as e:
							error('Could not load config file:\n' + str(e))
							return False

						if 'deleteFile' in config.get('disabledEvents', []):
							continue

						if not 'deleteFile' in config.get('noPromptEvents', []) and not ask('Delete file %s from FTP too?' % filename, 'Delete'):
							break

						if not ignored(filename, config):
							# Delete
							ftp = FTP(config)
							ftp.connect()
							ftp.delete(folder, filename)

							process_triggers(config.get('triggers', []), folder, filename, 'delete', {'ftp': ftp, 'config': config, 'sublime': sublime, 'msg': msg, 'error': error, 'ask': ask})

							ftp.exit()

						break

		# TODO: command: delete_folder, args = {'dirs': ['/home/user/dir1', ...]}
		# TODO: command: new_folder, args = {'dirs': ['/home/user/dir1', ...]}
