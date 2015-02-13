#encoding=cp1255

from nltk.tree import Tree
from nltk.corpus.reader import ChunkedCorpusReader
from nltk.tokenize import RegexpTokenizer
from bgutags_new import tostring1
from nltk import FreqDist
from nltk import ConditionalFreqDist
from nltk import bigrams
from nltk import trigrams
from itertools import izip
from codecs import open
from urllib2 import urlopen
from hebtokenizer import tokenize


class BguCorpusReader(ChunkedCorpusReader):
    
    #format=BGU : השבוע    1093009412    DEF:NOUN-M,S,ABS:    O    O 
    #format=BITMASK : השבוע  1093009412
    def __init__(self, directory="../text/tb/tagged",fileids=r".*.tagged",format="BGU"):
        ChunkedCorpusReader.__init__(self, directory ,fileids , str2chunktree=self.__str2BguTree,sent_tokenizer=RegexpTokenizer('\n\n', gaps=True))
        self._format = format
        
    
    #@return: FreqDist of words
    #@param th: threshold for filtering. less counts than th will not be in the fd
    def fdWords(self,th=0):        
        fd = FreqDist(self.words())
        self.__filterFd(fd,th)
        return fd    
    
    #@return: FreqDist of bigrams of words
    #@param th: threshold for filtering. less counts than th will not be in the fd
    def fdWords2(self,th=0):
        fd = FreqDist(bigrams(self.words()))
        self.__filterFd(fd,th)
        return fd
     
    #@return: FreqDist of trigrams of words
    #@param th: threshold for filtering. less counts than th will not be in the fd
    def fdWords3(self,th=0):
        fd = FreqDist(trigrams(self.words()))
        self.__filterFd(fd,th)
        return fd
    
    #@return: FreqDist of POS tags
    #@param th: threshold for filtering. less counts than th will not be in the fd
    def fdPosTags(self,th=0):
        fd = FreqDist(self.posTags())
        self.__filterFd(fd,th)
        return fd
     
    #@return: FreqDist of bigrams of POS tags
    #@param th: threshold for filtering. less counts than th will not be in the fd   
    def fdPosTags2(self,th=0):
        fd = FreqDist(bigrams(self.posTags()))
        self.__filterFd(fd,th)
        return fd
    
    #@return: FreqDist of trigrams of POS tags
    #@param th: threshold for filtering. less counts than th will not be in the fd                           
    def fdPosTags3(self,th=0):
        fd = FreqDist(trigrams((self.posTags())))
        self.__filterFd(fd,th)
        return fd
    
    #@return: iterator of POS tags
    def posTags(self,fileids=None):
        for _,t in self.tagged_words(fileids):
            yield  t.getPosTag()
    

    def __str2BguTree(self,text):
        lines = text.split('\r\n')
        tree = Tree('s',[])
        for line in lines:
            if line=='':
                continue
            if 'http://news.walla.co.il/' in line:
                continue 
            mlist = line.split("\t")
            word = mlist[0]
            if self._format=="BGU":
                raw = mlist[1:]
            if self._format=="BITMASK":
                raw = [mlist[1],tostring1(int(mlist[1])),None,None,None]
            if self._format=="POS":
                raw = [None,mlist[1],None,None,None]
            tree.append((word,bguTag(raw)))
        return tree
       
    def __filterFd(self,fd,th=0):
        if th<=1:
            return
        for w in fd.keys():
            if fd[w]<th and fd[w]>0:
                fd.pop(w)
            
    def __filterCfd(self,cfd,th=0):
        if th<=1:
            return
        for cond in cfd.conditions():
            self.filterFd(cfd[cond],th)
    
    
    #@return: list of (word,next POS tag)
    #@param th: threshold for filtering. less counts than th will not be in the list        
    def wordsNextPosTags(self,fdWords=None,th=0):
        ans = []
        tagged_words = self.tagged_words()
        if fdWords==None:
            fdWords = self.fdWords(th)
        for i in range(len(tagged_words)-1):
            word = tagged_words[i][0]
            if fdWords[word]>=th:
                nextTag = tagged_words[i+1][1].getPosTag()
                ans.append((word,nextTag))
        return ans
    
 
    #@return: list of (word,(next POS tag,next next POS tag))
    #@param th: threshold for filtering. less counts than th will not be in the list        
    def wordsNextPosTags2(self,fdWords=None,th=0):
        ans = []
        tagged_words = self.tagged_words()
        if fdWords==None:
            fdWords = self.fdWords(th)
        for i in range(len(tagged_words)-2):
            word = tagged_words[i][0]
            if fdWords[word]>=th:
                nextTags2 = (tagged_words[i+1][1].getPosTag(),tagged_words[i+2][1].getPosTag())
                ans.append((word,nextTags2))
        return ans

    #@return: list of (word,prev POS tag)
    #@param th: threshold for filtering. less counts than th will not be in the list        
    def wordsPrevPosTags(self,fdWords=None,th=0):
        ans = []
        tagged_words = self.tagged_words()
        if fdWords==None:
            fdWords = self.fdWords(th)
        for i in range(len(tagged_words)-1):
            word = tagged_words[i+1][0]
            if fdWords[word]>=th:
                prevTag = tagged_words[i][1].getPosTag()
                ans.append((word,prevTag))
        return ans

    #@return: list of (word,(prev prev POS tag,prev POS tag))
    #@param th: threshold for filtering. less counts than th will not be in the list        
    def wordsPrevPosTags2(self,fdWords=None,th=0):
        ans = []
        tagged_words = self.tagged_words()
        if fdWords==None:
            fdWords = self.fdWords(th)
        for i in range(len(tagged_words)-2):
            word = tagged_words[i+2][0]
            if fdWords[word]>=th:
                prevTags2 = (tagged_words[i][1].getPosTag(),tagged_words[i+1][1].getPosTag())
                ans.append((word,prevTags2))
        return ans
    
    #@return: ConditionalFreqDist of (word,next POS tag)
    #@param th: threshold for filtering. less counts than th will not be in the cfd   
    def cfdWordsNextPosTags(self,fdWords=None,th=0):
        cfd = ConditionalFreqDist(self.wordsNextPosTags(self.tagged_words(),fdWords,th))
        self.__filterCfd(cfd,th)
        return cfd
    
    #@return: ConditionalFreqDist of (word,(next POS tag,next POS tag))
    #@param th: threshold for filtering. less counts than th will not be in the cfd   
    def cfdWordsNextPosTags2(self,fdWords=None,th=0):
        cfd = ConditionalFreqDist(self.wordsNextPosTags2(self.tagged_words(),fdWords,th))
        self.__filterCfd(cfd,th)
        return cfd
    
    
    #@return: ConditionalFreqDist of (word,prev POS tag)
    #@param th: threshold for filtering. less counts than th will not be in the cfd   
    def cfdWordsPrevPosTags(self,fdWords=None,th=0):
        cfd = ConditionalFreqDist(self.wordsPrevPosTags(self.tagged_words(),fdWords,th))  
        self.__filterCfd(cfd,th)
        return cfd
    
    #@return: ConditionalFreqDist of (word,(prev prev POS tag,prev POS tag))
    #@param th: threshold for filtering. less counts than th will not be in the cfd   
    def cfdWordsPrevPosTags2(self,fdWords=None,th=0): 
        cfd = ConditionalFreqDist(self.wordsPrevPosTags2(self.tagged_words(),fdWords,th))
        self.__filterCfd(cfd,th)
        return cfd
    
    #@return: % of unknown words in this corpus comparing to a given lexicon corpus
    #@param corpus: a lexicon corpus
    def perOfUnknownWords(self,lexiconCorpus,fdWords=None):
        count = 0
        total = 0
        if fdWords==None:
            fdWords = lexiconCorpus.fdWords()
        for w in self.words():
            total+=1
            if fdWords[w]==0:
                count+=1
        return count/float(total)
    
   
   
