import base64
import json
import logging

def generatephase2output(phase2out):
    f = open("/home/user/tutorial/output/phase2output.json", "w")
    json.dump(phase2out, f, indent=2)
    f.close()

logging.basicConfig(filename='logs/phase2.log',level=logging.DEBUG)
logging.info('Starting executing phase 2 of Unvalidated Redirect URL')

baseString = ["http://wwww.google.com"]
output = dict()
ls = list()
ls.append(baseString)
for element in baseString:
    s = base64.b64encode(element.encode('ascii'))
    ls.append(str(s)[2:-1])
    ls.append(element)

output["payload"] = ls
generatephase2output(output)
logging.info('Phase 2 of Unvalidated Redirect URL has ended. Check the output file for payloads')