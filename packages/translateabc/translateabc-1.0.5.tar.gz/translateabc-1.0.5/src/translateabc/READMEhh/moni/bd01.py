# %% [markdown]
# ## 8.银行客户聚类

# %%
import pandas as pd
import numpy as np

# %% [markdown]
# ### 1.导入数据，查看数据前五行

# %%
df = pd.read_csv('./bankmarketing.csv')
df.head()

# %% [markdown]
# ### 2.对数据进行缺失值处理

# %%
df.isnull().sum()

# %%
df.fillna(df.mode().iloc[0],inplace=True)

# %%
df.isnull().sum()

# %% [markdown]
# ### 3.对数据进行编码处理

# %%
df_oh = pd.get_dummies(df)
df_oh.head()

# %% [markdown]
# ### 4.对数据进行主成分分析降维，主成分对原数据解释比例不低于95%

# %%
from sklearn.decomposition import PCA

# %%
pca_model = PCA(n_components=0.95)
df_pca = pca_model.fit_transform(df_oh)
df_pca = pd.DataFrame(df_pca)
df_pca.head()

# %% [markdown]
# ### 5.对数据进行标准化

# %%
from sklearn.preprocessing import StandardScaler

# %%
scale = StandardScaler()
df_std = scale.fit_transform(df_pca)

# %% [markdown]
# ### 6.使用k-means算法进行建模，使用sse和轮廓系数对模型结果进行评估。对轮廓系数绘制折线图，根据绘图选出最优的k值

# %%
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from matplotlib import pyplot as plt

# %%
k,silhouette = [],[]
for i in range(2,6):
    km_model = KMeans(n_clusters=i)
    km_model.fit(df_std)
    k.append(i)
    sil = silhouette_score(df_std,km_model.labels_)
    silhouette.append(sil)
    sse = km_model.inertia_
    print(f'k={i},silhouette={sil},sse={sse}')

# %%
plt.plot(k,silhouette)
plt.xlabel('k')
plt.ylabel('silhouette')
plt.show()

# %% [markdown]
# ### 7.使用Birch算法对用户业务流量进行聚类分析，并绘制轮廓系数的手肘图选出最优的k值

# %%
from sklearn.cluster import Birch

# %%
k,silhouette = [],[]
for i in range(2,8):
    birch_model = Birch(n_clusters=i)
    birch_model.fit(df_std)
    k.append(i)
    sil = silhouette_score(df_std,birch_model.labels_)
    silhouette.append(sil)
    sse = km_model.inertia_
    print(f'k={i},silhouette={sil},sse={sse}')

# %%
plt.plot(k,silhouette)
plt.xlabel('k')
plt.ylabel('silhouette')
plt.show()

# %% [markdown]
# ### 8.使用SpecteralClustering算法对用户业务流量进行聚类分析，并绘制轮廓系数的手肘图选出最优的k值

# %%
from sklearn.cluster import SpectralClustering

# %%
k,silhouette = [],[]
for i in range(2,6):
    spe_model = SpectralClustering(n_clusters=i)
    spe_model.fit(df_std)
    k.append(i)
    sil = silhouette_score(df_std,spe_model.labels_)
    silhouette.append(sil)
    see = spe_model.inertia_
#     print(f'k={i},silhouette={sil},sse={sse}')

# %%
plt.plot(k,silhouette)
plt.xlabel('k')
plt.ylabel('silhouette')
plt.show()

# %% [markdown]
# ### 9.根据前面三种算法的结果，选出最优的算法模型，利用最优的算法模型输出数据集的聚类标签，并将标签导入到数据集中

# %%
birch_model = Birch(n_clusters=2)
label = birch_model.fit_predict(df_std)
label

# %%
df_oh['label'] = label
df_oh.head()

# %% [markdown]
# ### 10.查看不同聚类结果下的特征均值，并绘制不同聚类结果下的特征均值折线图

# %%
df.columns

# %%
mean_dict = {'age':'mean','duration':'mean','campaign':'mean'}
data_label = df_oh.groupby('label').agg(mean_dict)
data_label

# %%
plt.figure(figsize=(20,10))
for i in data_label.index:    
    plt.plot(['age','duration','campaign'],data_label.iloc[i],'o-')
plt.show()

# %% [markdown]
# ### 11.绘制三维散点图查看各簇的数据在三维特征下的数据分布，并描述各个簇的特点

# %%
import mpl_toolkits.mplot3d

# %%
from mpl_toolkits.mplot3d import Axes3D 
colors = ['r','g'] 
markers = ['s', 'x'] 
fig = plt.figure(figsize=(10,8)) 
ax = Axes3D(fig) 
for i in range(0,2): 
    ax.scatter(df_oh['age'][df_oh['label']==i],
               df_oh['duration'][df_oh['label']==i],
               df_oh['campaign'][df_oh['label']==i],
               c=colors[i],marker=markers[i]) # 绘制三维散点图 
ax.view_init(elev=20,azim=30) 
ax.set_xlabel('age') 
ax.set_ylabel('duration') 
ax.set_zlabel('campaign') 
plt.show() 


