import csv
import httplib
import time

conn = httplib.HTTPConnection("localhost:8080")
headers = {"Content-type": "application/json"}
errors = []
size = 20

def importAreas():
    conn.request("DELETE", "/areas")
    conn.close()
    
    count = 0
    reader = csv.reader(open("areas.csv", "rb"))
    areaName = ["code", "name", "parent", "unit", "middle", "hasChild"]
    for row in reader:        
        areaValue = [str(unicode(cell, 'utf-8')) for cell in row]
        area = {}
        for i in range(6):
            area[areaName[i]] = areaValue[i]
        print "[import]" + area["code"]
        postArea(toJson(area))
        count += 1
        if size and count >= size:
            break

    while len(errors) != 0:
        area = errors.pop()
        print "[reimport]" + area["code"]
        postArea(area)

def toJson(area):
    return "{%s}" % ",".join([filedToJson(k,v) for k,v in area.items() if v and len(v) > 0])
        
def filedToJson(k, v):
    if k == "hasChild":
        return r'"%s":%s' % (k,v)
    else:
        return r'"%s":"%s"' % (k,v)
        
def postArea(json):
    try:
        conn.request("POST", "/areas", json, headers)
        response = conn.getresponse()
        if response.status != 204:
            print "[server error]" + json
            errors.append(json) 
        conn.close()  
    except: 
        print "[client error]" + json
        errors.append(json)
        time.sleep(1)      
    
def importExcludeWords():        
    reader = csv.reader(open("excludeWords.csv", "rb"))
    excludeWords = '{"words": [%s]}' % ",".join([r'"' + str(unicode(row[0], 'utf-8')) + r'"' for row in reader])         
    
    conn.request("PUT", "/excludeWords", excludeWords, headers)
    conn.close()

if __name__ == '__main__':
    importAreas()
    importExcludeWords()