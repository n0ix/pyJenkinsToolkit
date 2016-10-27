# pyJenkinsToolkit
A Jenkins Pentest/Security Toolkit written in Python

System Requirements:

- Python 2.7
- Python Module 'requests'
- Python Module 'urllib'
- Python Module 'urllib2'
- Python Module 'colorama'
- Python Module 'BeautifulSoup4'
- Python Module 'argparse'
- Python Module 'urlparse'

usage: pyJenkinsToolkit.py [-h] -u URL [URL ...] [-m {info,shell}] [-o OUTPUT]
                           [-spw SHELLPASSWORD] [-sp SHELLPORT]
                           [-st {perl,python}] [-v]

Jenkins Toolkit

optional arguments:
  -h, --help            show this help message and exit
  -u URL [URL ...], --url URL [URL ...]
                        <Required> One or more Jenkins Urls to process. You
                        can also specifiy a text file with the urls in it
  -m {info,shell}, --mode {info,shell}
                        <Required> Specifies the Toolkit Mode
  -o OUTPUT, --output OUTPUT
                        <Optional> File where the output is written (Only if
                        Mode = Info)
  -spw SHELLPASSWORD, --shellpassword SHELLPASSWORD
                        <Optional> Password for Shell
  -sp SHELLPORT, --shellport SHELLPORT
                        <Required (Mode Shell)> Port Bind Shell
  -st {perl,python}, --shelltype {perl,python}
                        <Optional (Mode Shell)> Specifies Shell Script Type -
                        Default:"perl"
  -v, --verbose         Show Debug Information
