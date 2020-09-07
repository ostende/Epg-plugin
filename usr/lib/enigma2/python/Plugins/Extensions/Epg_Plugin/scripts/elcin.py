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
    "Connection": "keep-alive",
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36'
}
nb_channel=['1101-Aloula', '1120-ART_Aflam_1', '1121-ART_Aflam_2', '1122-ART_Hekayat', 
            '1134-ONDrama', '1135-Emirates', '1136-Abu_Dhabi_TV', '1137-Alhayat_TV', 
            '1138-AlhayatDrama', '1145-Mehwar', '1148-RotanaCinema EGY', '1156-NileDrama', 
            '1157-Nile_Cinema', '1158-NileComedy', '1159-NileLife', '1168-LBCI', '1169-Dubai_TV', 
            '1170-AlraiTV', '1173-Dubai_One', '1174-AlKaheraWalNasTV', '1176-Cima', '1177-SamaDubai', 
            '1177-Sama_Dubai', '1178-Abu_Dhabi_Drama', '1179-Dream', '1182-ART_Hekayat_2', 
            '1188-SharjahTV', '1193-Al_Nahar_TV', '1195-ART_Cinema', '1198-CBC', '1199-CBC_Drama', 
            '1203-ONE', '1204-iFILMTV', '1216-AlJadeedTV', '1217-Rotana_Classic', '1223-Al_Nahar_Drama', 
            '1226-SadaElBalad', '1227-SadaElBaladDrama', '1252-AlKaheraWalNasTV2', '1260-CBC_sofra', 
            '1261-Zee_alwan', '1262-Zee_aflam', '1264-AlDafrah', '1269-Alsharqya', '1279-SadaElBalad+2', 
            '1280-TeNTV', '1283-Dubai_Zaman', '1290-DMC', '1292-DMC_DRAMA', '1296-MTVLebnon', '1297-SBC', 
            '1298-Amman', '1299-Roya', '1300-SyriaDrama', '1301-Alsumaria', '1302-Fujairah', '1304-Nessma', 
            '1308-Watania1', '1310-Kuwait', '1313-Lana', '1314-JordanTV', '1317-Oman', '1321-almanar', 
            '1334-Watania2', '1336-MasperoZaman', '1338-SyriaTV', '1339-AlSaeedah', 
            '1339-Al_Saeedah', '1341-LBC', '1342-LanaPlusTV', '1350-SamaTV', '1352-Saudiya_TV', '1355-Mix']


REDC =  '\033[31m'                                                              
ENDC = '\033[m'                                                                 
                                                                                
def cprint(text):                                                               
    print REDC+text+ENDC

print('**************ELCINEMA EPG******************')
 
with io.open("/etc/epgimport/elcinema.xml","w",encoding='UTF-8')as f:
    f.write(('<?xml version="1.0" encoding="UTF-8"?>'+"\n"+'<tv generator-info-name="By ZR1">').decode('utf-8'))

for x in nb_channel:
    with io.open("/etc/epgimport/elcinema.xml","a",encoding='UTF-8')as f:
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
                s.mount('https://', HTTPAdapter(max_retries=100))
                self.url = s.get('https://elcinema.com/tvguide/'+self.nb.split('-')[0]+'/',headers=headers,verify=False)
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
                            self.des.insert(index,"يتعذر الحصول على معلومات هذا البرنامج")
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
                    with io.open("/etc/epgimport/elcinema.xml","a",encoding='UTF-8')as f:
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
            if channel["bouquet"]=="elcin":
                channel['date']=datetime.today().strftime('%A %d %B %Y at %I:%M %p')
        with open('/usr/lib/enigma2/python/Plugins/Extensions/Epg_Plugin/times.json', 'w') as f:
            json.dump(data, f)
    
    
with io.open("/etc/epgimport/elcinema.xml", "a",encoding="utf-8") as f:
    f.write(('</tv>').decode('utf-8'))
    
          
print('**************FINISHED******************')
