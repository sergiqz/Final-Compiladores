import re

OPR = ['+','-','*','/','<','>','<=','>=','==','!=','!','||','&&','=']
ADDOPR = ['+','-']
MULOPR = ['*','/']
COMPOPR = ['<','>','<=','>=','==','!=']
LOGICOPR = ['!','||','&&']

KEY = ['auto','break','case','const','continue','default','do','else','enum','extern','for','goto','if',
    'long','register','return','short','signed','sizeof','static','struct','switch','typedef','unsigned','union','volatile','while']
DIGIT = ['0','1','2','3','4','5','6','7','8','9']
BOUND = ['(',')','{','}','[',']',';',',']
FUNCTION = ['print','scan']
TYPE = ['int','void']
WS = [' ','\n','\t']


stack_offset = -4

tokens = []
token = None
MIDCODES=[]
RESULT=[]

REG_USED=set([])
WHOLE_VALTABLE={}
LOCAL_VALTABLE={}

FUNCTABLE={}
NOWFUNC=None

FUNC_CALL='FUNC_CALL'
FUNC_DECLARE='FUNC_DECLARE'

ISLOCAL='islocal'
ISWHOLE='iswhole'
ISCONST=False
ISBRANCH=False

WHOLE_STRING={}