import argparse
from csrfmap import CSRF
from argparse import RawTextHelpFormatter

def banner():
    return """                      
 _____ _____ _____ _____ _____ _____ _____ 
|     |   __| __  |   __|     |  _  |  _  |
|   --|__   |    -|   __| | | |     |   __|
|_____|_____|__|__|__|  |_|_|_|__|__|__|   
                                                       
                        v0.0.2 - @joaoviictorti 
    """
def argumentos():
    parser = argparse.ArgumentParser(prog=banner(),usage="csrfmap -a \"http://exemplo.com\" -m post -p form1 -n username password token",formatter_class=RawTextHelpFormatter)
    parser.add_argument("--version",action="version",version="csrfmap 0.0.2")
    parser.add_argument("-a","-A",dest="action",action="store",type=str,required=True,help="Insert action")
    parser.add_argument("-m","-M",dest="method",action="store",type=str,required=True,help="Insert method")
    parser.add_argument("-p",dest="payload",action="store",type=str,help=False,choices=["form1","form2","json1","json2"])
    parser.add_argument("-n","-name",nargs="+",dest="name",action="store",required=True,help="Insert name")
    parser.add_argument("-v","-value",nargs="+",dest="value",action="store",required=False,default="__valor__",help="Insert values")
    args = parser.parse_args()
        
    match args.payload:
        case "form1":
            match args.value:
                case "__valor__":
                    CSRF(action=args.action,method=args.method,name=args.name,values=args.value).CSRFUserInteraction()
                case _:
                    if len(args.name) == len(args.value):
                        CSRF(action=args.action,method=args.method,name=args.name,values=args.value).CSRFUserInteraction()
                    else:
                        print(CSRF().Error)
        case "form2":
            match args.value:
                case "__valor__":
                    CSRF(action=args.action,method=args.method,name=args.name,values=args.value).CSRFNoUserInteraction()
                case _:
                    if len(args.name) == len(args.value):
                        CSRF(action=args.action,method=args.method,name=args.name,values=args.value).CSRFNoUserInteraction()
                    else:
                        print(CSRF().Error)
        case "json1":
            match args.value:
                case "__valor__":
                    CSRF(action=args.action,method=args.method,name=args.name,values=args.value).CSRFJson()
                case _:
                    if len(args.name) == len(args.value):
                        CSRF(action=args.action,method=args.method,name=args.name,values=args.value).CSRFJson()
                    else:
                        print(CSRF().Error)
        case "json2":
            match args.value:
                case "__valor__":
                    CSRF(action=args.action,method=args.method,name=args.name,values=args.value).CSRFJsonCredentials()
                case _:
                    if len(args.name) == len(args.value):
                        CSRF(action=args.action,method=args.method,name=args.name,values=args.value).CSRFJsonCredentials()
                    else:
                        print(CSRF().Error)
        case _:
            pass