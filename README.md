# get\_ebook\_files\_from\_gihyo.py

This is a script for downloading ebook files (epub, pdf) you bought from Gihyo Digital Publishing.  
By calling it from cron, for example, if you bought monthly magazine subscription, you can read the latest magazines from local disk without downloading manually.

## Requirements

### Python version

- Python >= 3.7

## Install

Install playwright

```
$ pip install -r requirements.txt
```

Install browser for playwright

```
$ playwright install chromium
```

Install dependencies necessary to run browsers

```
$ playwright install-deps
```

## Set gihyo login info to conf file

Make `get_ebook_files_from_gihyo.conf` form `get_ebook_files_from_gihyo.conf.sample`  
Set your gihyo account email and password

```
[login]
email = SET_EMAIL_HERE
password = SET_PASS_HERE
```

## Run

[Command options]

```
usage: get_ebook_files_from_gihyo.py [-h] [-c CONF] [-s] -d DOWNLOAD_DIRECTORY [-t TITLE_OF_EBOOKS]

optional arguments:
  -h, --help            show this help message and exit
  -c CONF, --conf CONF  conf file path (default: /path/to/the/script/dir/get_ebook_files_from_gihyo.conf)
  -s, --show_browser
  -d DOWNLOAD_DIRECTORY, --download_directory DOWNLOAD_DIRECTORY
  -t TITLE_OF_EBOOKS, --title_of_ebooks TITLE_OF_EBOOKS
                        title of ebooks in regular expression (for example: "Software Design .*月号")
```

[Example commands]

Following command downloads every ebook files to `/path/to/ebooks`

```
$ ./get_ebook_files_from_gihyo.py --download_directory /path/to/ebooks
```

Following command downloads ebook files including `Software Design` in the title to `/path/to/ebooks`

```
$ ./get_ebook_files_from_gihyo.py --download_directory /path/to/ebooks --title_of_ebooks 'Software Design'
```

`--title_of_ebooks` supports regular expression  
Following command downloads ebook files including `Software Design .*月号` in the title to `/path/to/ebooks`

```
$ ./get_ebook_files_from_gihyo.py --download_directory /path/to/ebooks --title_of_ebooks 'Software Design .*月号'
```
