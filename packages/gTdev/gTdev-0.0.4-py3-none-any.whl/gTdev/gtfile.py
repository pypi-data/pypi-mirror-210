
import os
import numpy as np
import pandas

class curve():
    def __init__(self,x,y,name='',info = {}):
        self.name = name
        self.x = x
        self.y = y
        self.info = info
        self.curve = (self.x,self.y)
    def __str__(self):
        return str(self.curve)

class gtfile():
    def __init__(self,key='.xls',location='./',X_Axis='GateV',Y_Axis="DrainI",absY=True):
        self.key=key
        self.location = location
        
        self.X_Axis = X_Axis
        self.Y_Axis = Y_Axis

        self.files = set()
        
        self.curves = []
        
        self.filterFile()
        self.getcurves(absY)

    def filterFile(self):
        for f  in os.listdir(self.location):
            if self.key in f:
                self.files.add(f)

    def axis2d(self, df, absY=True):
        try:
            x=list(df[self.X_Axis])
            if absY:
                y=np.abs(list(df[self.Y_Axis]))
            else:
                y=list(df[self.Y_Axis])
            return x,y
        except:
            return (None,None)


    def getcurves(self, absY=True):
        for file in self.files:
            dataforms = pandas.read_excel(
                os.path.join(self.location,file),
                sheet_name=None)

            sheets = list(dataforms.keys())
            for sht in sheets:
                if sht == 'Data' or 'Append' in sht:
                    x, y = self.axis2d(dataforms[sht],absY)
                    self.curves.append(curve(x,y,sht))


