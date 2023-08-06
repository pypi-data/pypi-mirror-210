import requests
import json
import urllib.parse
import sys
import os.path

#import .sdb as sdb

name = "nwebclient"

class NWebGroup:
    __client = None
    __data = None
    def __init__(self, client, data):
        self.__client = client
        self.__data = data
    def guid():
        return self.__data['guid']
    def title():
        return self.__data['title']
    def println(self):
        for key, value in self.__data.iteritems():
            print(key + ": " + value)
    def asDict(self):
        return self.__data;
    def docs(self):
        """
        :rtype: [NWebDoc]
        """
        contents = self.__client.req('api/documents/' + str(self.__data['group_id']))
        j =json.loads(contents);
        items = j['items'];
        #return j.items;
        return map(lambda x: NWebDoc(self.__client, x), items)
class NWebDoc:
    __client = None
    __data = None
    def __init__(self, client, data):
        self.__client = client
        self.__data = data
    def title(self):
        return self.__data['title']
    def name(self):
        return self.__data['name']
    def kind(self):
        return self.__data['kind']
    def content(self):
        return self.__data['content']
    def printInfo(self):
        s = "Doc-"+self.kind()+"(id:"+self.id()+", title: "+self.title()
        if (self.kind()=="image"):
            s+=" thumb: " + self.__data['thumbnail']['nn'] + " "
        s+=")"
        print(s)
    def id(self):
        return self.__data['document_id']
    def tags(self):
        return self.__data['tags']
    def println(self):
        print(self.__data)
        #for key, value in self.__data.iteritems():
        #    print key + ": " + value
    def downloadThumbnail(self, size = 'nn'):
        # TODO imple   
        path = 'image/'+self.id()+'/thumbnail/'+size+'/'+self.id()+'.jpg'
        return 0
    def save(self, file):
        self.__client.reqToFile('/w/d/'+str(self.id())+'/download', file)
    def setContent(self, content):
        self.__data['content'] = content
        self.__client.req('api/document/'+self.__data['document_id'], {
            'action': 'update',
            'content': content
        })
class NWebClient:
    __url = ""
    __user = ""
    __pass = ""
    __cfg = {}
    ssl_verify = False
    def __init__(self, url, username = '', password = ''):
        """
          Anstatt url kann auch ein Pfad zur einer JSON-Datei, die die Schluessel enthaelt, angegeben werden. 
          url https://bsnx.net/4.0/
        """
        if url is None:
            if os.path.isfile('/etc/nweb.json'):
                url = '/etc/nweb.json'
            if os.path.isfile('nweb.json'):
                url = 'nweb.json'
        if url[0] == '/' or url.endswith('nweb.json'):
            self.__cfg = json.loads(self.file_get_contents(url))
            self.__url = self.__cfg['url']
            self.__user = self.__cfg['username']
            self.__pass = self.__cfg['password']
        else:
            self.__url = url
            self.__user = username
            self.__pass = password
    def __call__(self, q):
        return "NWebClient TODO"
    def __getitem__(self, key):
        if key in self.__cfg:
            return self.__cfg[key]
        else:
            return "Non Existing"
    def __repr__(self):
        return f'<NWebClient {self.__url} User: {self.__user} docs() >'
    def file_get_contents(self, filename):
        with open(filename) as f:
            return f.read()
    def _appendGet(self, url, name, value):
        v = name + '=' + urllib.parse.quote(value)
        if '?' in url:
            return url + '&' + v
        else:
            return url + '?' + v
    def reqToFile(self, path, name):
        url = self.__url + path
        url = self._appendGet(url, 'username', self.__user)
        url = self._appendGet(url, 'password', self.__pass)
        r = requests.get(url, stream=True, verify=self.ssl_verify) 
        if r.status_code == 200:
            with open(name, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
    def req(self, path, params = {}):
        if self.__user != "":
            params["username"]= self.__user
            params["password"]= self.__pass
        url = self.__url+path
        #print("NWEB-Client: " + url);
        res = requests.post(url, data=params, verify=self.ssl_verify)
        return res.text
    def upload(self, path, params={}, name='file', data=None):
        """ open('file.txt','rb') """
        url = self.__url+path
        if self.__user != "":
            params["username"]= self.__user
            params["password"]= self.__pass
        files = {name: data}
        r = requests.post(url, files=files, data=params)
    def doc(self, id):
        response = self.req("api/document/"+str(id), {format:"json"})
        #print(response)
        data = json.loads(response);
        return NWebDoc(self, data)
    def docs(self, q = ''):
        """ Syntax: q """
        ja = self.req('w/api/docs?'+q);
        items = json.loads(ja)
        return list(map(lambda x: NWebDoc(self, x), items))
    def group(self, id): 
        data = json.loads(self.req("api/group/"+id, {format:"json"}))
        return NWebGroup(self, data)
    def getOrCreateGroup(self, guid, title):
        return "TODO"
    def createDoc(self, name, content, group_id, kind='markup'):
        res = self.req("w/group/"+str(group_id)+"/create", {
            "title": name,
            "content": content,
            "kind": kind
        })
        return res
    def createFileDoc(self, name, group_id, data):
        """  open('file', 'rb') """
        self.upload("w/group/"+str(group_id)+"/create", {
            "title": name,
            "kind": 'binary'
        }, 'file', data)
    def deleteDoc(self, id):
        return self.req('w/d/'+str(id)+'/delete', {'confirm': 1})
    def downloadImages(self, limit=1000, tag=None):
        # https://bsnx.net/4.0/w/api/docs?tag=Untertage
        q = 'kind=image&limit='+str(limit)
        if not tag is None:
            q = q + "&tag=" + str(tag)
        docs = self.docs(q)
        for doc in docs:
           self.reqToFile('image/'+str(doc.id())+'/orginal/web/'+str(doc.id())+'.jpg', str(doc.id())+ '.jpg')
           print("Download Image: " + str(doc.id()))

def metric_val(baseUrl, metricName, val):
    """ baseUrl: string = e.g. https://bsnx.net/metric-endpoint """
    requests.get(url=baseUrl, params= {'metric':metricName, 'val':val})

def main():
    print("nx-c")
    c = NWebClient(None)
    print(sys.argv)
    print(str(c.docs()))

if __name__ == '__main__': # nx-c vom python-package bereitgestellt
    main()
