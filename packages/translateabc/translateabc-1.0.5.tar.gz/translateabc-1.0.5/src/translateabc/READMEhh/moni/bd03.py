# %%
import pandas as pd
import numpy as np
df = pd.read_csv('F:/ICT2023/AI-LAB/data/titanic_train.csv')
df.head()

# %%
df.tail()

# %%
for x in df.columns:
    qssl = df[x].isnull().sum()#缺失值数量
    qszb = df[x].isnull().sum()/df.shape[0]*100
    print(x,'缺失值数量：',qssl,'缺失值占比：',qszb,'%')

# %%
df.dropna(inplace=True)

# %%
df.isnull().sum()

# %%
# 获取数值特征统计信息
df.describe()

# %%
# 绘制数据集中所有数值型特征的直方图
import matplotlib.pyplot as plt
df.hist(figsize=(12,8))
plt.show()

# %%
# 绘制数据集中所有分类型特征的条形图
import seaborn as sn
x = ['Sex','Embarked','Pclass','Survived']
for f in x:
    sn.countplot(x=f,data=df)
    plt.show()

# %%
# 使用pandas的corr()方法计算数据集中数值型特征之间的相关系数矩阵
df_corr = df.corr()
df_corr

# %%
# 绘制相关系数矩阵的热力图
import seaborn as sn
sn.heatmap(df_corr,annot=True)

# %%
# 选择两个数值型特征绘制散点图，并添加趋势线
sn.regplot(x='Age',y='Fare',data=df)
plt.show()

# %%
# 对所有分类型特征进行独热编码
from sklearn.preprocessing import OneHotEncoder
categorical_features = ['Sex','Embarked','Pclass']
encoder = OneHotEncoder()
encoder_features = encoder.fit_transform(df[categorical_features]).toarray()
encoder_features_df = pd.DataFrame(encoder_features, columns=encoder.get_feature_names())
df.drop(categorical_features, axis=1, inplace=True)
data = pd.concat([df, encoder_features_df], axis=1)
data.dropna(inplace=True)


# %%
df_one = pd.get_dummies(df)#对数据集做独热编码

# %%
# 将数据集划分为训练集和测试集，比例为3:1，使用随机种子为42
x=[col for col in df_one.columns if col!='Survived']
X = df[x]
Y=df_one['Survived']

# %%
from sklearn.model_selection import train_test_split
x_train,x_test,y_train,y_test=train_test_split(X,Y,test_size=0.3,random_state=42)

# %%
# 使用线性回归模型对数据集进行拟合，计算模型的R方值
from sklearn.linear_model import LinearRegression,LogisticRegression
from sklearn.metrics import r2_score,accuracy_score,f1_score
lr = LinearRegression()# 建模
lr.fit(x_train, y_train)# 使用模型训练数据
y_pred = lr.predict(x_test)# 对模型进行预测
r2 = r2_score(y_test, y_pred)# 模型评估
print('线性回归模型的R方值：',r2)

# %%
# 使用逻辑回归对数据集进行拟合，计算模型的准确率
logistic_regression = LogisticRegression()#建模
logistic_regression.fit(x_train,y_train)#进行模型训练
y_pred = logistic_regression.predict(x_test)#预测
accuracy = accuracy_score(y_test,y_pred)#模型评分
print('逻辑回归模型的准确率：',accuracy)

# %%
# 使用随机森林模型对数据集进行拟合，计算模型的准确率
from sklearn.ensemble import RandomForestClassifier
random_forest = RandomForestClassifier()
random_forest.fit(x_train,y_train)
y_pred = random_forest.predict(x_test)
accuracy = accuracy_score(y_test,y_pred)
print('随机森林模型的准确率：',accuracy)

# %%
# 使用accuracy_score进行评估
from sklearn.metrics import accuracy_score,f1_score
print('逻辑回归模型的准确率(使用accuracy_score进行评估)：',accuracy_score(y_test,y_pred))

# %%
# 使用网格搜索对随机森林模型进行调参，选择最优参数，过采样（SMOTE）
from sklearn.model_selection import GridSearchCV
param_grid = {'n_estimators':[10,20,30,40],'max_depth':[3,4,5,6]}
grid_search = GridSearchCV(random_forest,param_grid=param_grid,cv=10)
grid_search.fit(x_train,y_train)
print('最优参数：',grid_search.best_params_)

# %%
# 使用最优参数重新训练随机森林模型，并计算模型的准确率
random_forest = grid_search.best_estimator_
random_forest.fit(x_train,y_train)
y_pred = random_forest.predict(x_test)
accuracy = accuracy_score(y_test,y_pred)
print('优化后的随机森林模型的准确率：',accuracy)

# %%
# 对调优后的模型使用f1值评估
print('优化后的随机森林模型的f1值：',f1_score(y_test,y_pred,average='micro'))

# %%



