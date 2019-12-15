from define import *
from mips import *
import re
import sys
import os
from sys import argv

debug = 0

point_token = 0
point_t=0
point_s=0
point_label=0
point_string=0

class TOKEN:
    def __init__(self,Name=None,Type=None):
        self.Name = Name
        self.Type = Type

    def to_int(self,s):
        r= re.match(r'^-?[1-9]\d*|0',s)
        res = r.group()
        return res,len(res)

    def to_val(self,s):
        r= re.match(r'^[a-zA-Z_]\w*',s)
        res = r.group()
        return res,len(res)

    def to_opr(self,s):
        r= re.match(r'^[\+\-\*/]|[<>=!]=?|\|\||&&',s)
        res = r.group()
        return res,len(res)
    
    def to_string(self,s):
        isok=0
        for ind,ch in enumerate(s):
            if(ind==0):
                continue
            if(ch=='"'):
                isok=1
                break
        if(not isok):
            exit('no " match')
        return s[:ind+1],len(s[:ind+1])

    def show(self):
        print((self.Name,self.Type))

    def nextToken(self):
        return tokens[point_token]

    def preToken(self):
        return tokens[point_token-2]

    def getNextToken(self):
        global point_token,token
        token = tokens[point_token]
        point_token+=1

    def tokenBack(self):
        global point_token
        point_token-=1

    def getTokens(self,s):
        words=[]
        while(1):
            r=getMarks(s)
            if(len(r)==0):
                break
            x=r[0]
            y=r[1]
            words+=s[:x].split()
            words.append(s[x:y+1])
            s=s[y+1:]

        words+=s.split()
        for s in words:

            while(len(s)):
                ch=s[0]
                if ch == ' ':
                    s=s[1:]
                
                elif ch in OPR:
                    res,i = self.to_opr(s)
                    token = TOKEN(res,'OPR')
                    tokens.append(token)
                    s=s[i:]
                elif ch in BOUND:
                    token = TOKEN(ch,'BOUND')
                    tokens.append(token)
                    s=s[1:]
                elif ch.isdigit():
                    res,i = self.to_int(s)
                    token = TOKEN(res,'DIGIT')
                    s = s[i:]
                    tokens.append(token)
                elif ch.isalpha():
                    res,i = self.to_val(s)
                    if(res in KEY):
                        token = TOKEN(res,'KEY')
                    elif(res in FUNCTION):
                        token = TOKEN(res,'SYSCALL')
                    elif(res in TYPE):
                        token = TOKEN(res,'TYPE')
                    else:
                        token = TOKEN(res,'VAL')
                    s=s[i:]
                    tokens.append(token)
                
                elif ch=='"':
                    res,i = self.to_string(s)
                    token = TOKEN(res,'STRING')
                    s=s[i:]
                    tokens.append(token)
                else:
                    for i in tokens:
                        i.show()
                    exit(ch+' ES ILEGAL')
        
        for i,t in enumerate(tokens):
            if(t.Name in FUNCTABLE.keys()):
                t.Type=FUNC_CALL
            try:
                if(t.Type=='VAL' and tokens[i+1].Name=='(' and tokens[i-1].Type=='TYPE'):
                    t.Type=FUNC_DECLARE
                    FUNCTABLE[t.Name]={'param_num':None,'return_type':tokens[i-1].Name}
            except:
                pass

def init_sentence():
    global point_t
    point_t=0
    for attr in WHOLE_VALTABLE.values():
        attr['reg']=None
    for attr in LOCAL_VALTABLE.values():
        attr['reg']=None
    REG_USED.clear()

def init_func():
    LOCAL_VALTABLE.clear()
    global stack_offset
    stack_offset = -4

def func_head(func_name):
    gen('label',func_name)
    gen('protect',['$ra','$fp'])
    gen('=','$fp','$sp')

def func_end():
    gen('return',None)

def newLable():
    global point_label
    lable = 'L'+str(point_label)
    point_label+=1
    return lable

def newStringName():
    global point_string
    name = 'string'+str(point_string)
    point_string+=1
    return name

def getRegt(n):
    global point_t
    if(n==-1):
        if(point_t==0):
            reg='$t0'
        else:
            reg = '$t'+str(point_t-1)
        return reg
    for _ in range(10):
        reg = '$t'+str(point_t)
        point_t+=1
        if reg not in REG_USED:
            break

    return reg

