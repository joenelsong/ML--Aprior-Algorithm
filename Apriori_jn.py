'''
# largely borrowed and modified from an old python2 version found here https://pypi.python.org/pypi/apriori/1.0.0

# Version: Python3.5

#Usage:
    Apriori FoodMart.csv 0.01 0.17

'''

import csv
import sys

def Read_CSV(fileName):
    ''' Rawdata[0] = IV labels
        Rawdata[1:rowCt] = data values
        Rawdata[::][end] = DV classification label
    '''
    head = 0
    Rawdata = [[]] # 2 dimensional list of each data record
    rowCt = 0
    with open(fileName, newline='') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            a_list = []
            for i in row:
                a_list.append(i)
            if (head == 1):
                Rawdata.append(a_list) # avoids appending to empty array and instead fils in first cell
                #print(a_list)
            else:
                Rawdata[0] = a_list
                head = 1
            rowCt += 1
    return Rawdata
    
def loadCSVDataSet(csv):
    LoadedData = [[]]
    for r in range (1, len(csv)-1):
        a_list = []
        for c in range( len(csv[0]) ):
            if ( csv[r][c] == "1" ):
                a_list.append(csv[0][c])
        LoadedData.append(a_list)
    return LoadedData
    #return [["1", "2","3", "4","6"], ["2", "3","4", "5","6"], ["1", "2", "3", "5","6"], ["1","2","4", "5","6"]]

def createC1(dataSet):
    C1 = []
    for transaction in dataSet:
        for item in transaction:
            if not [item] in C1:
                C1.append([item])            
    C1.sort()
    return list(map(frozenset, C1))#use frozen set so we
                            #can use it as a key in a dict    

def scanD(D, Ck, minSupport):
    ssCnt = {}
    for tid in D:
        for can in Ck:
            if can.issubset(tid):
                if not can in ssCnt: ssCnt[can]=1
                else: ssCnt[can] += 1
    numItems = float(len(D))
    retList = []
    supportData = {}
    for key in ssCnt:
        support = ssCnt[key]/numItems
        if support >= minSupport:
            retList.insert(0,key)
        supportData[key] = support
    return retList, supportData


def aprioriGen(Lk, k): #creates Ck
    retList = []
    lenLk = len(Lk)
    for i in range(lenLk):
        for j in range(i+1, lenLk): 
            L1 = list(Lk[i])[:k-2]; L2 = list(Lk[j])[:k-2]
            L1.sort(); L2.sort()
        #print "L1:",L1
        #print "L2:",L2
        #compare the first items to avoid duplicate
            if L1==L2: #if first k-2 elements are equal,namely,besides the last item,all the items of the two sets are the same!
                retList.append(Lk[i] | Lk[j]) #set union
    return retList

def apriori(dataSet, minSupport = 0.5):
    C1 = createC1(dataSet)
    D = list(map(set, dataSet))
    L1, supportData = scanD(D, C1, minSupport)
    L = [L1]
    k = 2
    while (len(L[k-2]) > 0):
        Ck = aprioriGen(L[k-2], k)
        Lk, supK = scanD(D, Ck, minSupport)#scan DB to get Lk
        supportData.update(supK)
        L.append(Lk)
        k += 1
    return L, supportData


def generateRules(L, supportData, minConf=0.7):  #supportData is a dict coming from scanD
    bigRuleList = []
    for i in range(1, len(L)):#only get the sets with two or more items
        for freqSet in L[i]:
            H1 = [frozenset([item]) for item in freqSet]
            if (i > 1):
                rulesFromConseq(freqSet, H1, supportData, bigRuleList, minConf)
            else:
                calcConf(freqSet, H1, supportData, bigRuleList, minConf)
    return bigRuleList         

def calcConf(freqSet, H, supportData, brl, minConf=0.7):
    prunedH = [] #create new list to return
    for conseq in H:
        conf = supportData[freqSet]/supportData[freqSet-conseq] #calc confidence
        if conf >= minConf: 
            print (freqSet-conseq,'-->',conseq,'conf:',conf)
            brl.append((freqSet-conseq, conseq, conf))
            prunedH.append(conseq)
    return prunedH

def rulesFromConseq(freqSet, H, supportData, brl, minConf=0.7):
    print ("freqSet:",freqSet)
    
    Hmp1=calcConf(freqSet, H, supportData, brl, minConf)
    
    m = len(Hmp1[0])
    print ("m:",m,"Hmp1 now:",Hmp1)
    if (len(freqSet) > (m + 1)): #try further merging
        Hmp1 = aprioriGen(Hmp1, m+1)#create Hm+1 new candidates
        print ('Hmp1:',Hmp1)
        Hmp1 = calcConf(freqSet, Hmp1, supportData, brl, minConf)
        print ('Hmp1 after calculate:',Hmp1)
        if (len(Hmp1) > 1):    #need at least two sets to merge
            rulesFromConseq(freqSet, Hmp1, supportData, brl, minConf)
            

if __name__ == "__main__":
    
    if (len(sys.argv) != 4):
        raise Exception("Incorrect number of arguments. correct usage: ./Apriori <CSV Data File Path> <support> <confidence>")
        
    data_file = sys.argv[1]
    support = sys.argv[2]
    confidence = sys.argv[3]
    
    #data_file = "FoodMart.csv"
    csvData = Read_CSV(data_file)
    dataSet=loadCSVDataSet(csvData)
    L,supportData=apriori(dataSet,float(support))
    brl=generateRules(L, supportData,float(confidence))
    print ('brl:',brl)