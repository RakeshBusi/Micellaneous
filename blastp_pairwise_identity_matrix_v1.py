import subprocess
import time
import pandas as pd
from collections import defaultdict
import copy
from itertools import combinations_with_replacement,combinations
import sys

filename=sys.argv[1]
prtns=filename.split('.')[0]
class per_ident:
    def __init__(self,file):
        self.acc,self.seq=[],[]
        with open(file,'r') as inpt:
            for i in inpt:
                if i.startswith('>'):
                    self.acc.append(i)
                else:
                    self.seq.append(i)
                    
    def create_files(self):
        total_data=[]
        for i in range(len(self.acc)):
            main_out=open('main_temp.txt','w')
            main_out.write(self.acc[i]+self.seq[i])
            main_out.close()
            for j in range(i+1,len(self.acc)):
                out=open('temp.txt','w')
                out.write(self.acc[j]+self.seq[j])
                out.close()
                data=self.blast('main_temp.txt','temp.txt')
                if data==[]:
                    data=['\t'.join([self.acc[i].rstrip().split(' ')[0][1:],self.acc[j].rstrip().split(' ')[0][1:],'0','0','0'])]# change the number of 0 based on number parameters taken
                total_data.extend(data)
        final_out=open(f'{prtns}_pairwise_blastp.txt','w')
        for k in total_data:
            final_out.write(k+'\n')
        final_out.close()
        
    def blast(self,file1,file2):
        data=[]
        subprocess.run(f' blastp -query {file1} -subject {file2} -outfmt "6 qseqid sseqid pident qcovs qcovhsp" -out result.txt',
               shell=True,stdout=subprocess.PIPE,check=True,universal_newlines=True)
        with open('result.txt','r') as inpt:
            for i in inpt:
                data.append(i.rstrip())
        return data
    
class pairwise_matrix:
    def __init__(self,file3):
        self.temp=[]
        self.multi_hit=defaultdict(list)
        with open(file3,'r') as inpt:
            for i in inpt:
                j=i.rstrip().split('\t')
                name=j[0]+'&'+j[1]
                self.temp.append(j)
                self.multi_hit[name].append([float(fl_i) for fl_i in j[2:]])
    def matrix(self,typ,pi,qc):
        self.collect=defaultdict(list)
        for i,j in dict(self.multi_hit).items():
            j=sorted(j,key=lambda x:x[-1], reverse= True)
            j=j[0] # hsp with high query coverage is taken
            if j[0]>=pi and j[-1]>=qc: # pi=percentage identity and qc=query coverage
                j_1=j
            else:
                j_1=[0,0,0]
            i1=i.split('&')
            self.collect[i1[0]].append(j_1[0])
        self.collect[i1[1]]=[] # for the last accession number, eg 8&9 is last in list and we need 9.
        self.collect=dict(self.collect)
        le=len(self.collect)
        for k,l in self.collect.items():
            diff=le-len(l)
            tem=[]
            for m in range(diff):
                tem.append('-2')
            l=tem+l
            self.collect[k]=l
        df=pd.DataFrame(self.collect, index=self.collect.keys()).astype(float)
        label=[]
        for each in alpha.acc:
            tt=each.rstrip()[1:].split('$')[typ]
            label.append(tt)
        df.index=df.columns=label
        for ro_co in range(le):
            df.iloc[ro_co,ro_co]=-1
        dff=copy.copy(df.T)
        dff.to_excel(f'{prtns}_pariwise_blastp_matrix_{pi_cutoff}_{qc_cutoff}.xlsx')
        return dff.round(decimals=1)
    
class matrix_analysis:
    def __init__(self):
        self.uniq=[]
        self.each_len=[]
        for eaa in list(a.index):
            if eaa not in self.uniq:
                self.uniq.append(eaa)
#         self.uniq=['c','lalba']
#         self.uniq=['g','c','ch']
        self.name='_'.join(self.uniq)
        self.comb = list(combinations_with_replacement(self.uniq, 2))
        out=open(f'{prtns}_compare_pair_identity_{pi_cutoff}_{qc_cutoff}.txt','w')
        self.dat={}
        for jj in self.comb:
            temp=jj[0]+','+jj[1]
        #     print(temp)
            self.dat[temp]=[]
            rl=len(a.index)
            cl=len(a.columns)
            for kk in range(rl):
                for ll in range(cl):
                    if kk+ll <rl:
                        if a.index[kk]==jj[0] and a.columns[kk+ll]==jj[1]:
                            self.dat[temp].append(float(a.iloc[kk,kk+ll]))
            hj=[xy for xy in list(self.dat[temp]) if xy != -1]
            hj.sort()
            self.dat[temp]=hj
            self.each_len.append(len(hj))
            temp1=12-len(temp)
            temp2=f'{hj[:5]}'[1:-1]
            temp21=36-len(temp2)
            temp3=f'{hj[-5:]}'[1:-1]
#             print(temp,' '*temp1,'min:',temp2,' '*temp21,'max:',temp3,'\n')
            out.write(temp+' '*temp1+'min: '+temp2+' '*temp21+'max: '+temp3+'\n')
        out.close()
        
    def overlapping(self):
        common={}
        stat={}
        cwr=list(combinations(self.uniq,2))
        for i in cwr:
            x=i[0]+','+i[1]
            y=i[0]+','+i[0]
            z=i[1]+','+i[1]
            for j in [y,z]:
                temp=[q for q in self.dat[x] if q>=min(self.dat[j])]
                common[f'{x}>{j}']=temp
                stat[f'{x}>{j}']=[len(self.dat[x]),len(self.dat[j]),min(self.dat[j]),len(temp)]
        dfuc=pd.DataFrame(stat,index=['no. hybrid(H)','no. identical(I)','min % I','H>I']).astype(int)
        dfuc.to_excel(f'{prtns}_per_ident_stat_{pi_cutoff}_{qc_cutoff}.xlsx')
        return common,dfuc
        
    def to_excel(self):
        graph_data=copy.copy(self.dat)
        for gh1,gh2 in graph_data.items():
            if max(self.each_len)>len(gh2):
                diff=(max(self.each_len)-len(gh2))*['']
                graph_data[gh1].extend(diff)
        df1=pd.DataFrame(graph_data)
        df1.to_excel(f'{prtns}_per_ident_plot_{pi_cutoff}_{qc_cutoff}.xlsx',index=False)

start=time.perf_counter()
pi_cutoff=0
qc_cutoff=80
alpha=per_ident(filename)
# alpha.create_files()
a=pairwise_matrix(f'{prtns}_pairwise_blastp.txt').matrix(1,pi_cutoff,qc_cutoff) # 0:'acc',1:'prtn',2:'ec',3:'org',4:'species',5:'ghf'
b=matrix_analysis()
c,c_stat=b.overlapping()
d=b.to_excel()
stop=time.perf_counter()
print('The total time take:',round((stop-start),2),'sec')