def getMarks(s):
    res=[]
    for ind,ch in enumerate(s):
        if(ch=='"'):
            res.append(ind)
    if(len(res)%2==1):
        exit("falta \"")
    return res[:2]

def exchange2reg(id):
    if(id in LOCAL_VALTABLE.keys()):
        id = LOCAL_VALTABLE[id]['reg']
    elif(id in WHOLE_VALTABLE.keys()):
        id = WHOLE_VALTABLE[id]['reg']
    return id
    
def gen(opr,des,sou1=None,sou2=None):
    if(opr == 'label'):
        try:
            if((opr,des)==MIDCODES[-1]):
                return
        except:
            pass
        print(des+':')
        MIDCODES.append((opr,des))
        return

    if(opr in ['return','push','pop']):
        des=exchange2reg(des)
    
    if(opr=='load' or opr =='store'):
        des=exchange2reg(des)

    if(sou1 is None and sou2 is None):
        print((opr,des))
        MIDCODES.append((opr,des))
    elif(sou2 is None):
        print((opr,des,sou1))
        MIDCODES.append((opr,des,sou1))
    else:
        print((opr,des,sou1,sou2))
        MIDCODES.append((opr,des,sou1,sou2))


def judgeVAL(idname,index_reg=0):
    if(idname in LOCAL_VALTABLE.keys()):
        if(LOCAL_VALTABLE[idname]['array']):
            base=LOCAL_VALTABLE[idname]['offset']+'($fp)'
            t1reg=getRegt(1)
            gen('arraylocal',t1reg,base,index_reg)
            return t1reg
        else:
            return LOCAL_VALTABLE[idname]['offset']+'($fp)'
    elif(idname in WHOLE_VALTABLE.keys()):
        if(WHOLE_VALTABLE[idname]['array']):
            base=idname
            t1reg=getRegt(1)
            gen('arraywhole',t1reg,base,index_reg)
            return t1reg
        else:
            return idname
    else:
        exit('varaible:'+idname+' no esta declarada')



