import csv
import httplib

conn = httplib.HTTPConnection("localhost:8080")
headers = {"Content-type": "application/json"}

def clearAreas():
    conn.request("DELETE", "/areas")
    conn.close()

def importExcludeWords():        
    reader = csv.reader(open("excludeWords.csv", "rb"))
    excludeWords = '{"words": [%s]}' % ",".join([r'"' + str(unicode(row[0], 'utf-8')) + r'"' for row in reader])         
    
    conn.request("PUT", "/excludeWords", excludeWords, headers)
    conn.close()

if __name__ == '__main__':
    clearAreas()
    importExcludeWords()