#    def unknown_words(self,fileids=None):
#        file = open('../lexicon.txt','r','cp1255')
#        raw = file.read()
#        lexicon = raw.split('\r\n')
#        fdWords = FreqDist(lexicon)
#        for w,t in self.tagged_words(fileids):
#            if fdWords[w]==0 and fdWords[t.getLemma()]==0:
#                yield w
#     
#   
#                
#    def unknown_posTags(self,fileids=None):
#        file = open('../lexicon.txt','r','cp1255')
#        raw = file.read()
#        lexicon = raw.split('\r\n')
#        fdWords = FreqDist(lexicon)
#        for w,t in self.tagged_words():
#            if fdWords[w]==0 and fdWords[t.getLemma()]==0:
#                yield t.getPosTag()
#
#    
#    
#    def unknown_tagged_words(self,sentLength=None,fileids=None):
#        file = open('../lexicon.txt','r','cp1255')
#        raw = file.read()
#        lexicon = raw.split('\r\n')
#        fdWords = FreqDist(lexicon)
#        for tagged_sent,sent in izip(self.tagged_sents(),self.sents()):
#            ind = -1
#            for w,t in tagged_sent:
#                ind+=1
#                if fdWords[w]==0 and fdWords[t.getLemma()]==0:
#                    if sentLength!=None:
#                        yield ((w,t.getPosTag()),self.__sequence(sent,ind,sentLength))
#                    else:
#                        yield (w,t.getPosTag())
              
    def __sequence(self,words,start,count):
        ans = ''
        half = count/2
        for j in range(half):
            if start-(half-j)<len(words) and start-(half-j)>=0:
                ans+=words[start-(half-j)]+' '
        ans+='['+words[start]+'] '
        for j in range(half):
            if start+j+1<len(words) and start+j+1>=0:
                ans+=words[start+j+1]+' '
        return ans
    
    def getUrl(self,fileid):
        text = self.raw(fileid)
        url = text.split('\n')[0].split('\t')[0]
        return url[:-13]
    
    def getHeadLine(self,fileid):
        url = self.getUrl(fileid)
        rawHtml = urlopen(url).read()
        start = rawHtml.find('id="awqs1">',0)+11
        end = rawHtml.find('</h2>',start)
        start2 = rawHtml.find('id="awqs0">',0)+11
        end2 = rawHtml.find('</h1>',start2)
        return rawHtml[start2:end2],rawHtml[start:end]
    
    def getHeadLineWords(self,fileid):
        h1,h2 = self.getHeadLine(fileid)
        hTokenized = tokenize(h1+' '+h2.decode('cp1255'))
        words = [w for _,w in hTokenized]
        return words
    
