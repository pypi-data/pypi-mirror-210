class StringTokenizer:
    def __init__(self,st,delim=' \t\n\r\f',retdelim=False):
        if type(retdelim)!=bool:
            raise TypeError("Expected <class 'bool'> received "+str(type(retdelim)))
        self.__tokens=list(st)
        try:
            self.__delim=tuple(self.__flatten__(delim))
        except Exception:
            raise TypeError('Invalid Delimeter Group')
        self.__retdelim=retdelim
    def nextToken(self,delim=None):
        if delim==None:
            delim=self.__delim
        else:
            try:
                delim=tuple(self.__flatten__(delim))
            except Exception:
                raise TypeError('Invalid Delimeter Group')
            self.__delim=delim
        temp=''
        while len(self.__tokens)>0:
            if temp=='' and self.__tokens[0] in delim:
                if self.__retdelim:
                    temp=self.__tokens[0]
                    del self.__tokens[0]
                    break
                else:
                    del self.__tokens[0]
            elif self.__tokens[0] in delim:
                if not self.__retdelim:
                    del self.__tokens[0]
                break
            else:
                temp+=self.__tokens[0]
                del self.__tokens[0]
        if temp:
            return temp
        else:
            raise ValueError('No Such Element Exists')
    def hasMoreTokens(self):
        temp=list(self.__tokens)
        r=True
        try:
            self.nextToken()
            self.__tokens=temp
        except Exception:
            r=False
        return r
    def countTokens(self):
        c=0
        temp=list(self.__tokens)
        try:
            while True:
                self.nextToken()
                c+=1
        except Exception:
            pass
        self.__tokens=temp
        return c
    def __flatten__(self,d):
    	t=list(d)
    	if type(d)==str:
    	    return t
    	nd=[]
    	for i in t:
    		if len(i)==0:
    			...
    		elif type(i)!=str:
    			nd.extend(self.__flatten__(i))
    		else:
    			nd.extend(list(i))
    	return nd
