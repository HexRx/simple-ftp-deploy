#Simple FTP Deploy
> This package for Sublime Text 3 give you possibility to auto upload file to FTP server when you save local file.

1. How to Install
============
##Using [Package Control](https://packagecontrol.io)
1. In Sublime Text open menu `Tools -> Command Palette...`
2. Enter `Package Control: Install Package`
3. Find and install `Simple FTP Deploy`

##Manual
1. Download the [.zip](https://github.com/HexRx/simple-ftp-deploy/archive/master.zip)
2. Open `Packages` directory, which you can find using the Sublime Text menu item `Preferences -> Browse Packages...` and unzip archive to this directory

2. How to Use
============
1. Open folder which contain your local files in Sublime Text open menu `File -> Open Folder...` or `Project -> Add Folder to Project`
2. Create new `simple-ftp-deploy.json` config file in root of an opened directory (its settings see to configuration section)
3. Save it
4. Now open file which you want to edit, it must be located in an opened directory or in the inside folders, if you save it, this file will be upload to FTP server which you entered in config file

3. Configuration
============

Example `simple-ftp-deploy.json` file:

    {
        "host": "localhost",
        "username": "user",
        "password": "pass"
    }

###Format
The format is JSON, so every property consists of a key-value pair

    {
        "host": "localhost",
        "port": 21, 
        "username": "user",
        "password": "pass",
        "rootDirectory": "/path/"
    }

###Properties

`"host"` *string*
The hostname or IP address of your FTP server

`"port"` *number*
The port of the FTP server. *Optional property, default value: `21`*

`"username"` *string*
The username

`"password"` *string*
The password

`rootDirectory` *string*
The FTP path to deploy. *Optional property, default value: `/`*
**Example:** in the root of FTP you have three folders `site1`, `site2`, `site3` and if you need to upload in `site2` folder, you must set this property to `/site2`, because if you skip this property, files will be upload to the root of FTP
 
License
============
The MIT License