"""======================class bguTag=====================================
======================================================================="""
    
class bguTag:
    def __init__(self,raw):
        self.__raw = raw
        
    #lemma might be an empty string!!!    
    def getLemma(self):
        bguTag = self.getBguTag()
        if bguTag[5]==None:
            return self.__raw[0]
        ans = bguTag[5].split('^')
        if len(ans)==1:
            return ans[0]
        return ans[1]
        
    def getRaw(self):
        return self.__raw
    
    def getBguTag(self):
        return self.__parseRaw(self.__raw[1])+self.__raw[2:]
       
    def getComplexPosTag(self):
        return self.__raw[1]
    
    def getPosTag(self):
        bguTag = self.getBguTag()
        pos = ''
        pre = bguTag[0]
        mid = bguTag[1]
        suf = bguTag[2]
        for t in pre:
            pos+=t[0]+' '
        pos+=mid[0]+' '
        for t in suf:
            pos+=t[0]+' '
        return pos[:-1]

    def __parseRaw(self,raw):
        pre,mid,suf = raw.split(':')
        pre = pre.split('+')
        pre = [w.split('-') for w in pre]
        suf = suf.split('+')
        suf = [w.split('-') for w in suf]
        mid = mid.split('-')
        if len(mid)>1:
            mid = (mid[0],mid[1].split(',')) 
        sufs = []
        for w in suf:
            if len(w)>1:
                sufs.append((w[0],w[1].split(',')))
            else:
                if w[0]!='':
                    sufs.append((w[0],[])) 
        pres = []
        for w in pre:
            if len(w)>1:
                pres.append((w[0],w[1].split(',')))
            else:
                if w[0]!='':
                    pres.append((w[0],[]))         
        return [pres,mid,sufs]
    
    
        






   

            

#print '1'
#tags = corpus.posTags()
#print '2'
#tags = corpus.posTags()
#print '3'
#print len(tagged_words)
#w,t = tagged_words[1056]
#print w
#print t.getRaw()
#print t.getPosTag()
#print t.getBguTag()
#          

