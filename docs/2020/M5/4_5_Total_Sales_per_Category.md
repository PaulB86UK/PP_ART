---
title: Sales per Category per Day.
permalink: /2020/M5_Sales_per_Category_day
---
[Go Back](https://paulb86uk.github.io/PP_ART.github.io/)

## Up to the 4th of June of 2020
### [STORE] >>> [TOTAL SALES PER DAY]  [<04_05_2020]
#### Total Sales per day of every Category: 
Time Range Used: All

First I used and transformed the MultishiftA function, from the multifeature code I built last month in order to check the [Bitcoin Price Prediction](https://medium.com/@PP_ART/time-series-forecasting-neural-networks-2ecd302a3e02). For this part of the M5 project the only feature I decided to use is the total sales per day, and per Category.

So to start, we have to make the sum of the sales, after filtering one Category, example Hobbies.
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
mask = (df_cat['valor'] < 21) 
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
    df['{}_t-{}'.format(target,i)] = shift 
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
 Now I had to split the data into train and test(model validation). To decide which portion of the data to use, I made a plot of the total sales of everyday, considering all the categories, to see the trends...
 
  I have to make a better graph, I know is bad, but helps to explain the idea.
  ![prueba](https://paulb86uk.github.io/PP_ART.github.io/2020/Total_Ventas.png)
  
  In the graph it can be clearly see the regions delimited by almost 0 sales days.
  So taking advantage of this fact, I decided to:
  
*   -Dont use the first portion
*   -Keep the 2nd and 3rd portion as train for the model.
*   -Use the 4th and 5th portion as validation for the model.

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
First I select all values that are less than 10, the divisors in the chart, and then made them zero. By sorting first by value and then by day, I can have all the divisors in order in the first rows, so I take two of them and asign values. And finally use this values to create the train, and test dataframes. After this I need to scale the values acordingly for the model:

```python
def Escalando(train,test):
  df = pd.concat([train,test])
  scaler = MinMaxScaler(feature_range=(0, 1))
  values = df.values
  scaler.fit(values)
  train = scaler.transform(train[:,:29].values)
  test = scaler.transform(test[:,:29].values)
  return train,test
 ```
The next step is to prepare all the train,val,test sets with the train,test dataframes. The next function, which is explained more in detail in the Bitcoin Project (explaining here will take a lot of space), makes the work.
```python
def seg_tscv(train,test,n_sp,key):
      np.random.seed(79)
      tscv = TimeSeriesSplit(n_splits=n_sp) 
      X, y = train[:,0:key], train[:,key:] 
      X_test, y_test = test[:,0:key], test[:,key:] 
      for train_index, test_index in tscv.split(train):
        X_train, X_valid = X[train_index], X[test_index]
        y_train, y_valid = y[train_index], y[test_index]
      X_train = X_train.reshape((X_train.shape[0], X_train.shape[1],1))
      X_valid = X_valid.reshape((X_valid.shape[0], X_valid.shape[1], 1))
      X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))
      Data =  {
        'X_train': X_train, 
        'y_train': y_train,
        'X_valid': X_valid,
        'y_valid': y_valid,
        'X_test': X_test,
        'y_test': y_test}
      return Data
 ```
 The important things to consider here, about the function are:
 *  the key is the position where the target+1 is, in this case the 28th position.
 *  n_sp is the number of splits wanted for the TimeSeriesSplit function(has to be tuned, I used a manual Bayesian approach, for the whole tunning of the model)
 *  The train and validation sets are made with the train dataset, while the test set is made with the test dataset.
   
Finally, my favourite franquestein function... With the data ready, the next step is to build up the model. **So after a looong time of fine-tunning**, I set up this function to run the best configuration and to get predictions for the total sales, for the target days of every category.

```python
def rNN_fastaFT(Data): 
    #Sets Asignment
    X_train, y_train = Data['X_train'], Data['y_train']
    X_valid,y_valid = Data['X_valid'], Data['y_valid']
    X_test, y_test  = Data['X_test'], Data['y_test']
    #Model Building
    modelo = keras.models.Sequential([
    keras.layers.SimpleRNN(150, return_sequences=True, input_shape=[28, 1]),
    keras.layers.SimpleRNN(150, return_sequences = True),
    keras.layers.SimpleRNN(150, return_sequences = True),
    keras.layers.SimpleRNN(150),
    keras.layers.Dense(28)])
    #Model Setup
    perdida = "mse"
    optimizador = keras.optimizers.Adam(lr=0.0001)
    modelo.compile(loss=perdida, optimizer=optimizador)
    epoces = 120
    #Model Callbacks
    checkpoint_name = 'Best.hdf5' 
    checkpoint = ModelCheckpoint(checkpoint_name, monitor='val_loss', verbose = 1, save_best_only = True, mode ='auto')
    callbacks_list = [checkpoint]
    #Model ON!
    history = modelo.fit(X_train, y_train, epochs=epoces, validation_data=(X_valid, y_valid), callbacks=callbacks_list)
    #Error on unkown dataset (test)
    y_pred = modelo.predict(X_test)
    err = np.sqrt(mean_squared_error(y_test, y_pred))
    return err
 ```
After exploring different weights, I compiled the best model found in the run with the following code:
```python
def mejormodelo():
  modelo = keras.models.Sequential([
            keras.layers.SimpleRNN(150, return_sequences=True, input_shape=[28, 1]),
            keras.layers.SimpleRNN(150, return_sequences = True),
            keras.layers.SimpleRNN(150, return_sequences = True),
            keras.layers.SimpleRNN(150),
            keras.layers.Dense(28)])
  modelo.load_weights('Best.hdf5')
  optimizer = keras.optimizers.Adam(lr=0.0001)
  modelo.compile(loss='mse', optimizer=optimizer)
  return modelo
```
And eventually, after all this work, I got a prediction:
```python
def laprediccione():
  df_prediccion  = df2.drop(columns=['dia'])
  df_prediccion = df_prediccion.loc[1912,:]
  df_prediccion = escalerA.transform(df_prediccion.values.reshape(56,1).transpose())
  df_prediccion = df_prediccion[:,:28]
  #make the prediction
  resultado = modelo.predict(df_prediccion.reshape(1,28,1))
  #reshape prediction in order to do inverse scaling
  resultado = np.append(df_prediccion,resultado)
  resultado = resultado.transpose()
  resultado = resultado.reshape(1,56)
  resultado = escalerA.inverse_transform(resultado)
  resultado = resultado[:,28:].transpose()
  resultado = resultado.reshape(28)
  return resultado
```
Notes about this code:
* I had to get back into df2, in order to get a nondropped data, in order to get the last row of a complete 28 column train data(row 1912)
* The using the scaler I had to prepare it, after some transpose, and reshaping tricks.(its 56 long, but 28 of them are just nan, need that shape for the scaler to work properly)
* After that put the row into 3d, make the prediction, and again some transpose, and reshape to make the inverse transform. again transpose reshape, and the result is out the oven.

In the last piece of code of this work, I have created the dataframe and downloaded it. Obtaining 3 different dataframes one per category.

```python
def lafinale(resultado,cat):
  dia2 = np.array(range(1914,1942,1))
  df = pd.DataFrame(data={'dia':dia2, 'pred_valor':resultado})
  name = 'total_{}.csv'.format(cat)
  df.to_csv(name)
  files.download(name)
```
