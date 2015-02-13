#encoding=utf-8 
import urllib
import bgutags_new
from codecs import open
from hebtokenizer import tokenize
import os
from compiler.ast import For
#fname = sys.argv[1]
foutname = "11"

#fout = sys.stdout #codecs.open(foutname,"w","utf8")

def do_post(text2):
	#text2 = text.decode("utf8")
	params = urllib.urlencode({'text':text2})#.encode("utf8")})
	#print "meni tagging ***"#	,params.decode("utf8"),"***"
	f = urllib.urlopen("http://amdsrv6.cs.bgu.ac.il:8080/bm", params)
	return processFile(f.readlines())

	
def processFile(fid):
	res = ""

	for line in fid:
		line = line.strip()#.decode("utf-8").encode("cp1255")
		if not line:
			res +="\n"
			continue
		mlist = line.split("\t")
		word = mlist[0].decode("utf-8")
		try:
			definition = bgutags_new.tostring1(int(mlist[1]))
			lema = mlist[2]
			mlist[2] = definition
			mlist.append(lema)
		except:
			print "error in  + "+str(line)
		res +="\t".join(mlist)+"\n"
	return res	

#raw text to tagged text using Meni's tagger
def exportTaggedFile(path,dirNumStr,fileNumStr):
	try:
		print fileNumStr
		inputFile = open(path,'r','cp1255')
		inputText = inputFile.read()
		taggedText = do_post(inputText.encode("utf8"))
		if taggedText=='':
			return
#		outputFile = open("../text/walla/walla_tagged/"+dirNumStr+"/"+fileNumStr+"_tagged.txt",'w','cp1255')
		outputFile = open("test2.txt",'w','cp1255')
		outputFile.write(taggedText)
		inputFile.close()
		outputFile.close()
	except:
		return


def exportTaggedDir1(dirNum):
	os.system("md ..\\text\\walla\walla_tagged\\"+str(dirNum))
	for i in range(44):
		fileNum = 56+ i + (100*dirNum)
		fileNumStr = str(fileNum)
		dirNumStr = str(dirNum)
		exportTaggedFile("../text/walla/walla_text/"+dirNumStr+"/"+fileNumStr+".txt",dirNumStr,fileNumStr)


#complete directory of raw text to tagged text using Meni's tagger
def exportTaggedDir(dirNum):
	os.system("md ..\\text\\walla\walla_tagged\\"+str(dirNum))
	for i in range(100):
		fileNum = i + (100*dirNum)
		fileNumStr = str(fileNum)
		dirNumStr = str(dirNum)
		exportTaggedFile("../text/walla/walla_text/"+dirNumStr+"/"+fileNumStr+".txt",dirNumStr,fileNumStr)
	
#raw text to tagged text using Meni's tagger
def exportUntaggedFile(path,dirNumStr,fileNumStr):
	print fileNumStr
	inputFile = open(path,'r')
	inputText = inputFile.read()
	#sents = inputText.split('\n\n\n')
	outputFile = open("../text/walla/walla_untagged/"+dirNumStr+"/"+fileNumStr+"_untagged.txt",'w','cp1255')
	#for s in sents:
	taggedText = tokenize(inputText.decode('cp1255'))
	if taggedText=='':
		return
	for _,w in taggedText:
		outputFile.write(w+'\n')
	#outputFile.write('\n')
	inputFile.close()
	outputFile.close()

#complete directory of raw text to tagged text using Meni's tagger
def exportUntaggedDir(osDirName,dirName,dirNum):
	dirNumStr = str(dirNum)
	os.system("md "+osDirName+"\\"+str(dirNumStr))
	for i in range(100):
		fileNum = i + (100*dirNum)
		fileNumStr = str(fileNum)
		try:
			exportUntaggedFile(dirName+"/"+dirNumStr+"/"+fileNumStr+".txt",dirNumStr,fileNumStr)
		except:
			continue
		




#defenition = xxx+xxxx:xxxx-xxx:
def parseDefenition(defenition):
	res = ""
	splitDef = defenition.split(':')
	for w in splitDef:
		if w!="":
			splitPlus = w.split("+")
			for pos in splitPlus:
				splitComma = pos.split(",")
				res += splitComma[0]+"\t"
	return res

exportTaggedFile('input2.txt','','')
#taggedFileToPosTagged('../test_tagged/1_tagged.txt',"",'1')


	
#usage do_post(mytext.encode("utf8"))
#for i in range(495):
#	exportUntaggedDir('..\\text\\walla\\walla_untagged','../text/walla/walla_text',i+1)


