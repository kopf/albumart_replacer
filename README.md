# Album art replacer
Copyright Aengus Walton 2011. See LICENCE for licencing information.

This is a simple script which takes a directory (or file in a directory) as an argument and 
searches tineye.com for higher-resolution copies of an image in that directory. 

It is most useful for automatically finding and saving higher-res copies of album art. 

## Installation and Configuration
* [Download a copy of the Master branch.](https://bitbucket.org/ventolin/albumart_replacer/get/master.zip) 
* Unpack the files and edit the settings.py file. At the moment, this file contains just one variable to be edited: FILENAMES.
This is a list of the files which the script will search for in the directory you pass it upon invokation. 
The script follows the order of the list. Once it finds a file, it presumes it is the file which needs replacing and disregards the rest.

## Requirements:
* pip install PIL
* pip install MultipartPostHandler