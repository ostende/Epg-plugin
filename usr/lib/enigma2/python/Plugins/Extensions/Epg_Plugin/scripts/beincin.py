#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import requests,re,io,sys,os,ssl
from datetime import datetime,timedelta
from time import sleep,strftime
from requests.adapters import HTTPAdapter
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

def get_tz():
    url_timezone = 'http://worldtimeapi.org/api/ip'
    requests_url = requests.get(url_timezone)
    ip_data = requests_url.json()

    try:
        return ip_data['utc_offset'].replace(':', '')
    except:
        return ('+0000')
    
time_zone=get_tz()

headers={
    'Host': 'elcinema.com',
    'Connection': 'keep-alive',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) snap Chromium/80.0.3987.149 Chrome/80.0.3987.149 Safari/537.36'
}
nb_channel=['1322-BEINMOVIESPREMIERE','1323-BEINMOVIESACTION','1324-BEINMOVIESDRAMA','1325-BEINMOVIESFAMILY','1326-BeInBoxOffice','1327-BeInSeriesHD1'
            ,'1328-BeInSeriesHD2','1309-beINDrama','1330-FOXACTIONMOVIES','1331-FOXFAMILYMOVIESHD']

REDC =  '\033[31m'                                                              
ENDC = '\033[m'                                                                 
                                                                                
def cprint(text):                                                               
    print REDC+text+ENDC
  
print('**************ELCINEMA BEIN ENTERTAINMENT EPG******************')  
with io.open("/etc/epgimport/beinentCin.xml","w",encoding='UTF-8')as f:
    f.write(('<?xml version="1.0" encoding="UTF-8"?>'+"\n"+'<tv generator-info-name="By ZR1">').decode('utf-8'))

for x in nb_channel:
    with io.open("/etc/epgimport/beinentCin.xml","a",encoding='UTF-8')as f:
        f.write(("\n"+'  <channel id="'+x.split('-')[1]+'">'+"\n"+'    <display-name lang="en">'+x.split('-')[1]+'</display-name>'+"\n"+'  </channel>\r').decode('utf-8'))

class elcin():
    def __init__(self):
        self.now=datetime.today().strftime('%Y %m %d')
        self.time=[]
        self.end=[]
        self.des=[]
        self.titles=[]
        self.prog_start=[]
        self.prog_end=[]
        self.title=[]
        self.error = False
        self.channel_name=''
        self.url=''
    def main(self):
        for nb in nb_channel:
            self.nb=nb
            self.time[:]=[]
            self.end[:]=[]
            self.des[:]=[]
            self.titles[:]=[]
            self.prog_start[:]=[]
            self.prog_end[:]=[]
            self.title[:]=[]
            with requests.Session() as s:
                ssl._create_default_https_context = ssl._create_unverified_context
                s.mount('http://', HTTPAdapter(max_retries=10))
                self.url = s.get('http://elcinema.com/tvguide/'+self.nb.split('-')[0]+'/',headers=headers,verify=False)
                for time in re.findall(r'(\d\d\:\d\d.*)',self.url.text):
                    if 'مساءً'.decode('utf-8') in time or 'صباحًا'.decode('utf-8') in time:
                        start=datetime.strptime(time.replace('</li>','').replace('مساءً'.decode('utf-8'),'PM').replace('صباحًا'.decode('utf-8'),'AM'),'%I:%M %p')
                        self.time.append(start.strftime('%H:%M'))
                for end in re.findall(r'\"subheader\">\[(\d+)',self.url.text):     
                    self.end.append(int(end))
                    
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) 
                last_hr = 0
                for d in self.time:
                    h, m = map(int, d.split(":"))
                    if last_hr > h:
                        today += + timedelta(days=1)
                    last_hr = h
                    self.prog_start.append(today + timedelta(hours=h, minutes=m))
                    
                for f,l in zip(re.findall(r'<li>(.*?)<a\shref=\'#\'\sid=\'read-more\'>',self.url.text),re.findall(r"<span class='hide'>[^\n]+",self.url.text)):
                    self.des.append(f+l.replace("<span class='hide'>",'').replace('</span></li>',''))
                    
                self.title = re.findall(r'<a\shref=\"\/work\/\d+\/\">(.*?)<\/a><\/li',self.url.text)
                mt2 = re.findall(r'<a\shref=\"\/work\/\d+\/\">(.*?)<\/a><\/li|columns small-7 large-11\">\s+<ul class=\"unstyled no-margin\">\s+<li>(.*?)<\/li>',self.url.text)
                for m in mt2:
                    if m[0]=='' and m[1]=='':
                        self.titles.append('Unknown program')
                    elif m[0]=='':
                        self.titles.append(m[1])
                    else:
                        self.titles.append(m[0])
                try:
                    for index, element in enumerate(self.titles):
                        if element not in self.title:
                            self.des.insert(index,"No description Found for this program")
                    b = datetime.strptime(self.now+' '+self.time[0],'%Y %m %d %H:%M').strftime('%Y %m %d %H:%M')
                    a = datetime.strptime(b,'%Y %m %d %H:%M')
                    for r in self.end:
                        x=a+timedelta(minutes=r)
                        a += timedelta(minutes=r)
                        self.prog_end.append(x)
                except IndexError:
                    self.error = True
                    cprint('No epg found or missing data for : '+self.nb.split('-')[1])
                    sys.stdout.flush()
                    pass
                for elem,next_elem,title,des in zip(self.prog_start,self.prog_end,self.titles,self.des):
                    ch=''
                    startime=datetime.strptime(str(elem),'%Y-%m-%d %H:%M:%S').strftime('%Y%m%d%H%M%S')
                    endtime=datetime.strptime(str(next_elem),'%Y-%m-%d %H:%M:%S').strftime('%Y%m%d%H%M%S')
                    ch+= 2 * ' ' +'<programme start="' + startime + ' '+time_zone+'" stop="' + endtime + ' '+time_zone+'" channel="'+self.nb.split('-')[1]+'">\n'
                    ch+=4*' '+'<title lang="ar">'+title.replace('&#39;',"'").replace('&quot;','"').replace('&amp;','and')+'</title>\n'
                    ch+=4*' '+'<desc lang="ar">'+des.replace('&#39;',"'").replace('&quot;','"').replace('&amp;','and').replace('(','').replace(')','').strip()+'</desc>\n  </programme>\r'
                    with io.open("/etc/epgimport/beinentCin.xml","a",encoding='UTF-8')as f:
                        f.write((ch).decode('utf-8'))    
            if self.error:
                self.error = False
                pass
            else:
                print self.nb.split('-')[1]+' epg ends at : '+str(self.prog_end[-1])
                sys.stdout.flush()
        
if __name__=='__main__':
    import time
    Hour = time.strftime("%H:%M")
    start='00:00'
    end='02:00'
    if Hour>=start and Hour<end:
        print 'Please come back at 2am to download the epg'
    else:
        elcin().main()
        from datetime import datetime
        import json
        with open('/usr/lib/enigma2/python/Plugins/Extensions/Epg_Plugin/times.json', 'r') as f:
            data = json.load(f)
        for channel in data['bouquets']:
            if channel["bouquet"]=="beincin":
                channel['date']=datetime.today().strftime('%A %d %B %Y at %I:%M %p')
        with open('/usr/lib/enigma2/python/Plugins/Extensions/Epg_Plugin/times.json', 'w') as f:
            json.dump(data, f)
    
    
with io.open("/etc/epgimport/beinentCin.xml", "a",encoding="utf-8") as f:
    f.write(('</tv>').decode('utf-8'))
       

print('**************FINISHED******************')
