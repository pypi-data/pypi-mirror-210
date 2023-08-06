# %% [markdown]
# 1、导入库pandas、numpy、warnings

# %%
import pandas as pd
import numpy as np

# %% [markdown]
# 2、读取数据,查看除表头外的前5行数据

# %%
df=pd.read_csv('E:\\data\\03\\credit-default.csv')
df.head()

# %% [markdown]
# 3、查看目标变量’Target’列中的数据分布状况

# %%
df['Target'].value_counts()#方法一

# %%
import seaborn as sn  #方法二
sn.countplot(df['Target'])

# %% [markdown]
# 4、使用corr()方法获取spearman相关性系数矩阵并输出；

# %%
df_corr=df.corr()
df_corr

# %% [markdown]
# 5、对相关性超过0.8的属性进行删除；

# %%
list_drop=[]
for x in df_corr.columns:
    for y in df_corr.index:
        c=df_corr.loc[x,y]
        if c>0.8 and x!=y:
            list_drop.append(x)

# %%
for x in list_drop:
    del df[x]

# %%
df.shape

# %% [markdown]
#  6、使用heatmap绘制相关性矩阵热力图；

# %%
import matplotlib.pyplot as plt
plt.figure(figsize=(15,12))
sn.heatmap(df_corr)

# %% [markdown]
# 7、对数值型变量’ House_State’ 、’ Year_Income’、’ Couple_Year_Income’、’  L12_Month_Pay_Amount’中的缺失值进行填充；
# 

# %%
df['House_State']=df['House_State'].replace(np.nan,df['House_State'].mode()[0])
df['Year_Income']=df['Year_Income'].replace(np.nan,df['Year_Income'].mean())
df['Couple_Year_Income']=df['Couple_Year_Income'].replace(np.nan,df['Couple_Year_Income'].mean())
df['L12_Month_Pay_Amount']=df['L12_Month_Pay_Amount'].replace(np.nan,df['L12_Month_Pay_Amount'].mean())

# %% [markdown]
# 8、对名义型变量(字符串类型的数据，DataFrame中表示的是object型) ’
#   Gender’ 中的缺失值进行填充；
# 

# %%

df['Unit_Kind']=df['Unit_Kind'].replace('Be',df['Unit_Kind'].mode()[0])
df['Unit_Kind']=df['Unit_Kind'].replace('ae',df['Unit_Kind'].mode()[0])
df['Unit_Kind']=df['Unit_Kind'].replace('Da',df['Unit_Kind'].mode()[0])
df['Occupation']=df['Occupation'].replace('Y0000',df['Occupation'].mode()[0])
df['Occupation']=df['Occupation'].replace('X0000',df['Occupation'].mode()[0])
df['Occupation']=df['Occupation'].replace(' ',df['Occupation'].mode()[0])
df['Occupation']=df['Occupation'].replace('   ',df['Occupation'].mode()[0])

# %%
from sklearn.impute import SimpleImputer
model=SimpleImputer(missing_values=np.nan,strategy='mean')
df_model=model.fit_transform(df)

# %%
df_df=pd.DataFrame(data=df_model,columns=df.columns)
type(df_df)

# %%
#9、对名义型变量做独热编码
df_one=pd.get_dummies(df_df)#做独热编码

# %% [markdown]
# 10、将数据按照目标列和其他列进行拆分，并命名为x,y

# %%
x=[col for col in df_one.columns if col!='Cust_No' and col!='Target']
x

# %%
y=df['Target']
df_x=df_one[x]
y

# %%
#11、使用train_test_split对数据进行x,y拆分，拆分为训练集和测试集，拆分的测试集比例为0.3
from sklearn.model_selection import train_test_split
x_train,x_test,y_train,y_test=train_test_split(df_x,y,test_size=0.3)

# %% [markdown]
# 12、引入随机深林算法随机指定参数

# %%
#使用随机深林建模，训练，输出模型
from sklearn.ensemble import RandomForestClassifier
model_R=RandomForestClassifier().fit(x_train,y_train)#
#print(round(model_R.score(x_test,y_test),2))#取小数点后两位

# %%
#预测
df_p=model_R.predict(x_test)
df_p

# %%
#对模型进行评分
from sklearn.metrics import accuracy_score
print(accuracy_score(y_test,df_p))

# %%
from imblearn.over_sampling import SMOTE
x_train,y_train=SMOTE().fit_resample(x_train,y_train)
pd.Series(y_train).value_counts()

# %%
#再次训练随机深林模型
from sklearn.ensemble import RandomForestClassifier
model_R2=RandomForestClassifier().fit(x_train,y_train)

# %%
df_p2=model_R2.predict(x_test)
df_p

# %%
from sklearn.metrics import f1_score
print(f1_score(y_test,df_p2))

# %%



