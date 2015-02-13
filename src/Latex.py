#encoding=cp1255
dic = {}
dic['א']="'"
dic['ב']="b"
dic['ג']="g"
dic['ד']="d"
dic['ה']="h"
dic['ו']="w"
dic['ז']="z"
dic['ח']=".h"
dic['ט']=".t"
dic['י']="y"
dic['כ']="k"
dic['ך']="K"
dic['ל']="l"
dic['מ']="m"
dic['ם']="M"
dic['נ']="n"
dic['ן']="N"
dic['ס']="s"
dic['ע']="`"
dic['פ']="p"
dic['ף']="P"
dic['צ']=".s"
dic['ץ']=".S"
dic['ק']="q"
dic['ר']="r"
dic['ש']="/s"
dic['ת']="t"


def matrixToLatex(matrix,fileName):
    output = open(fileName,'w') 
    for row in matrix:
        s=''
        for c in row:
            s+=str(c)+' & '
        s=s[:-2]
        s+='\\\\\n'
        output.write(s)
        
def translateFromHebrew(hebString):
    ans = ''
    for c in hebString:
        if dic.has_key(c):
            ans+=dic[c]
        else:
            ans+=c
    print ans


translateFromHebrew("תודה אל/על הפרגון")
    