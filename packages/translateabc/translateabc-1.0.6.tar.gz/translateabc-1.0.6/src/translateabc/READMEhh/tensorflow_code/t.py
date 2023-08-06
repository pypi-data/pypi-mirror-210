import tensorflow as tf
from tensorflow.python.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.python.keras import regularizers

# Define parameters
batch_size = 128
epochs = 20
IMG_HEIGHT = 100
IMG_WIDTH = 100
l2_rate = 0.01

# rescale在这里把图片的像素值缩小了255倍，除以255
train_image_generator = tf.keras.preprocessing.image.ImageDataGenerator(
    rescale=1./255, validation_split=0.2)
# directory 目标路径
# batch_size  每次输入到模型中的样本数量
# shuffle 开始之前是否对数据进行随机打乱
# target_size 是指在读取图像时，将所有图像调整为固定大小的操作
# class_mode categorical代表分类编码的形式 还有binary二元分类 sparse稀疏分类问题
train_data_gen = train_image_generator.flow_from_directory(directory='flower_photos',
                                                           batch_size=batch_size,
                                                           shuffle=True,
                                                           target_size=(
                                                               IMG_HEIGHT, IMG_WIDTH),
                                                           class_mode='categorical',
                                                           subset='training')

validation_data_gen = train_image_generator.flow_from_directory(directory='flower_photos',
                                                                batch_size=batch_size,
                                                                shuffle=False,
                                                                target_size=(
                                                                    IMG_HEIGHT, IMG_WIDTH),
                                                                class_mode='categorical',
                                                                subset='validation')

# 获取训练数据集和验证数据集中类别标签名称及其对应的数字编码
class_names = train_data_gen.class_indices

# 将数字编码和标签名称反转，得到标签名称列表
# label_names = list(class_names.keys())
print('标签名称列表为：', class_names)

# 用于构建序列模型，由多个神经网络层按照一定的顺序依次组成
model = tf.keras.Sequential([
    # Convolutional Layers 卷积层  -> 作用：提取图像特征

    # Conv2D(32, (3,3)：创建一个包含32个卷积核、大小为3x3的二维卷积层。
    # padding='same'：每次卷积运算都会缩小空间，为了避免某次输出大小为1，即使用零填充到输入特征图外围，使得输出特征图和输入特征图的大小相同。
    # activation='relu'：设置激活函数为ReLU，ReLU函数可以有效地缓解梯度消失问题，并且在卷积神经网络中表现良好。
    # input_shape=(IMG_HEIGHT, IMG_WIDTH ,3)：指定输入的形状，即待处理图像的高度、宽度和通道数。这里输入的是RGB三通道的彩色图像，所以通道数为3。
    # kernel_regularizer=regularizers.l2(l2_rate)：设置L2正则化项，用于控制模型的复杂度，防止欠拟合
    Conv2D(32, (3, 3), padding='same', activation='relu', input_shape=(IMG_HEIGHT, IMG_WIDTH, 3),
           kernel_regularizer=regularizers.l2(l2_rate)),
    MaxPooling2D(pool_size=(2, 2)),
    Conv2D(64, (3, 3), padding='same', activation='relu',
           kernel_regularizer=regularizers.l2(l2_rate)),
    MaxPooling2D(pool_size=(2, 2)),
    Conv2D(128, (3, 3), padding='same', activation='relu',
           kernel_regularizer=regularizers.l2(l2_rate)),
    MaxPooling2D(pool_size=(2, 2)),
    Conv2D(128, (3, 3), padding='same', activation='relu',
           kernel_regularizer=regularizers.l2(l2_rate)),
    MaxPooling2D(pool_size=(2, 2)),

    # 压缩128通道到到一维
    Flatten(),

    # Dense layers
    Dense(1024, activation='relu', kernel_regularizer=regularizers.l2(l2_rate)),
    Dense(512, activation='relu', kernel_regularizer=regularizers.l2(l2_rate)),
    Dense(256, activation='relu', kernel_regularizer=regularizers.l2(l2_rate)),
    Dense(128, activation='relu', kernel_regularizer=regularizers.l2(l2_rate)),
    Dense(5, activation='softmax')
])

# Compile the model with categorical crossentropy loss and Adam optimizer
# adam随机梯度下降
# 多分类任务的交叉熵损失函数
model.compile(optimizer='adam',
              loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

# Fit the model to the data generator for given number of epochs
# 整除
history = model.fit(train_data_gen,
                    steps_per_epoch=train_data_gen.samples // batch_size,
                    epochs=epochs,
                    validation_data=validation_data_gen,
                    validation_steps=validation_data_gen.samples // batch_size)

# Save the trained model to a file
model.save('model/model_test.ckpt')
