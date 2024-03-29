from datetime import datetime
import csv
import httplib

test = True

if test:
    conn = httplib.HTTPConnection("localhost:8080")
    headers = {"Content-type": "application/json", "Cookie" : r'dev_appserver_login="test@example.com:True"'}
    size = 20
else:
    conn = httplib.HTTPConnection("address.muthos.cn")
    headers = {"Content-type": "application/json"}

errors = []

def importAreas():
    conn.request("DELETE", "/areas", headers = headers)
    conn.close()

    count = 0
    reader = csv.reader(open("areas.csv", "rb"))
    areaName = ["code", "name", "parentArea", "hasChild", "alphaCode", "pinyin", "alias", "postCode"]
    fieldLength = len(areaName)
    for row in reader:        
        areaValue = [str(unicode(cell, 'utf-8')) for cell in row]
        area = {}
        for i in range(fieldLength):
            area[areaName[i]] = areaValue[i]
        print "%s [import] %s" %(datetime.now(), area["code"])
        postArea(area)
        count += 1
        if test and count >= size:
            break

    while len(errors) != 0:
        area = errors.pop()
        print "%s [reimport] %s" %(datetime.now(), area["code"])
        postArea(area)

def toJson(area):
    return "{%s}" % ",".join([filedToJson(k,v) for k,v in area.items() if v and len(v) > 0])
        
def filedToJson(k, v):
    if k == "hasChild":
        return r'"%s":%s' % (k,v)
    else:
        return r'"%s":"%s"' % (k,v)
        
def postArea(area):
    try:
        conn.request("POST", "/areas", toJson(area), headers)
        response = conn.getresponse()
        if response.status not in (201, 204):
            print "[server error]" + area["code"]
            errors.append(area) 
        conn.close()  
    except: 
        print "[client error]" + area["code"]
        errors.append(area)
    
def importExcludeWords():        
    reader = csv.reader(open("excludeWords.csv", "rb"))
    excludeWords = '{"words": [%s]}' % ",".join([r'"' + str(unicode(row[0], 'utf-8')) + r'"' for row in reader])         
    
    conn.request("PUT", "/excludeWords", excludeWords, headers)
    conn.close()

if __name__ == '__main__':
    importAreas()
    importExcludeWords()