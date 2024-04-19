import json 
import os 

CACHEFILE = "sheetsApi/cache.json"

def fetch(cacheKey):
    if (not os.path.isfile(CACHEFILE)):
        file = open(CACHEFILE, "w")
        file.write("{}")
        file.close()

    file = open(CACHEFILE, "r")
    string = file.read()
    file.close()
    cache = json.loads(string)
    
    if cacheKey in cache.keys():
        return cache[cacheKey]
    else:
        return False
    

def save(cacheKey, value):
    file = open(CACHEFILE, "r")
    string = file.read()
    file.close()
    cache = json.loads(string)

    cache[cacheKey] = value    

    file = open(CACHEFILE, "w")
    string = json.dumps(cache)
    file.write(string)

    file.close()
