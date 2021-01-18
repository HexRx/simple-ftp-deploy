# Simple FTP Deploy
> This package for Sublime Text 3 give you possibility to auto upload file to FTP server when you save local file.

## Features
- Upload to FTP server on local file save
- Higly configurable
- Auto creates directory if doesn't exists on server and auto delete files on local file delete (configurable; **BETA** - Please report any issues. If any problem occured, you can disable delete handler patching by setting `"enableDeleteHandler"` option to false in global settings (`Preferences -> Package Settings -> Simple FTP Deploy -> Settings - User`) and restarting Sublime Text)

## How to Install

### Using [Package Control](https://packagecontrol.io)
1. In Sublime Text open menu `Tools -> Command Palette...`
2. Enter `Package Control: Install Package`
3. Find and install `Simple FTP Deploy`

### Manual
1. Download the [.zip](https://github.com/HexRx/simple-ftp-deploy/archive/master.zip)
2. Open `Packages` directory, which you can find using the Sublime Text menu item `Preferences -> Browse Packages...`
3. Unzip the archive to this directory.

## How to Use

1. Open folder which contains your local files in Sublime Text - open menu `File -> Open Folder...` or `Project -> Add Folder to Project...`.
2. Create new `simple-ftp-deploy.json` config file in the root of an opened directory (its settings see to configuration section)
3. Save the config file.
4. Now open file which you want to edit, it must be located in an opened directory or in the inside folders, if you save it, this file will be upload to FTP server which you entered in the config file.

## Configuration

Example `simple-ftp-deploy.json` file:
```json
{
    "host": "localhost",
    "username": "user",
    "password": "pass"
}
```

### Format
The format is [JSON](https://www.json.org), so every property consists of a key-value pair
```json
{
    "host": "localhost",
    "port": 21, 
    "username": "user",
    "password": "pass",
    "rootDirectory": "/path/",
    "autoCreateDirectory": false,
    "ignoredFilenames": ["example.py", "anotherFilename.json"],
    "ignoredExtensions": [".ignore", ".txt"],
    "ignoredFolders": ["ignore", "IGNORE"],
    "sessionCacheEnabled": true,
    "connectionTimeout": 600,
    "passive": true
}
```

### Properties

`"host"` *string*  
The hostname or IP address of your FTP server.

`"port"` *number, optional (default: `21`)*  
The port of the FTP server.

`"username"` *string*  
The username

`"password"` *string*  
The password

`"rootDirectory"` *string, optional (default: `"/"`)*  
The FTP path to deploy.  
**Example:** in the root of FTP you have three folders `site1`, `site2`, `site3` and if you need to upload in `site2` folder, you must set this property to `/site2`, because if you skip this property, files will be upload to the root of FTP

`"autoCreateDirectory"` *boolean, optional (default: `false`)*  
Whatever to automatically create a directory if doesn't exist and don't prompt user for acceptation.

`"ignoredFilenames"` *array, optional (default: `[]`)*  
List of filenames, that are ignored and not uploaded. Note that `"simple-ftp-deploy.json"` is ALWAYS ignored. **Case-sensitive**

`"ignoredExtensions"` *array, optional (default: `[]`)*  
List of extensions to ignore. Note that it only check last extension (so `file.tar.gz` has extension `".gz"`) and if you want to ignore files like `.htaccess`, this file has no extension => use `"ignoredFilenames"` instead. **Case-sensitive**

`"ignoredFolders"` *array, optional (default: `[]`)*  
List of folder names to ignore. The file is ingored, if it is in at least one of the specified folders (so `folder1/folder2/file.py` is ignored if `"ignoredFolders"` contains `"folder1"` and/or `"folder2"`). **Case-sensitive**

`"sessionCacheEnabled"` *boolean, optional (default: `true`)*  
Whatever FTP session caching is enabled (only for time specified in `"connectionTimeout"`, extends if session is used in that time)

`"connectionTimeout"` *number, optional (default: `600`)*  
Sets timeout for FTP connections and for cache lifetime (in seconds)

`"passive"` *boolean, optional (default: `true`)*
Whether to connect to the FTP server in passive mode

## Contributors
- [Aiq0](https://github.com/Aiq0)
- [themiddlehalf](https://github.com/themiddlehalf)

## License
The MIT License
