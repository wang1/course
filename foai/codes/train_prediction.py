"""
行为：
- 如果当前目录存在 mnist_mlp.keras -> 加载模型并在测试集上评估 + 保存预测图
- 否则训练模型（MLP），训练后保存为 mnist_mlp.keras，再评估并保存预测图

注意：
- 适合远程无头运行（使用 matplotlib Agg 后端并保存图片）
- 默认激活函数为 'relu'（可通过修改 ACTIVATION 变量切换）

环境安装：
- 使用TensorFlow 的 Keras（一个高层神经网络 API）
- conda install tensorflow matplotlib numpy -c conda-forge
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')   # 无头服务器使用 Agg 后端（不弹窗，直接保存图片）
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras

# 载入 MNIST 数据，第一次将从网络下载，以后本地读取
# train是60000张训练图片，test是10000张测试图片
# x是图片，y是标签即具体数字
(x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()
# 归一化数据
x_train = x_train.astype("float32") / 255.0
x_test  = x_test.astype("float32") / 255.0

# 程序运行参数定义
RELU = "relu"   # 隐藏层激活函数，也可使用 sigmoid（或 'tanh', 'leaky_relu'）
SOFTMAX = "softmax"   # 最后一层的激活函数，输出概率值 
LOSS = 'sparse_categorical_crossentropy'    # 损失函数（交叉熵损失比均方差mse更合适）
BATCH_SIZE = 32 # 每批检测的图片个数，完成一个批次后更新参数。每个epoch大约有54000/32=1688批次（数值越大则需要的内存越大）
EPOCHS = 10 # 重复10次
VALIDATION_SPLIT = 0.1  # 训练时留下10%的数据进行校验，以防过拟合及调整超参数。test用于整体评估（从 60000 张图片里划去了 10%，剩下 54000 张用于训练）
LEARNING_RATE = 0.1    # 学习率，过大或过小都欠佳，比如设为1.0或0.0001
OPT = keras.optimizers.SGD(learning_rate=LEARNING_RATE) # 优化器使用随机梯度下降

OUT_PNG = "predictions.png"
MODEL_PATH = "mnist_mlp.keras"
VERBOSE = 1 # 显示训练或检测的进度，0则静默

model = None

# 显示 TensorFlow 版本与使用的设备（CPU/GPU）
print("TensorFlow version:", tf.__version__)
print("Physical devices:", tf.config.list_physical_devices())

# 检测是否有训练好的模型文件，有则加载，无则马上训练
if os.path.exists(MODEL_PATH):
    print(f"检测到模型文件 {MODEL_PATH}，直接加载...")
    model = keras.models.load_model(MODEL_PATH)    
else:
    print(f"未检测到 {MODEL_PATH}，开始训练新模型")
    # 构建网络结构。可调整隐藏层的神经元个数如128和层数如4层等
    model = keras.models.Sequential([
        keras.layers.Flatten(input_shape=(28, 28)),
        keras.layers.Dense(16, activation=RELU),
        keras.layers.Dense(16, activation=RELU),
        keras.layers.Dense(10, activation=SOFTMAX)
    ])
    # 构建网络其他参数（梯度函数，损失函数，以及每个 epoch 结束后算一下正确率）
    model.compile(optimizer=OPT, loss=LOSS, metrics=['accuracy'])

    print("开始训练模型...")
    model.fit(
        x_train, y_train,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_split=VALIDATION_SPLIT,
        verbose=VERBOSE
    )
    print(f"训练结束，保存模型到 {MODEL_PATH}")
    model.save(MODEL_PATH)
    # 对测试集（10000张）进行测试：
    loss, acc = model.evaluate(x_test, y_test, verbose=VERBOSE)
    print(f"测试集图片测试结果 - loss: {loss:.4f}, accuracy: {acc:.4f}")

# 显示模型信息
print("模型结构：")
model.summary()

# 取前 30 张测试图做可视化并保存到文件
n = 30
# x_vis = x_test[:n]
# y_vis = y_test[:n]

# 从测试集随机选 30 个索引，图片不重复
indices = np.random.choice(len(x_test), n, replace=False)
x_vis = x_test[indices]
y_vis = y_test[indices]

# 进行预测。preds 形状是 (30, 10)，每行表示该图片属于 0~9 的概率分布。
preds = model.predict(x_vis)
plt.figure(figsize=(12, 3)) # 图形尺寸
for i in range(n):
    plt.subplot(n//10, 10, i+1)   # 显示3行，每行10个，从1开始
    plt.imshow(x_vis[i], cmap='gray')   # 显示每个图片
    plt.axis('off') # 不显示坐标轴
    p = np.argmax(preds[i])    # 取概率最大的那个数字的序号
    t = y_vis[i]
    color = 'green' if p == t else 'red'    # 如果与标签符合则绿色否则红色
    plt.title(f"P:{p} / T:{t}", color=color, fontsize=8)
plt.tight_layout()
plt.savefig(OUT_PNG, dpi=150)
print(f"预测图已保存为 {OUT_PNG}")

    

    