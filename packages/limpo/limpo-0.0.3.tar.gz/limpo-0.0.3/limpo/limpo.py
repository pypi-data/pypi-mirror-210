import pandas as pd
import numpy as np
  
class Table:
  def __init__(self, dataframe: pd.DataFrame()):
    self.dataframe = dataframe
    self.records = len(self.dataframe)
    self.column_names = self.dataframe.columns

  def find_null_values(self):
        dic = {}

        for col in self.column_names:
            missing = self.dataframe[col].isnull()
            num_missing = np.sum(missing)
            
            if num_missing > 0:
                dic.update({col: num_missing} )

        result = pd.DataFrame.from_dict(dic, orient ='index').reset_index()
        result = result.rename(columns={0: 'null_values','index':'column'})
        result["perc_null_values"] = result["null_values"] / self.records
        result = result.sort_values('perc_null_values', ascending=False)

        return print(result)
  
  def find_duplicates(self, columns: list):
        # find way to ignore null values
        dic = {}

        for col in self.column_names:
            unique_values = len(self.dataframe[col].unique())
            dic.update({col: unique_values} )

        result = pd.DataFrame.from_dict(dic, orient ='index').reset_index()
        result = result.rename(columns={0: 'unique_values','index':'column'})
        result["duplicates"] =  self.records - result["unique_values"] 
        result["perc_duplicates"] = result["duplicates"] / self.records

        return print(result)    
