import tensorflow as tf
import numpy as np
from PIL import Image

# 加载模型
model = tf.keras.models.load_model('model/model_test.ckpt')

# 加载图片，并进行预处理
img = Image.open('flower_photos/roses/123128873_546b8b7355_n.jpg').resize((100, 100))
img_arr = np.array(img) / 255.0
img_arr = np.expand_dims(img_arr, axis=0)

# 使用模型进行预测
result = model.predict(img_arr)
label = np.argmax(result, axis=1)

# 输出预测结果
print('预测结果为：', label)