class ASSIGN:
    def S(self):
        if(debug):
            print('S->',token.Name)

        if(token.Type=='VAL'):

            if(token.nextToken().Name!='['):
                idname=judgeVAL(token.Name)
                
            else:
                address_reg=self.A()
                idname='0('+address_reg+')'
                
            TOKEN().getNextToken()
            if(token.Name=='='):
                TOKEN().getNextToken()
                E_reg=self.E()
                gen('store',E_reg,idname,None)
            else:
                exit("ERROR:ASSGIN.S")
        else:
            exit("ERROR:ASSGIN.S")
        
        TOKEN().getNextToken()
        if(token.Name==';'):
            pass
        else:
            exit("ERROR:ASSGIN.S")

    def E(self):
        if(debug):
            print('E->',token.Name)
        neg=0
        if(token.Name in ADDOPR):
            
            if(token.Name=='-'):
                neg=1
            TOKEN().getNextToken()
        T_reg=self.T()
        E1_val=T_reg
        TOKEN().getNextToken()
        E1_reg=self.E1(E1_val)
        E_reg=E1_reg
        
        if(neg):
            try:
                int(E_reg)
                E_reg='-'+E_reg
            except:
                gen('-',E_reg,'$zero',E_reg)

        return E_reg

    def E1(self,E1_val):
        if(debug):
            print('E1->',token.Name)

        if(token.Name in ADDOPR):
            opr = token.Name
            TOKEN().getNextToken()
            T_reg=self.T()

            E2_val=T_reg
            E2_reg=getRegt(-1)
            gen(opr,E2_reg,E1_val,T_reg)
            
            E2_val=E2_reg

            TOKEN().getNextToken()
            E2_reg=self.E1(E2_val)
            E1_reg=E2_reg

            return E1_reg
        else:
            E1_reg = E1_val
            TOKEN().tokenBack()
            return E1_reg

    def T(self):
        if(debug):
            print('T->',token.Name)

        Fval=self.F()
        TOKEN().getNextToken()
        T1_val=Fval
        T1_reg=self.T1(T1_val)  
        T_reg=T1_reg

        return T_reg

    def T1(self,T1_val):
        if(debug):
            print('T1->',token.Name)
        

        if(token.Name in MULOPR):
            opr = token.Name
            TOKEN().getNextToken()
            Fval=self.F()
            
            T2_reg = getRegt(-1)
            gen(opr,T2_reg,T1_val,Fval)
            
            T2_val=T2_reg

            TOKEN().getNextToken()
            T2_reg=self.T1(T2_val)
            T1_reg=T2_reg
            return T1_reg
        else:
            T1_reg = T1_val
            TOKEN().tokenBack()
            return T1_reg

    def F(self):
        if(debug):
            print('F->',token.Name)


        if(token.Type==FUNC_CALL):
            FUNC().CALL()
            temp_reg=getRegt(-1)
            gen('=',temp_reg,'$v0')
            REG_USED.add(temp_reg)
            
            return temp_reg
        elif(token.Type=="VAL" and token.nextToken().Name=='['):
            idname=token.Name
            address_reg=ASSIGN().A()
            address='0('+address_reg+')'

            temp_reg=getRegt(1)
            gen('load',temp_reg,address,None)
            REG_USED.add(temp_reg)

            if(idname in LOCAL_VALTABLE.keys()):
                LOCAL_VALTABLE[idname]['reg']=temp_reg
            else:
                WHOLE_VALTABLE[idname]['reg']=temp_reg
                

            return temp_reg

        elif(token.Type=="VAL"):
            idname=judgeVAL(token.Name)
            temp_reg=getRegt(1)
            gen('load',temp_reg,idname,None)
            REG_USED.add(temp_reg)
            
            if(idname==token.Name):
                WHOLE_VALTABLE[token.Name]['reg']=temp_reg
            else:
                LOCAL_VALTABLE[token.Name]['reg']=temp_reg
            Fval = temp_reg
            return Fval
        elif(token.Type=='DIGIT'):
            Fval = token.Name
            return Fval
        elif(token.Name=='('):
            TOKEN().getNextToken()
            E_reg = self.E()
            F_val = E_reg
            TOKEN().getNextToken()
            if(token.Name==')'):
                return F_val
            else:
                exit('expect )')
        else:
            exit('variable:'+token.Name+' no es legal')
    
    def A(self):
        arrayname=token.Name

        TOKEN().getNextToken()
        if(token.Name!='['):
            exit("array:"+arrayname+"expect [")

        TOKEN().getNextToken()
        E_reg=self.E()

        TOKEN().getNextToken()
        if(token.Name!=']'):
            exit("array:"+arrayname+"expect ]")
                
        addres_reg=judgeVAL(arrayname,E_reg)
        return addres_reg

