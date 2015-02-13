# encoding: utf8

# Robust Hebrew Tokenizer 
# KNOWN ISSUES:
#     - NOT VERY FAST!!!
#
#     - transition from hebrew words to numbers: ב-23:00  will be cut as ב-23 :00
#     - deliberately not segmenting משהוכלב from start of words before numbers/quotes/dashes
#     - emoticons are not supported (treated as punctuation)
#     - ' is always kept at end of hebrew chunks (a document level pre/post processing could help here)
#     - !!!!!!!111111 are split to !!!!!!!! 1111111
#########
import re
import codecs

def heb(s,t): return ('HEB',t)
def eng(s,t): return ('ENG',t)
def num(s,t): return ('NUM',t)
def url(s,t): return ('URL',t)
def punct(s,t): return ('PUNCT',t)
def junk(s,t): return ('JUNK',t)

#### patterns
_NIKUD = u"\u05b0-\u05c4"
_TEAMIM= u"\u0591-\u05af"

undigraph = lambda x:x.replace(u"\u05f0",u"וו").replace(u"\u05f1",u"וי").replace("\u05f2","יי").replace("\ufb4f","אל").replace(u"\u200d","")

_heb_letter = ur"([א-ת%s]|[דגזצתט]')" % _NIKUD

# a heb word including single quotes, dots and dashes  / this leaves last-dash out of the word
_heb_word_plus = ur"[א-ת%s]([.'`\"\-/\\]?['`]?[א-ת%s0-9'`])*" % (_NIKUD,_NIKUD)

# english/latin words  (do not care about abbreviations vs. eos for english)
_eng_word = ur"[a-zA-Z][a-zA-Z0-9'.]*"  

# numerical expression (numbers and various separators)
#_numeric = r"[+-]?[0-9.,/\-:]*[0-9%]"
_numeric = r"[+-]?([0-9][0-9.,/\-:]*)?[0-9]%?"

# url
_url = r"[a-z]+://\S+"

# punctuations
_opening_punc = r"[\[('`\"{]"
_closing_punc = r"[\])'`\"}]"
_eos_punct = r"[!?.]+"
_internal_punct = r"[,;:\-&]"

# junk
#_junk = ur"[^א-ת%sa-zA-Z0-9%%&!?.,;:\-()\[\]{}\"'\/\\+]+" #% _NIKUD
_junk = ur"[^א-ת%sa-zA-Z0-9!?.,:;\-()\[\]{}]+" % _NIKUD #%%&!?.,;:\-()\[\]{}\"'\/\\+]+" #% _NIKUD

is_all_heb = re.compile(ur"^%s+$" % (_heb_letter),re.UNICODE).match
is_a_number = re.compile(r"^%s$" % _numeric ,re.UNICODE).match
is_all_lat= re.compile(r"^[a-zA-Z]+$",re.UNICODE).match
is_sep = re.compile(r"^\|+$").match
is_punct = re.compile(r"^[.?!]+").match




#### scanner

scanner = re.Scanner([
   (r"\s+", None),
   (_url, url),
   (_heb_word_plus, heb),
   (_eng_word, eng),
   (_numeric,  num),
   (_opening_punc, punct),
   (_closing_punc, punct),
   (_eos_punct, punct),
   (_internal_punct, punct),
   (_junk, junk),
   ])

##### tokenize
def tokenize(sent):
   tok = sent
   parts,reminder = scanner.scan(tok)
   assert(not reminder)
   return parts

if __name__=='__main__':
   import sys
   from itertools import islice
   #FILTER = set(['JUNK','ENG'])
   FILTER = set()
   #for sent in codecs.open("10000utf8.sents","r","utf_8_sig"):
   for sent in codecs.open(sys.argv[1],"r","utf_8_sig"):
      #print u"\n".join(["%s %s" % (which,tok) for which,tok in tokenize(sent) if which not in FILTER]).encode("utf8")
      print " ".join([tok for (which,tok) in tokenize(sent)]).encode("utf-8")



