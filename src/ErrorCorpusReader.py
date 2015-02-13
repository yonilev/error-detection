#encoding=utf-8 
from BeautifulSoup import BeautifulSoup
from nltk.tree import Tree
import hebtokenizer
from nltk.corpus.reader import ChunkedCorpusReader
from nltk.tokenize import RegexpTokenizer
from BeautifulSoup import Tag



class ErrorCorpusReader(ChunkedCorpusReader):
    
    def __init__(self, directory="../text",fileids=r".*.txt",myEncoding="windows-1255"):
        ChunkedCorpusReader.__init__(self, directory ,fileids , str2chunktree=self.__str2ErrorTree,sent_tokenizer=RegexpTokenizer('\n\n\n', gaps=True),encoding=myEncoding)

    def __str2ErrorTree(self,text):
        soup = BeautifulSoup(text)
        tree = Tree('s',[])
        for content in soup.contents:
            if 'http://news.walla.co.il/' in content:
                continue  
            s,tag = self.__getTag(content)
            if tag=='ok':
                tokenized = hebtokenizer.tokenize(s)
                for tup in tokenized:
                    tree.append((tup[1],tag,''))
            else:
                error,target = s.split('$')
                tokenized = hebtokenizer.tokenize(error)
                #missing text tag
                if len(tokenized)==0:
                    tree.append(('',tag,target))
                else:
                    #the tag for the first word in the phrase
                    tree.append((tokenized[0][1],tag,target))
                    #the tag for the rest of the words in the phrase
                    for i in range(len(tokenized)-1):
                        tree.append((tokenized[i+1][1],tag+'$cont',''))     
        return tree

    def __getTag(self,soupContent):
        tag = ""
        while isinstance(soupContent,Tag):
            tag += soupContent.name+'$'
            soupContent = soupContent.contents[0]
        if len(tag)==0:
            tag = 'ok'
        else:
            tag = tag[:-1]
        return (soupContent,tag) 

#corpus = ErrorCorpusReader('../tagged1')
#tagged_words = corpus.tagged_words()
#print len(tagged_words)