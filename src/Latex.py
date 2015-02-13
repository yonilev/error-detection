#encoding=cp1255
dic = {}
dic['�']="'"
dic['�']="b"
dic['�']="g"
dic['�']="d"
dic['�']="h"
dic['�']="w"
dic['�']="z"
dic['�']=".h"
dic['�']=".t"
dic['�']="y"
dic['�']="k"
dic['�']="K"
dic['�']="l"
dic['�']="m"
dic['�']="M"
dic['�']="n"
dic['�']="N"
dic['�']="s"
dic['�']="`"
dic['�']="p"
dic['�']="P"
dic['�']=".s"
dic['�']=".S"
dic['�']="q"
dic['�']="r"
dic['�']="/s"
dic['�']="t"


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


translateFromHebrew("���� ��/�� ������")
    