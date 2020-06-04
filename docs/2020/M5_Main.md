---
title: M5_MAIN
permalink: /2020/M5_Main
---
[Go Back](https://paulb86uk.github.io/PP_ART.github.io/)

## Up to the 4th of June of 2020

The M5 Competition...
The Strategy I choose:
The Planned Schedule:
The Metrics?
The Parts.
PartA: 
## Working on the File1...
### Working on the Column:::

The idea is to get some data to the final model:
#### Total Sales per day of every Store: 
Time Range Used: All

#### Code Explained:
First I used and transformed the MultishiftA function, from the multifeature code I built last month in order to check the [Bitcoin Price Prediction](https://medium.com/@PP_ART/time-series-forecasting-neural-networks-2ecd302a3e02). For this part of the M5 project the only feature I decided to use is the total sales per day, and per Store.

### [STORE] >>> [TOTAL SALES PER DAY]  [<04_05_2020]

So to start, we have to make the sum of the sales, after filtering one store:
```python
file1 = pd.read_csv("drive/My Drive/kaggle_reg/sales_train_validation.csv") 
dia = [] #list with day values
valor = [] #list with values
for i in file1[file1['cat_id'] == 'HOBBIES'].columns[6:]: 
  a = file1[file1['cat_id'] == 'HOBBIES'][i] 
  dia.append(i)
  valor.append(a.sum()) 
  a = 'asd' #
df_cat = pd.DataFrame(data = {'dia' : dia, 'valor' : valor}) 
df_cat['dia'] = df_cat['dia'].str.replace("d_","") #
df_cat['dia'] = df_cat['dia'].astype(int)  
mask = (df_cat['valor'] < 10) 
df_cat.loc[mask, 'valor'] = 0 
df_cat = df_cat.sort_values(ascending= True, by= ['valor','dia']) 
val_cat_train_inicio = df_cat.iloc[1,0] 
val_cat_train_final = df_cat.iloc[3,0] 
train = df_cat[(df_cat['dia'] > val_cat_train_inicio) & (df_cat['dia'] < val_cat_train_final)]
test = df_cat[df_cat['dia'] > val_cat_train_final] 
```

And then fix the MultishiftA function to shift the dataframe backwards. Only 27 steps, since the present is considered for the train, making a total of 28 steps for the training set.
```python
def MultishiftA(df, target):
  for i in range(1,28,1): 
    shift = df[target].shift(i)
    df['{}_t-{}'.format(col,i)] = shift 
  df2 = df.dropna() 
  df2 = df2.drop(columns=[target])
  df2[target] = df[target]
  return df2
 ```
 
 The next step in the transformation is to use the pandas shift function to the future, that will be the 28 steps test set for the model.
 ```python
 def MultishiftB(df,target):
    for j in range(1,29): #28 forward steps
      shift = df[target].shift(-j) 
      df['{}_t+{}'.format(target,j)] = shift 
      df = df.dropna()
    return df
  ```
 Now I had to split the data into train and test(model validation). To decide which portion of the data to use, I made a plot of the total sales of everyday, considering all the stores, to see the trends...
 
  I have to make a better graph, I now is bad, but helps to explain the idea.
  ![prueba](https://paulb86uk.github.io/PP_ART.github.io/2020/Total_Ventas.png)
  
  In the graph it can be clearly see the regions delimited by almost 0 sales days.
  So taking advantage of this fact, I decided to:
  -Dont use the first portion
  -Keep the 2nd and 3rd portion as train for the model.
  -Use the 4th and 5th portion as validation for the model.
 The following code segments the data following the idea explained.
 
 ```python
 def SegmentA(df,colval,colday):
  mask = (df[colval] < 10)
  df.loc[mask, colval] = 0
  df= df.sort_values(ascending= True, by= [colval,colday]) 
  val_cat_train_inicio = df.iloc[1,0]
  val_cat_train_final = df.iloc[3,0]
  train = df[(df[colday] > val_cat_train_inicio) & (df[colday] < val_cat_train_final)]
  test = df[df[colday] > val_cat_train_final]
  train = train.drop(columns=[colday])
  test = test.drop(columns=[colday])
  test = test.sort_index()
  train = train.sort_index()
  return train,test
 ```