class DECLARE:
    def D(self,t):
        initVal='0'
        

        T_type=self.T()
        TOKEN().getNextToken()
        res=[]
        while(1):
            isArray=0
            if(token.Type!='VAL'):
                exit("declare:not val or array")
            idname = token.Name

            if(idname in WHOLE_VALTABLE.keys() or idname in LOCAL_VALTABLE.keys()):
                exit("val:"+idname+" already declared")

            if(ISBRANCH):
                exit("declare val:"+idname+" can't declare in branch")
            
            
            TOKEN().getNextToken()
            if(token.Name=='['):
                TOKEN().getNextToken()
                if(token.Type!='DIGIT' and token.Name!='0'):
                    exit("array declare:size of array must be a digit")
                arraySize=int(token.Name)
                TOKEN().getNextToken()
                if(token.Name!=']'):
                    exit("array declare:expect ]")
                TOKEN().getNextToken()
                isArray=1
            elif(token.Name=='='):
                TOKEN().getNextToken()
                
                if(t==1):
                    if(token.Type=='DIGIT'):
                        initVal=token.Name
                        TOKEN().getNextToken()
                    else:
                        exit('whole declare assign must be digit')
                else:
                    initVal=ASSIGN().E()
                    TOKEN().getNextToken()
            if(isArray):
                res.append((T_type,initVal,idname,arraySize))  
            else:    
                res.append((T_type,initVal,idname,0))
            
            if(token.Name==';'):
                break
            elif(token.Name==','):
                TOKEN().getNextToken()
            else:
                exit('declaracion mala')

        return res

    def LD(self):
        res=self.D(0)

        global stack_offset
        for T_type,initVal,idname,arraySize in res:
            if(idname in LOCAL_VALTABLE.keys()):
                exit("la declaracion:"+idname+" ya ha sido declarado")
            if(arraySize):
                LOCAL_VALTABLE[idname]={'type':T_type,'width':4*arraySize,'offset':str(stack_offset),'value':None,'reg':None,'const':ISCONST,'array':True}
                gen('newstack',arraySize)
                stack_offset-=4*arraySize
            else:
                LOCAL_VALTABLE[idname]={'type':T_type,'width':4,'offset':str(stack_offset),'value':initVal,'reg':None,'const':ISCONST,'array':False}
                gen('push',initVal)
                stack_offset-=4
    
    def WD(self):
        res=self.D(1)

        for T_type,initVal,idname,arraySize in res:
            if(idname in WHOLE_VALTABLE.keys()):
                exit("declare:"+idname+" has been already declared")
            if(arraySize):
                WHOLE_VALTABLE[idname]={'type':T_type,'width':4*arraySize,'value':None,'reg':None,'const':ISCONST,'array':True}
            else:
                WHOLE_VALTABLE[idname]={'type':T_type,'width':4,'value':initVal,'reg':None,'const':ISCONST,'array':False}
        
            

    def T(self):
        if(token.Type=='TYPE'):
            if(token.Name=='int'):
                T_type='int'
                return T_type
        else:
            exit("declare:wrong KEY")
    
    def param_list(self):
        index=0
        temp_valtable={}
        if(token.Name!='('):
            exit('param_declare list falta (')
        TOKEN().getNextToken()
        while(1):
            global ISCONST
            if(token.Name=='const'):
                ISCONST=True
                TOKEN().getNextToken()
            if(token.Type=='TYPE'):
                temp_type=token.Name
            elif(token.Name==')'):
                return temp_valtable,index
                break
            else:
                exit('param_declare TYPE wrong')
            TOKEN().getNextToken()
            if(token.Type=='VAL'):
                temp_valtable[token.Name]={'type':temp_type,'width':4,'offset':str(8+4*index),'reg':None,'const':ISCONST,'array':False}
                index=index+1
                ISCONST=False
            else:
                exit('param_declare not VAL')
            
            TOKEN().getNextToken()
            if(token.Name==','):
                TOKEN().getNextToken()
            elif(token.Name==')'):
                return temp_valtable,index
                break
            else:
                exit('param_declare BOUND wrong')

class SYSTEMCALL:
    def S(self):
        opr = token.Name
        TOKEN().getNextToken()
        if(token.Name!='('):
            exit('expect (')
        TOKEN().getNextToken()
        if(opr=='scanf'):
            idname=judgeVAL(token.Name)
            gen(opr,idname)
        else:
            if(token.Type=='STRING'):
                name=newStringName()
                WHOLE_STRING[name]=token.Name
                gen(opr,name,'string')
            else:
                E_reg=ASSIGN().E()
                gen(opr,E_reg,'val')

        TOKEN().getNextToken()
        if(token.Name!=')'):
            exit('expect )')
        TOKEN().getNextToken()
        if(token.Name!=';'):
            exit('expect ;')

