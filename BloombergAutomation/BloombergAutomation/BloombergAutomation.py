##import blpapi 
##import pdblp as blp
import json

##Configuration Stage
with open("Configuration.json") as json_file:
    basic_config=json.load(json_file)

print(basic_config)



