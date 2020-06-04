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

### [STORE] >>> [TOTAL SALES PER DAY]

So to start, we have to make the sum of the sales, after filtering one store:
```python
file1 = pd.read_csv("drive/My Drive/kaggle_reg/sales_train_validation.csv") #LOAD DATAFRAME
dia = [] #list with day values
valor = [] #list with values
for i in file1[file1['cat_id'] == 'HOBBIES'].columns[6:]: #before killing my small RAM(accept donations xD)
  a = file1[file1['cat_id'] == 'HOBBIES'][i] #I will work only with one category to verify all is working good
  dia.append(i)
  valor.append(a.sum()) #Here the sum of all the values of the day looped
  a = 'asd' #To take good care of my ram for this heavy project, I have to step on every asigned function to reduce size.

df_cat = pd.DataFrame(data = {'dia' : dia, 'valor' : valor}) #create the dataframe
df_cat['dia'] = df_cat['dia'].str.replace("d_","") #get rid of "d_"
df_cat['dia'] = df_cat['dia'].astype(int)  #Need int type column for the next steps.
mask = (df_cat['valor'] < 10) #I checked there is a good partition point on values close to Zero
df_cat.loc[mask, 'valor'] = 0 #Now they are zero xD
df_cat = df_cat.sort_values(ascending= True, by= ['valor','dia']) #asi asigno bien los cortes #ahora cada posicion indicado el valor que quiero.#This way I can order by value, and also by time, to be sure I made the correct splits.
val_cat_train_inicio = df_cat.iloc[1,0] #I get rid of the first data that not make sense, and make the start point for the train data
val_cat_train_final = df_cat.iloc[3,0] # the end point of the train data, and start of the test data
train = df_cat[(df_cat['dia'] > val_cat_train_inicio) & (df_cat['dia'] < val_cat_train_final)]
test = df_cat[df_cat['dia'] > val_cat_train_final] 
```

And then fix the MultishiftA function
```python
def MultishiftA(df,ide,target):
  for i in range(1,28,1):
    shift = df[target].shift(i)
    df['{}_t-{}'.format(col,i)] = shift
  df2 = df.dropna() #Can not leave NaN cells
  df2 = df2.drop(columns=[col])
  df2[target] = df[target] #this two steps is to locate the target in the middle.
  return df2
  
  
  ```
  
