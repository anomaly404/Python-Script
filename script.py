import glob,subprocess
import os
import time,hashlib,json

dir="translations/musescore.musescore/"
final="s3://extensions.musescore.org/languages/"
pull=subprocess.Popen(['tx','pull','-a'])
pull.communicate()
langs= glob.glob(dir+"*.ts")
counter=0

entry={}

r=open("temp.txt","r")
read=r.readline()
langs_=dict()
while read!="":
	read_name=r.readline()
	print read
	langs_[read.split('\n')[0]]=read_name.split('\n')[0]
	read=r.readline()
try:
	json_data=open(dir+'details.json','r+')
	data=json.load(json_data)
except:
	counter=1
	entry["type"]="Languages"
	entry["version"]="2.0"
	json_data=open(dir+"details.json","w")

for item in langs:
	lang_code=item.split('/')[-1]
	lang_code=lang_code.split('.')[0]
	print item
	lang_time=int(os.path.getmtime(item))
	cur_time=int(time.time())
	print cur_time,lang_time,cur_time-lang_time
	
	if cur_time-lang_time<86400 or counter==1:
		hash_file=hashlib.sha1()
		lrelease=subprocess.Popen(['lrelease',dir+lang_code+'.ts','-qm',dir+lang_code+'.qm'])
		lrelease.communicate()
		file_size=os.path.getsize(dir+lang_code+'.qm')
		file_size="%.2f" %(float(file_size)/1024)
		print lang_code
		file=open(dir+lang_code+'.qm')
		hash_file.update(file.read())
		if counter==1:
			entry[lang_code]={"file_name":lang_code+".qm","hash":hash_file.hexdigest(),"name":langs_[lang_code],"file_size":file_size}

		else:
			data[lang_code]["hash"]=str(hash_file.hexdigest())
			data[lang_code]["file_size"]=file_size
			print data[lang_code]["hash"]
		push_s3=subprocess.Popen(['s3cmd','put','--acl-public','--guess-mime-type',dir+lang_code+'.qm',final+lang_code+'.qm'])
		push_s3.communicate()

if counter==1:
	print entry
	json_data.write(json.dumps(entry))
	json_data.close()
else:
	json_data.close()
	json_data=open(dir+"details.json","w")
	json_data.write(json.dumps(data,json_data))
	json_data.close()

push_json=subprocess.Popen(['s3cmd','put','--acl-public','--guess-mime-type',dir+'details.json',final+'details.json'])
push_json.communicate()
	
	