class IF:
    def S(self,S_next):
        TOKEN().getNextToken()
        if(token.Name!='('):
            exit('if:expect (')

        TOKEN().getNextToken()
        B_true=newLable()
        B_false=S1_next=S_next
        self.B(B_true,B_false)
        gen('label',B_true)

        TOKEN().getNextToken()
        if(token.Name!=')'):
            exit('if:expect )')

        TOKEN().getNextToken()
        if(token.Name!='{'):
            PROGRAM().single_S(S1_next)
            gen('label',S_next)
            
        else:
            TOKEN().getNextToken()
            PROGRAM().multi_S()
            gen('label',S_next)

            TOKEN().getNextToken()
            if(token.Name!='}'):
                exit('if:expect }')

    def S_else(self,S_next):
        TOKEN().getNextToken()
        if(token.Name!='('):
            exit('if:expect (')

        TOKEN().getNextToken()
        B_true=newLable()
        B_false=newLable()
        S1_next=S2_next=S_next
        self.B(B_true,B_false)
        gen('label',B_true)

        TOKEN().getNextToken()
        if(token.Name!=')'):
            exit('if:expect )')

        TOKEN().getNextToken()
        if(token.Name!='{'):
            PROGRAM().single_S(S1_next)

        else:
            TOKEN().getNextToken()
            PROGRAM().multi_S()

            TOKEN().getNextToken()
            if(token.Name!='}'):
                exit('if:expect }')
        
        TOKEN().getNextToken()
        if(token.Name!='else'):
            exit('if:expect else')
        
        TOKEN().getNextToken()
        gen('goto',S_next)
        gen('label',B_false)
        if(token.Name!='{'):
            PROGRAM().single_S(S2_next)
            gen('label',S_next)
            
        else:
            TOKEN().getNextToken()
            PROGRAM().multi_S()
            gen('label',S_next)

            TOKEN().getNextToken()
            if(token.Name!='}'):
                exit('if:expect }')


    def B(self,B_true,B_false):
        if(debug):
            print('B->',token.Name)
        E1_reg=ASSIGN().E()

        TOKEN().getNextToken()

        print(token.Name)
        if(token.Name in COMPOPR):
            cmp=token.Name
        else:
            exit('BOOL:no es un cmp opr')

        TOKEN().getNextToken()
        E2_reg=ASSIGN().E()
        gen(cmp,B_true,E1_reg,E2_reg)
        gen('goto',B_false)
    
    def isHaveElse(self):
        p=point_token

        while(tokens[p].Name!=')'):
            p+=1
        if(tokens[p+1].Name=='{'):
            seen=0
            times=0
            for p in range(point_token,len(tokens)):
                now_token=tokens[p]
                if(now_token.Name=='{'):
                    seen=1
                    times+=1
                elif(now_token.Name=='}'):
                    times-=1
                if(seen==1 and times==0):
                    try:
                        if(tokens[p+1].Name=='else'):
                            return True
                        else:
                            return False
                    except:
                        pass
            return False
        else:
            while(1):
                idname=tokens[p].Name
                if(idname=='if'):
                    return False
                if(idname=='else'):
                    return True
                p+=1
                if(p>=len(tokens)):
                    return False

class LOOP:
    def W(self,S_next):
        TOKEN().getNextToken()
        if(token.Name!='('):
            exit('if:expect (')

        TOKEN().getNextToken()
        begin=newLable()
        B_true=newLable()
        B_false=S_next
        S1_next=begin
        gen('label',begin)
        IF().B(B_true,B_false)

        TOKEN().getNextToken()
        if(token.Name!=')'):
            exit('if:expect )')

        TOKEN().getNextToken()
        if(token.Name!='{'):
            exit('if:expect {')

        TOKEN().getNextToken()
        gen('label',B_true)
        PROGRAM().multi_S()
        
        gen('goto',begin)
        gen('label',S_next)

        TOKEN().getNextToken()
        if(token.Name!='}'):
            exit('if:expect }')
    
    
class FUNC:
    def CALL(self):
        if(token.Type==FUNC_CALL):
            Fname=token.Name
        else:
            exit("LLAMO AL NOMBRE INCORRECTO")
        
        TOKEN().getNextToken()
        if(token.Name!='('):
            exit("LLAMAR FALTA (")
        
        TOKEN().getNextToken()
        nums=0
        stack=[]
        if(token.Name!=')'):
            while(1):
                E_reg=ASSIGN().E()
                stack.append(E_reg)
                nums+=1

                TOKEN().getNextToken()
                if(token.Name==')'):
                    break
                elif(token.Name==','):
                    TOKEN().getNextToken()
        
        if(FUNCTABLE[Fname]['param_num']!=nums):
            exit('func:'+Fname+' param_num not match')
        p=[i for i in REG_USED if i not in stack]
        gen('protect',p)
        
        stack.reverse()
        gen('protect',stack)
        
        gen('call',Fname)

        gen('free',len(stack))
        p.reverse()
        gen('free',p)
    
    def RETURN(self):
        TOKEN().getNextToken()
        if(token.Name==';'):
            if(FUNCTABLE[NOWFUNC]['return_type']=='void'):
                gen('return',None)
            else:
                exit('func necesita retornar val')
        else:
            if(FUNCTABLE[NOWFUNC]['return_type']=='int'):
                E_reg=ASSIGN().E()
                gen('return',E_reg)
                TOKEN().getNextToken()
                if(token.Name!=';'):
                    exit('expect ;')
            else:
                exit('void func return int')
    
