**This project is a python implementation of the StringTokenizer class present in java**


__How to import ?__

from stringtokenizer import StringTokenizer


__How to declare object?__

s1=StringTokenizer(st)-->uses default delimeter set

s2=StringTokenizer(st,delim)-->uses provided delim set. Uses each character present in provided delim string as delimeters

s3=StringTokenizer(st,delim,retdelim)-->same as no. 2 but returns delim as tokens depending on True/False of retdelim


__Functions Contained and how to use?__

s1=StringTokenizer(st)

s1.countTokens()-->returns number of tokens left to parse

s1.hasMoreTokens()-->returns True/False depending on wheather any more tokens are left to parse

s1.nextToken()-->returns next Token

s1.nextToken(delim)-->returns next token based on the provided delim and updates the previously provided delim with the new ones


**made by Tanmay Mandal**
for any query please mail on tanmay.mandal@zohomail.in
