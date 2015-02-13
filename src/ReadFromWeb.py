#coding=utf_8
from __future__ import division
from codecs import open
from urllib2 import urlopen
import string
import os
from nltk import clean_html
#checks if line contains hebrew chars
def containsWord(line):
    chars = ["à","á","â","ã","ä","å","æ","ç","è","é","ë","ì","î","ð","ñ","ò","ô","ö","÷","ø","ù","ú"]
    for c in chars:
        if c in line:
            return True
    return False

#checks if it is the signature of the TB
def signTb(line):
    return '|' in line

#removes the blankes from the line
def removeBlankes(line):
    while line[0] =='\t'  or line[0]==' ':
        line = line[1:]
    while line[-1] =='\t'  or line[-1]==' ' or line[-1]=='\r':
        line = line[:-1]
    return line

#counts spaces
def countWords(line):
    return line.count(' ')

#removes the punctuations from the end of the line
def removePunctuation(line):
    punc = ['.',',','!','?',':',"'",'-','"']
    while line[0] in punc:
        line = line[1:]
    while line[-1] in punc:
        line = line[:-1]
    return line

#removes brackets from the line
def removeBrackets(line):
    while '(' in line:
        i = string.find(line,'(')
        j = string.find(line,')')
        if i==-1 or j==-1:
            return line
        line = line[:i]+line[j+1:]
    return line

def fourChars(line):
    for i in range(len(line)-3):
        c = line[i]
        if line[i+1]==c and line[i+2]==c and line[i+3]==c:
            return False
    return True


# returns 0 if there aren't tb in url, 1 otherwise
def getTbFromUrl(url,path):
    rawHtml = urlopen(url).read()
    output = open(path,'w','cp1255')
    output.write(url+'\n'+'\n'+'\n')
    startInd = 0
    count = 0
    while startInd<len(rawHtml):
        startInd = rawHtml.find("w3 template_tb_text2",startInd)
        if startInd == -1:
            break
        else:
            startInd+=22
        endInd = rawHtml.find("</div>",startInd)
        tb = rawHtml[startInd:endInd]
        if  countWords(tb)>=10 and fourChars(tb):
            output.write(tb+'\n'+'\n'+'\n'+'\n'+'\n')
            count+=1
        startInd = endInd+1
    output.close()
    if count>=5:
        return 1
    else:
        return 0


def getTbs():
    fileInd = 24100
    urlInd = 1518566
    lib = 36
    while fileInd<100000:
        try:
            nextLib = int(fileInd/100)
            if lib!=nextLib:
                lib = nextLib
                os.system("md ..\\text\\"+ str(lib))
            fileInd += getTbFromUrl('http://news.walla.co.il/?w=/157/'+str(urlInd)+'/@@/talkbacks','../text/'+str(lib)+'/'+str(fileInd)+'.txt')
            urlInd+=1
        except:
            print '======except!!!======='
            print fileInd
            urlInd+=1
            continue
        
def getWalla():
    urlNum = 1708922
    for i in range(504):
        lib = str(i+496)
        os.system('md ..\\text\\walla\\walla_text\\'+lib)
        for j in range(100):
            fileNum = str(((i+496)*100)+j)
            try:
#                path = '../tb_text/'+lib+'/'+fileNum+'.txt'
#                file = open(path,'r')
#                url = file.read().split('\n')[0][:-13]
                while True:
                    urlNum+=1
                    url = "http://news.walla.co.il/?w=/157/"+str(urlNum)
                    print url
                    rawHtml = urlopen(url).read()
                    start = 0 
                    cleanText = ''
                    while start!=-1:
                        start = rawHtml.find('</div><div style="text-align:justify;',start)
                        end = rawHtml.find('</div><br><span class="wcflow">',start)
                        rawText = rawHtml[start:end]
                        cleanText+= clean_html(rawText)+' '
                        start = end
                    if len(cleanText)<3 or '\n\n' in cleanText or 'HTML PUBLIC' in cleanText:
                        continue
                    if len(cleanText)>200:
                        break
                out = open('../text/walla/walla_text/'+lib+'/'+fileNum+'.txt','w')
                while cleanText[-1]==' ':
                    cleanText = cleanText[:-1]
                out.write(cleanText)
                out.close()
                file.close()
            except:
                continue

f=0
out = open('../text/walla/tagged/1.tagged','w')           
for i in range(950):
    if i%10==0:
        f+=1
        out.close()
        out = open('../text/walla/tagged/'+str(f)+'.tagged','w')
    for j in range(100):
        try:
            path = '../text/walla/walla_tagged/'+str(i+1)+'/'+str((i+1)*100+j)+'_tagged.txt'
            print path
            input = open(path,'r')
            out.write(input.read())
            input.close()
        except:
            continue
    
