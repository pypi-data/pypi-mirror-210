from ase.io import read
import os
import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def curvef(loc,polymer,start,end,savefig,savedata,xx=False):
    opath=os.getcwd()
    try:
        f=open(loc+'{0}_Result.txt'.format(polymer),'x')
    except:
        f=open(loc+'{0}_Result.txt'.format(polymer),'w')
    
    f.write('Strain Length(%),Stress Force(nN)\n')

    res = []
    for path in os.listdir(loc):
        if os.path.isfile(os.path.join(loc, path)):
            a=re.match(polymer+'_', path)
            if a:
                b=re.search('.xyz',path)
                if b:
                    c=re.search('trj',path)
                    if c:
                        continue
                    res.append(path)
    print(res)
    res.sort()
    os.chdir(loc)
    
    try:
        atoms=read('{0}_0.000.xyz'.format(polymer))
    except:
        atoms=read('{0}_0.xyz'.format(polymer))
    x=atoms.get_distance(start,end)
    
    for data in res:
        atoms=read(data)
        strain=re.search(r'_[0-9]+\.*[0-9]*',data)
        f.write('{0:.5f},{1}\n'.format(atoms.get_distance(start,end)/x,strain.group(0)[1:]))
        y=atoms.get_distance(start,end)
    f.close()

    datum=pd.read_csv('{0}_Result.txt'.format(polymer))
    datum=datum[:].sort_values(by=['Strain Length(%)']) #Sort document
    datum=datum[:-1]
    print(datum)
    if xx==False:
        a=sns.scatterplot(data=datum, x=datum['Strain Length(%)'],y=datum['Stress Force(nN)'],color='black',alpha=0.5)
        a.plot(datum['Strain Length(%)'],datum['Stress Force(nN)'])
        plt.xlabel('Strain Length(%)')
        plt.ylabel('Stress Force(nN)')
        _=plt.title('Strain-Stress Curve')
    if savefig==True:
        plt.savefig('{0}.png'.format(polymer),bbox_inches='tight')
    if xx==False:
        plt.show()
    if savedata==False:
        os.system('rm {0}_Result.txt'.format(polymer))
    os.chdir(opath)
    
class single:
    """
    The definition of polymer.
    single(polymer, loc='./')
    polymer: Your polymer name on your file.
    loc: File Location. The default is your current location.
    You can get the further information by .curve and .autocurve.
    """
    def __init__(self, polymer, loc='./'):
        self.loc=loc
        self.polymer=polymer

    def curve(self,start,end,savefig=True,savedata=True,xx=False):
        """
    The method to create a single polymer chart of Stress-Strain Curve and .txt relevant data file of stress and strain.
    curve(start, end, savefig=True, savedata=True)
    start, end: the beginning and end side of the polymer, mostly two sides imposing external force.
    savefig, savedata: To show if you want to save the chart and .txt curve. The default is True.
    The output of this file is a Stress-Strain Curve chart and relevant data.
    Example:
        Input:
            from MCPoly.sscurve import single
                poly1=single('Polymer1')
                poly1.curve(0,6)
        Output:
            ['Polymer1_2.0.xyz', 'Polymer1_0.0.xyz', 'Polymer1_0.5.xyz', 'Polymer1_2.5.xyz', 
             'Polymer1_1.0.xyz', 'Polymer1_3.0.xyz', 'Polymer1_1.5.xyz'] -> All your files
                  Strain Length(%)  Stress Force(nN)
                0           1.00000               0.0
                1           1.06778               0.5
                2           1.13094               1.0
                3           1.19338               1.5
                4           1.24726               2.0
                5           1.31094               2.5
            <matplotlib chart>
    TIPS: Make sure all your .xyz file is in the current location, or the chart may have some mistakes.
        """
        return curvef(self.loc,self.polymer,start,end,savefig,savedata,xx)
    
    def autocurve(self,savefig=True,savedata=True,xx=False):
        """
    The method to create a single polymer chart of Stress-Strain Curve and .txt relevant data file of stress and strain the same as function curve. but it can be more handy if there are some .out or .inp files. 
    autocurve(savefig=True, savedata=True)
    savefig, savedata: To show if you want to save the chart and .txt curve. The default is True.
    The output of this file is a Stress-Strain Curve chart and relevant data.
    Example:
        Input:
            from MCPoly.sscurve import single
                poly1=single('Polymer1')
                poly1.autocurve()
        Output:
            ['Polymer1_2.0.xyz', 'Polymer1_0.0.xyz', 'Polymer1_0.5.xyz', 'Polymer1_2.5.xyz', 
             'Polymer1_1.0.xyz', 'Polymer1_3.0.xyz', 'Polymer1_1.5.xyz']
                  Strain Length(%)  Stress Force(nN)
                0           1.00000               0.0
                1           1.06778               0.5
                2           1.13094               1.0
                3           1.19338               1.5
                4           1.24726               2.0
                5           1.31094               2.5
            <matplotlib chart>
    TIPS: Make sure all your .xyz file is in the current location, or the chart may have some mistakes.
          Make sure there is at least one .out or .inp file of relevant polymer here, or it will show FileNotFoundError.
        """
        t=0
        for path in os.listdir(self.loc):
            if os.path.isfile(os.path.join(self.loc, path)):
                a=re.match(self.polymer+'_', path)
                if a:
                    b=re.search('.inp',path)
                    if b:
                        t=1
                        break
                    c=re.search('.out',path)
                    if c:
                        t=2
                        break
        if t==0:
            raise FileNotFoundError('relevant .inp and .out file is not found. Try to find out the file and put it in this document.')
        else:
            opath=os.getcwd()
            os.chdir(self.loc)
            f=open(path,'r')
            i=0
            start=-1
            end=-1
            if t==1:
                for line in f:
                    if i==1:
                        num=re.findall(r'[0-9]+',line)
                        start=eval(num[0])
                        end=eval(num[1])
                        break
                    a=re.search('POTENTIALS',line)
                    if a:
                        i=i+1
            if t==2:
                for line in f:
                    if i==1:
                        num=re.findall(r'[0-9]+',line)
                        start=eval(num[1])
                        end=eval(num[2])
                        break
                    a=re.search('> POTENTIALS',line)
                    if a:
                        i=i+1
            os.chdir(opath)
        return curvef(self.loc,self.polymer,start,end,savefig,savedata,xx)