class PROGRAM:
    def P(self):
        self.whole_declare()
        while(1):
            if(self.func_declare()==-1):
                break
        self.void_main()

    def func_declare(self):
        init_func()
        if(token.Type!='TYPE'):
            exit('func declare INCORRECTO')
        if(token.nextToken().Name=='main'):
            return -1
        ret_type=token.Name

        TOKEN().getNextToken()
        if(token.Type!=FUNC_DECLARE):
            exit('nombre de la func no\'t existe')
        Fname=token.Name

        TOKEN().getNextToken()
        global LOCAL_VALTABLE,NOWFUNC
        LOCAL_VALTABLE,param_num=DECLARE().param_list()
        FUNCTABLE[Fname]['param_num']=param_num
        NOWFUNC=Fname

        TOKEN().getNextToken()
        if(token.Name!='{'):
            exit('func:'+Fname+' falta {')
        
        TOKEN().getNextToken()
        func_head(Fname)

        self.multi_S()
        func_end()
        TOKEN().getNextToken()
        if(token.Name!='}'):
            exit('main func falta {')
        TOKEN().getNextToken()

    def whole_declare(self):
        while(1):
            global ISCONST
            if(token.Name=='const'):
                ISCONST=True
                if(token.nextToken().Name not in TYPE):
                    exit("Const debe ser seguido por una declaracion")
            elif(token.Name in TYPE):
                if(token.nextToken().Type==FUNC_DECLARE):
                    print('whole_declare end')
                    break
                DECLARE().WD()
                ISCONST=False
            else:
                exit('whole_declare wrong')
        
            if(point_token<len(tokens)):
                TOKEN().getNextToken()
            else:
                exit('lack main func')

    def void_main(self):
        init_func()
        if(token.Name!='void'):
            exit('main debe estar vacío')
        TOKEN().getNextToken()
        if(token.Name!='main'):
            exit('nombre de func main incorrecto')

        TOKEN().getNextToken()
        global LOCAL_VALTABLE,NOWFUNC
        LOCAL_VALTABLE,param_num=DECLARE().param_list()
        FUNCTABLE['main']['param_num']=param_num
        NOWFUNC='main'

        TOKEN().getNextToken()
        if(token.Name!='{'):
            exit('main func falta {')
        TOKEN().getNextToken()

        func_head('main')
        
        self.multi_S()

        TOKEN().getNextToken()
        if(token.Name!='}'):
            exit('main func falta {')

    def multi_S(self):
        if(debug):
            print('P->',token.Name)
        while(1):
            S_next=newLable()
            self.S(S_next)
            gen('label',S_next)
            
            if(point_token<len(tokens)):
                TOKEN().getNextToken()
                if(token.Name=='}'):
                    TOKEN().tokenBack()
                    break
            else:
                break
        
    
    def S(self,S_next):
        if(debug):
            print('S->',token.Name)
        init_sentence()

        global ISBRANCH
        if(token.Name=='if'):
            ISBRANCH=True
            i = IF()
            if(i.isHaveElse()):
                i.S_else(S_next)
            else:
                i.S(S_next)
            ISBRANCH=False

        
        elif(token.Name=='while'):
            ISBRANCH=True
            LOOP().W(S_next)
            ISBRANCH=False

        else:
            while(1):
                global ISCONST
                init_sentence()
                if(token.Name=='return'):
                    FUNC().RETURN()
                
                elif(token.Type==FUNC_CALL):
                    FUNC().CALL()

                elif(token.Name=='const'):
                    ISCONST=True
                    if(token.nextToken().Name not in TYPE):
                        exit("const debe ser seguido por una declaracion")

                elif(token.Name in TYPE):
                    DECLARE().LD()
                    ISCONST=False

                elif(token.Type=='SYSCALL'):
                    SYSTEMCALL().S()

                elif(token.Type=='VAL'):
                    ASSIGN().S()

                if(point_token<len(tokens)):
                    TOKEN().getNextToken()
                    if(token.Name in ['}','if','while','return']):
                        TOKEN().tokenBack()
                        break
                else:
                    break
    
    def single_S(self,S_next):
        if(debug):
            print('S->',token.Name)
        init_sentence()

        global ISBRANCH
        if(token.Name=='if'):
            ISBRANCH=True
            i = IF()
            if(i.isHaveElse()):
                i.S_else(S_next)
            else:
                i.S(S_next)
            ISBRANCH=False

        
        elif(token.Name=='while'):
            ISBRANCH=True
            LOOP().W(S_next)
            ISBRANCH=False

        else:
            global ISCONST
            if(token.Name=='return'):
                FUNC().RETURN()

            elif(token.Type==FUNC_CALL):
                FUNC().CALL()

            elif(token.Name=='const'):
                ISCONST=True
                if(token.nextToken().Name not in TYPE):
                    exit("Const debe ser seguido por una declaracion")

            elif(token.Name in TYPE):
                DECLARE().LD()
                ISCONST=False

            elif(token.Type=='SYSCALL'):
                SYSTEMCALL().S()
            elif(token.Type=='VAL'):
                ASSIGN().S()
