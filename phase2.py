import base64
import json
import logging

def generatephase2output(phase2out):
    f = open("output/phase2output.json", "w")
    json.dump(phase2out, f, indent=2)
    f.close()

logging.basicConfig(filename='logs/phase2.log',level=logging.DEBUG)
logging.info('Starting executing phase 2 of Unvalidated Redirect URL')

baseString = ["http://google.com"]
output = dict()
ls = list()
for element in baseString:
    ls.append(element)
    s = base64.b64encode(bytes(element))
    ls.append(s)

output["payload"] = ls
generatephase2output(output)
logging.info('Phase 2 of Unvalidated Redirect URL has ended. Check the output file for payloads')