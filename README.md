# Simple FTP Deploy
> This package for [Sublime Text 3/4](https://www.sublimetext.com/) gives you possibility to automatically upload or delete files from FTP server when you save or delete local files and also execute custom triggers.

## Features
- Upload or delete files from FTP server when you locally save or delete files
- TLS support
- Highly configurable
- Automatically create directory if it doesn't exists on the server
- Execute custom triggers on save / delete (see example usage [here](https://gist.github.com/Aiq0/790aa5f04209e5b049138445fd79c522))

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

Minimal `simple-ftp-deploy.json` file:
```json
{
    "host": "localhost",
    "username": "user",
    "password": "pass"
}
```

**Note:** Password is optional. If omitted, you will be asked for it once needed.

### Format
The format is [JSON](https://www.json.org), so every property consists of a key-value pair:
```json
{
    "host": "localhost",
    "port": 21,
    "username": "user",
    "password": "pass",
    "rootDirectory": "/path/",
    "ignoredFilenames": ["example.py", "anotherFilename.json"],
    "ignoredExtensions": [".ignore", ".txt"],
    "ignoredFolders": ["ignore", "IGNORE"],
    "reuseSessions": true,
    "connectionTimeout": 600,
    "passive": true,
    "useTLS": true,
    "disabledEvents": ["deleteFile"],
    "noPromptEvents": ["createFolder"],
    "triggers": [
        {
            "on": "save",
            "extensions": [".css", ".js"],
            "execute": ".simple-ftp-deploy/minifier.py"
        }
    ]
}
```

### Properties

`"host"` *string*  
The hostname or IP address of your FTP server.

`"port"` *number, optional (default: `21`)*  
The port of the FTP server.

`"username"` *string*  
The username.

`"password"` *string, optional*  
The password. If not given, you will be asked for it once needed.

`"rootDirectory"` *string, optional (default: `"/"`)*  
The FTP path to deploy.  
**Example:** in the root of FTP you have three folders `site1`, `site2`, `site3` and if you need to upload in `site2` folder, you must set this property to `/site2`, because if you skip this property, files will be upload to the root of FTP.

`"ignoredFilenames"` *array of strings, optional (default: `[]`)*  
List of filenames, that are ignored and not uploaded. Note that `"simple-ftp-deploy.json"` is ALWAYS ignored. **Case-sensitive**

`"ignoredExtensions"` *array of strings, optional (default: `[]`)*  
List of extensions to ignore. Note that it only check last extension (so `file.tar.gz` has extension `".gz"`) and if you want to ignore files like `.htaccess`, this file has no extension => use `"ignoredFilenames"` instead. **Case-sensitive**

`"ignoredFolders"` *array of strings, optional (default: `[]`)*  
List of folder names to ignore. The file is ignored, if it is in at least one of the specified folders (so `folder1/folder2/file.py` is ignored if `"ignoredFolders"` contains `"folder1"` and/or `"folder2"`). **Case-sensitive**

`"reuseSessions"` *boolean, optional (default: `true`)*  
Whatever FTP session will be reused for next action (keeps session open for `"connectionTimeout"`; previously named `"sessionCacheEnabled"`).

`"connectionTimeout"` *number, optional (default: `600`)*  
Sets timeout for FTP connections (in seconds).

`"passive"` *boolean, optional (default: `true`)*  
Whether to connect to the FTP server in passive mode.

`"useTLS"` *boolean, optional (default: `false`)*  
Whether to connect to the FTP server with TLS connection (May not work correctly in Sublime Text 3).

`"disabledEvents"` *array of strings, optional (default: `[]`)*  
List of events that will be disabled (for example if you do not want to click `Cancel` every time you are asked if you want to delete file(s) from FTP server too)
Available events are: `"deleteFile"`

`"noPromptEvents"` *array of strings, optional (default: `[]`)*  
List of events that won't prompt you (for example if you do not want to click `Delete` every time you are asked if you want to delete file(s) from FTP server too)
Available events are: `"deleteFile"`, `"createFolder"`

`"triggers"` *array of triggers (objects), optional (default: `[]`)*  
List of custom triggers to call when specific event happens. Each trigger can contain:

* `"on"` *string* - When to call trigger (available values: `"save"` or `"delete"`).
* `"extensions"` *array of string, optional* - For which file extensions call this trigger. See `"ignoredExtension"` for more info.
* `"filenames"` *array of string, options* - For which filenames call this trigger. See `"ignoredFilenames"` for more info.
* `"execute"` *string* - Path (relative from project root) to python file to execute

See example usage of triggers [here](https://gist.github.com/Aiq0/790aa5f04209e5b049138445fd79c522)


## Contributors
- [Aiq0](https://github.com/Aiq0)
- [themiddlehalf](https://github.com/themiddlehalf)

## License
The MIT License
