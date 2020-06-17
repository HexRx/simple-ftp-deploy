# Simple FTP Deploy
> This package for Sublime Text 3 give you possibility to auto upload file to FTP server when you save local file.

## How to Install

### Using [Package Control](https://packagecontrol.io)
1. In Sublime Text open menu `Tools -> Command Palette...`
2. Enter `Package Control: Install Package`
3. Find and install `Simple FTP Deploy`

### Manual
1. Download the [.zip](https://github.com/HexRx/simple-ftp-deploy/archive/master.zip)
2. Open `Packages` directory, which you can find using the Sublime Text menu item `Preferences -> Browse Packages...` and unzip the archive to this directory.

## How to Use

1. Open folder which contains your local files in Sublime Text - open menu `File -> Open Folder...` or `Project -> Add Folder to Project...`.
2. Create new `simple-ftp-deploy.json` config file in the root of an opened directory (its settings see to configuration section)
3. Save the config file.
4. Now open file which you want to edit, it must be located in an opened directory or in the inside folders, if you save it, this file will be upload to FTP server which you entered in the config file.

## Configuration

Example `simple-ftp-deploy.json` file:

    {
        "host": "localhost",
        "username": "user",
        "password": "pass"
    }

### Format
The format is JSON, so every property consists of a key-value pair

    {
        "host": "localhost",
        "port": 21, 
        "username": "user",
        "password": "pass",
        "rootDirectory": "/path/",
        "autoCreateDirectory": false
    }

### Properties

`"host"` *string*  
The hostname or IP address of your FTP server.

`"port"` *number, optional (default: `21`)*  
The port of the FTP server.

`"username"` *string*  
The username

`"password"` *string*  
The password

`"rootDirectory"` *string, optional (default: `/`)*  
The FTP path to deploy.  
**Example:** in the root of FTP you have three folders `site1`, `site2`, `site3` and if you need to upload in `site2` folder, you must set this property to `/site2`, because if you skip this property, files will be upload to the root of FTP

`"autoCreateDirectory"` *boolean, optional (default: `false`)*  
Whatever to automatically create a directory if doesn't exist and don't prompt user for acceptation.

## Contributors
- [Aiq0](https://github.com/Aiq0)

## License
The MIT License