token_exprs = [
    (r'[ \n\t]+',              "ESPACE"),
    (r'\(',                    "("),
    (r'\)',                    ")"),
    (r'\}',                    "}"),
    (r'\{',                    "{"),
    (r';',                     ";"),
    (r',',                     ","),
    (r'\+',                    "+"),
    (r'-',                     "-"),
    (r'\*',                    "*"),
    (r'/',                     "/"),
    (r'<=',                    "<="),
    (r'<',                     "<"),
    (r'>=',                    ">="),
    (r'>',                     ">"),
    (r'!=',                    "!="),
    (r'=',                     "="),
    (r'!',                     "!"),
    (r'and',                   "and"),
    (r'or',                    "or"),
    (r'not',                   "not"),
    (r'if',                    "if"),
    (r'then',                  "them"),
    (r'else',                  "else"),
    (r'while',                 "while"),
    (r'int',                 "int"),
    (r'float',                 "float"),
    (r'char',                 "char"),
    (r'void',                 "void"),
    (r'return',                 "return"),
    (r'print',                 "print"),
    (r'call',                 "call"),
    (r'[0-9]+',                "IDN"),
    (r'[A-Za-z][A-Za-z0-9_]*', "IDN"),
    (r'\"[A-Za-z0-9_\n \t]*\"', "IDNs"),
]

def lex(characters, token_exprs):
    pos = 0
    tokens = []
    line = 1
    while pos < len(characters):
        match = None
        for token_expr in token_exprs:
            pattern, tag = token_expr
            regex = re.compile(pattern)
            match = regex.match(characters, pos)
            if match:
                text = match.group(0)
                if tag:
 
                        token = (text, tag , line)
                        tokens.append(token)
                        if text=='\n ':
                            line = line + 1
                break
        if not match:
            print("ERROR EN CARACTER: "  +characters[pos]+ " en " + str(pos))
            sys.exit(1)
        else:
            pos = match.end(0)
    return tokens

    
def imprimir (tokens):
    with open("datos.js", "w") as work_data:
        work_data.write('var datos=[')
        work_data.write('\n')
        for x in tokens:
                if x[1]=='ESPACE':
                    continue
                if x[1]=='IDNs':
                    stri='{ \"text\": \"'+'IDN'+'\",\"tag\": \"'+'IDN'+'\",\"line\":\"'+str(x[2])+'\"},'
                else:      
                    stri='{ \"text\": \"'+x[0]+'\",\"tag\": \"'+x[1]+'\",\"line\":\"'+str(x[2])+'\"},'
                work_data.write(repr(stri))
                work_data.write("\n")
        work_data.write(']')
        work_data.write("\n")

if __name__=="__main__":
    file = argv[1]
    with open(file,'r') as f:
        s=f.read()
    tokensy = lex(s, token_exprs)
    s=s.replace('call', ' ')
    TOKEN().getTokens(s)
    
    imprimir(tokensy) 
    if(tokens[-1].Name!=';' and tokens[-1].Name!='}'):
        exit('expect Last BOUND')
    TOKEN().getNextToken()
    PROGRAM().P()
    seg_show(file)
