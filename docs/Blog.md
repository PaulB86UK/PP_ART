---
title: Blog
permalink: /Blog/
---

# Blog

## Tuesday 27th May 2020  
### Titanic Target ['Age'] Missing Values Treatment
### XGBoost Regressor Fine-Tuning

#### Wednesday
Today I prepared some code to train XGboost with the dataset created, after fine tunning I choose a good performing model and use it to complete the missing age rows.
**Pandas**, **Sklearn** and **XGboost** were the used libraries in this opportunity.

|                   Category                   |    Date   |            Source            |
|:---------------------------------------------|:----------|:-----------------------------|    
| Target Variable ['Age'] Missing Values       |24/05/2020 | Titanic Dataset ['Age'] Data |   

The details of the work, [here](https://paulb86uk.github.io/PP_ART.github.io/2020/27_5): 

#### &nbsp;
#### &nbsp;

## Tuesday 26th May 2020  
### Titanic Target ['Age'] Transformation 

#### Good Tuesday!. 

An interesting fact is that on this day, 1969, Apollo10 ship returned to earth. Apollo 10 was a May 1969 human spaceflight, the fourth crewed mission in the United States Apollo program, and the second (after Apollo 8) to orbit the Moon. It was the F mission: a "dress rehearsal" for the first Moon landing, testing all the components and procedures just short of actually landing. Astronauts Thomas Stafford and Gene Cernan flew the Apollo Lunar Module (LM) to a descent orbit within 8.4 nautical miles (15.6 km) of the lunar surface, the point where powered descent for landing would begin. After orbiting the Moon 31 times Apollo 10 returned safely to Earth, and its success enabled the first actual landing (Apollo 11) two months later. Amazingly. Apollo 10 set the record for the highest speed attained by a crewed vehicle: 39,897 km/h (11.08 km/s or 24,791 mph) on May 26, 1969, during the return from the Moon.

Regarding, my work from today... My objective was to think about different ways to work the target variable, in order to get good results in the model for the fill-in the ['Age'] column missing values from the dataset.
I tried different things, but up to now, only one seems to have worked properly. I will show two of them with the corresponding codes. The first one was to split the age into classes, with aproximately (as much as possible) a similar amount of data in each class [A classification task]. The second one, was to transform the age data in order to obtain a more normal distribution [A regression task]. **Pandas**, **Sklearn** and **XGboost** were the used libraries in this opportunity.

|                   Category                   |    Date   |            Source            |
|:---------------------------------------------|:----------|:-----------------------------|    
| Target Variable ['Age']  transformation      |24/05/2020 | Titanic Dataset ['Age'] Data |   



The details of the work, [here](https://paulb86uk.github.io/PP_ART.github.io/2020/26_5): 
#### &nbsp;
#### &nbsp;
## Monday 25th May 2020  
### Titanic Dataset Age Data Features Fitting  
#### Fixing Columns for filling age missing values

Good Monday!. At this point I continued working with the remaining object features from the dataset: **Name** and **Ticket**. I did not remember having worked with string like this before, you should check the code, I believe its a nice one!.

|                   Category                   |    Date   |            Source            |
|:---------------------------------------------|:----------|:-----------------------------|    
| Exploratory Data Analysis & Data Preparation |24/05/2020 | Titanic Dataset ['Age'] Data |   


The details of the work of today can be seen [here](https://paulb86uk.github.io/PP_ART.github.io/2020/25_5): 
#### &nbsp;
#### &nbsp;
## Sunday 24th May 2020  
### Titanic Dataset Age Data Features Fitting  
#### Fixing Columns for filling age missing values

Hello!, Today I checked yesterday work, and continue in the same objective, fixing some omisions from yesterday, and also started to work on the object columns, in order to see how to convert them into numbers that make sense for the model I will try to build later on.

|                   Category                   |    Date   |            Source            |
|:---------------------------------------------|:----------|:-----------------------------|    
| Exploratory Data Analysis & Data Preparation |24/05/2020 | Titanic Dataset ['Age'] Data |   

The details of the work of today can be seen [here](https://paulb86uk.github.io/PP_ART.github.io/2020/24_5): 
#### &nbsp;
#### &nbsp;

## Saturday 23th May 2020  
### Titanic Dataset Age Data Features Fitting - Reorder.

Today I worked out some code to fix the numerical values of the features relevant to the Age column of the Tytanic Dataset. **Pandas** and **Seaborn** were the used libraries in this opportunity.

|                   Category                   |    Date   |            Source            |
|:---------------------------------------------|:----------|:-----------------------------|    
| Exploratory Data Analysis & Data Preparation |23/05/2020 | Titanic Dataset ['Age'] Data |   

### [GitHub Link](https://github.com/PaulB86UK/EDA_PP/blob/master/2020/May-June/EDA_Reorder.ipynb)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Open in Colaboratory](https://colab.research.google.com/drive/1VPLQVgzZ0R5MsGDPvb6DODxsJIpwa9sE?usp=sharing)
