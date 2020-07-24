import requests,re,io,sys
from datetime import datetime,timedelta
from requests.adapters import HTTPAdapter

channels=['sony-six/84','sony-ten-1/85','sony-ten-2/92','star-sports1/88','star-sports-select-1/86','star-sports-select-hd-2/214'
,'star-sports2/87','wow-hd/207']

with io.open("/etc/epgimport/sony.xml","w",encoding='UTF-8')as f:
    f.write(('<?xml version="1.0" encoding="UTF-8"?>'+"\n"+'<tv generator-info-name="By ZR1">').decode('utf-8'))
for code in channels:
    with io.open("/etc/epgimport/sony.xml","a",encoding='UTF-8')as f:
        f.write(("\n"+'  <channel id="'+code.split('/')[0]+'">'+"\n"+'    <display-name lang="en">'+code.split('/')[0]+'</display-name>'+"\r"+'  </channel>\r').decode('utf-8'))
for code in channels:
    with requests.Session() as s:
        s.mount('https://', HTTPAdapter(max_retries=10))
        url = s.get('https://www.peotv.com/tvguide/channel/'+code)
        title = re.findall(r'<h4 class="modal-title" style="margin-left:-10px;">(.*?)</h4>',url.text)
        times = re.findall(r'<span style="margin-left:0px;">(.*?)</span>',url.text)
        dess = re.findall(r'<p class=\"prog-desc\">\s+(.*?)<br>',url.text)
        start_date = datetime.strptime(re.findall(r'<span class="date-title" style="margin-right: 10px;">(.*?)</span>',url.text)[0],'%a %d/%b').strftime(str(datetime.today().year)+'-%m-%d')
        start=[]
        end=[]
        for time in times:
            end.append(time.split('to')[1].strip())
            start.append(time.split('to')[0].strip())
            
        time_start=[]
        time_end=[]
        now = datetime.strptime(start_date,'%Y-%m-%d')
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        last_hr = 0
        for d in start:
            h, m = map(int, d.split(":"))
            if last_hr > h:
                today += + timedelta(days=1)
            last_hr = h
            time_start.append(today + timedelta(hours=h, minutes=m))

        for s in end:
            h, m = map(int, s.split(":"))
            if last_hr > h:
                today += + timedelta(days=1)
            last_hr = h
            time_end.append(today + timedelta(hours=h, minutes=m))

        for elem,next_elem,en,titl,des in zip(time_start,time_start[1:] + [time_start[0]],time_end,title,dess):
            if time_start[-1]==elem and time_start[0]==next_elem:
                startime=datetime.strptime(str(elem),'%Y-%m-%d %H:%M:%S').strftime('%Y%m%d%H%M%S')
                endtime=datetime.strptime(str(en),'%Y-%m-%d %H:%M:%S').strftime('%Y%m%d%H%M%S')
                
            else:
                startime=datetime.strptime(str(elem),'%Y-%m-%d %H:%M:%S').strftime('%Y%m%d%H%M%S')
                endtime=datetime.strptime(str(next_elem),'%Y-%m-%d %H:%M:%S').strftime('%Y%m%d%H%M%S')
            ch=''
            ch+= 2 * ' ' +'<programme start="' + startime + ' +0650" stop="' + endtime + ' +0650" channel="'+code.split('/')[0]+'">\n'
            ch+=4*' '+'<title lang="en">'+titl.replace('&','and')+'</title>\n'
            ch+=4*' '+'<desc lang="en">'+des.replace('&','and').strip()+'</desc>\n  </programme>\r'
            with io.open("/etc/epgimport/sony.xml","a",encoding='UTF-8')as f:
                f.write(ch)
        print(code.split('/')[0]+' epg ends at '+str(time_end[-1]))
        sys.stdout.flush()
        
with io.open("/etc/epgimport/sony.xml", "a",encoding="utf-8") as f:
    f.write(('</tv>').decode('utf-8'))
    
import json
with open('/usr/lib/enigma2/python/Plugins/Extensions/Epg_Plugin/times.json', 'r') as f:
    data = json.load(f)
for bouquet in data['bouquets']:
    if bouquet["bouquet"]=="sony":
        bouquet['date']=datetime.today().strftime('%A %d %B %Y at %I:%M %p')
with open('/usr/lib/enigma2/python/Plugins/Extensions/Epg_Plugin/times.json', 'w') as f:
    json.dump(data, f)

