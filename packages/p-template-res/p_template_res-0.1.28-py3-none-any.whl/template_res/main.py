import sys
import argparse
import urllib3
import json

from template_res import template

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
subparsers = parser.add_subparsers()
parser_widget = subparsers.add_parser("list", help="资源列表")

def listTemplate():
    searchPath = ""
    if len(sys.argv) > 2:
         searchPath = sys.argv[2]
    result = template.listTemplate(searchPath)
    print(json.dumps(result))

def listMusic():
    searchPath = ""
    if len(sys.argv) > 2:
         searchPath = sys.argv[2]
    result = template.listMusic(searchPath)
    print(json.dumps(result))
    
module_func = {
    "list": listTemplate,
    "music": listMusic
}

def main():
    if len(sys.argv) < 2:
        return
    urllib3.disable_warnings()
    module = sys.argv[1]
    if module in module_func:
        module_func[module]()
    else:
        print("Unknown command:", module)
        sys.exit(0)
        
if __name__ == '__main__':
        main()
