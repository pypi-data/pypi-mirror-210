# %%
import pandas as pd
import numpy as np

# %%
data=pd.read_csv('E:\\data\\03\\credit-default.csv')
data.head()

# %%
#标准化处理模块
from sklearn.preprocessing import StandardScaler
#fit_transform 对数据进行标准化
#增加一个新的特征
data['normAmount'] = StandardScaler().fit_transform(data['Amount'].value.reshape(-1,1))

import seaborn as sn  #方法二
sn.countplot(df['Target'])

#删除没用特征
data = data.drop(['Time','Amount'],axis=1)

x = data.loc[:,data.columns!='Class']
y = data.loc[:,data.columns=='Class']

# 异常样本个数
number_records_abnormal =  data.loc[data['Class']==1].shape[0]
# 异常样本的索引值
abnormal_indexes=np.array(data.loc[data['Class']==1].index)
# 正常样本的索引值
normal_indexes=np.array(data.loc[data['Class']==0].index)
# 从正常样本随机取样，数量为异常样本个数
random_normal_indexes = np.random.choice(normal_indexes,number_records_abnormal,replace=False)
random_normal_indexes=np.array(random_normal_indexes)
# 合并数据
under_sample_indexes = np.concatenate([abnormal_indexes,random_normal_indexes])
#下采样数据集
under_sample_data=data.loc[under_sample_indexes]
#特征数据
x_undersample=under_sample_data.loc[:,under_sample_data.columns!='Class']
#label列
y_undersample=under_sample_data.loc[:,under_sample_data.columns!='Class']
#查看数据
print(xxx)
print(xxx)

from imblearn.over_sampline import SMOTE
oversampler = SMOTE(random_state=0)
X_oversample,Y_oversample= oversampler.fit_resample(X,Y.Values.reshape(-1,1))

#查看数据
x_oversample = pd.DataFrame(x_oversample)
y_oversample = pd.DataFrame(y_oversample)

#导入缺乏数据模块
from sklearn.model_selection import train_test_split
#切分原始数据：test_size--测试集比率
#random_state= 0 --每次随机得到的数据集是一样的
x_train_oversample,x_test_oversample,y_train_oversample,y_test_oversample=tranin_test_split(x_oversample,y_oversample,test_size=.2,random_state=0)
#查看数据
print('查看个数',len())
print('查看个数',len())

# 逻辑回归
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold, cross_val_score
from sklearn.metrics import confusion_matrixon_matrix,recall_score,classification_report


# 构造交又验证函数
def printing_Kfold_scores(x_data, y_data):
    fold = KFold(n_splits=5, shuffle=False)
    recall_accs = []
    for iteration, indices in enumerate(fold.split(x_data), start=1):
        lr = LogisticRegression()
        lr.fit(x_data.iloc[indices[0], :],
               y_data.iloc[indices[0], :].values.ravel())
        y_pred = lr.predict(x_data.iloc[indices[1], :].values)
        recall_acc = recall_score(
            y_data.iloc[indices[1], :].values, y_pred)
        recall_accs.append(recall_acc)
        print('Iteration', iteration, ':recall score = ', recall_acc)
        mean_recall_score = np.mean(recall_accs)
        print('Mean recall score', mean_recall_score)
        return mean_recall_score
    
origin = printing_Kfold_scores(x_train,Y_train)
undersample = printing_Kfold_scores(x_train_undersample,y_train_undersample)
oversample = printing_Kfold_scores(x_train_oversample,y_train_oversample)
    
# 构建混淆矩阵
def plot_confusion_matrix(cm,classes,title='Confusion matrix',cmap=plt.cm.Blues):
    plt.imshow(cm,interpolation='nearest',cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=0)
    plt.yticks(tick_marks, classes)
    thresh = cm.max() / 2
    for i, j in itertools.product(range(cm.shape[0]),range(cm.shape[1])):
        plt.text(j, i, cm[i,j],
            horizontalalignment="center",
            color="whiter" if cm[i,j] > thresh else "black")
        olt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

import itertools
lr = LogisticRegression()
lr.fit(x_train_oversample,y_train_oversample.value.raval())
y_pred = lr.predict(x_test.values)

# Compute confusionmatrix
cnf_matrix = confusion_matrix(Y_test,Y_pred)
np.set_printoptions(precision=2)

# Plot non-normalized confusion matrix
class_names = [0,1]
plt.figure()
plot_confusion_matrix(cnf_matrix,classes=class_names,title='Confusion matrix')
plt.show()


