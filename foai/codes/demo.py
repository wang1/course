"""
digit_recognizer.py
~~~~~~~~~~~~~~~~~~~
使用Gradio ImageEditor + Keras实现3B1B风格的MNIST交互绘制识别（最新版兼容5.x+）。
- 前端: 280x280 ImageEditor画布 (白底黑笔刷子绘图，大小20px)。
- 后端: resize 28x28, 灰度, 反转(黑底白字), 输入(1,28,28)形状, 预测。
- 模型: mnist_mlp.keras (期望(28,28)输入)。
- conda install scipy
"""

import gradio as gr
import numpy as np
from PIL import Image, ImageOps
from tensorflow.keras.models import load_model
from scipy.ndimage import gaussian_filter, binary_dilation

# 加载模型（修正文件名）
model = load_model('mnist_mlp.keras')
print("模型加载成功！")

def predict_digit(value):
    if value is None or value['composite'] is None:
        return "请在画布上绘制一个数字！"
    
    sketch_image = value['composite']
    resized = sketch_image.resize((28, 28), Image.Resampling.LANCZOS)
    gray = resized.convert('L')
    inverted = ImageOps.invert(gray)  # 白底黑笔 -> 黑底白笔
    
    # 新增预处理：转为array
    img_array = np.array(inverted, dtype=np.float32) / 255.0  # [0,1]
    
    # 高斯模糊去噪 (sigma=0.5，轻微)
    img_array = gaussian_filter(img_array, sigma=0.5)
    
    # 二值化：>0.1阈值设1（白），匹配MNIST粗体；可调0.05-0.2
    binary = (img_array > 0.1).astype(np.float32)
    
    # 形态学膨胀：变粗线条（用3x3结构）
    # from scipy.ndimage import binary_dilation
    structure = np.ones((2, 2))  # 小内核
    binary = binary_dilation(binary, structure=structure).astype(np.float32)
    
    # 保持(1,28,28)
    img_array = binary.reshape(1, 28, 28)
    
    predictions = model.predict(img_array, verbose=0)[0]
    digit = np.argmax(predictions)
    confidence = np.max(predictions)
    return f"预测数字: {digit}\n置信度: {confidence:.2%}"

# 创建Gradio界面
with gr.Blocks(title="MNIST Digit Recognizer - 3B1B Style") as demo:
    gr.Markdown("# 🖊️ 绘制数字识别器\n\n像3Blue1Brown视频一样，用鼠标画0-9数字，点击提交预测！（用刷子工具绘制）")
    
    with gr.Row():
        with gr.Column(scale=1):
            # 输入: ImageEditor作为sketchpad
            sketchpad = gr.ImageEditor(
                sources=(),  # 禁用上传/摄像头，只剩空白画布
                canvas_size=(280, 280),  # 放大前端画布
                fixed_canvas=True,  # 固定尺寸
                brush=gr.Brush(
                    default_size=10,  # 刷子半径
                    colors=["#000000"],  # 固定黑笔
                    color_mode="fixed"  # 只用黑，不变色
                ),
                type="pil",  # 返回PIL图像
                label="绘制区 (280x280，鼠标+刷子画数字)",
                interactive=True
            )
            submit_btn = gr.Button("提交预测", variant="primary")
            clear_btn = gr.Button("清空画布")
        
        with gr.Column(scale=1):
            output = gr.Textbox(
                label="预测结果",
                placeholder="绘制后点击提交...",
                lines=3,
                interactive=False
            )
            # 示例（简单提示）
            gr.Markdown("**提示**：画清晰的0-9数字，笔刷大小适中。")
    
    # 绑定事件
    submit_btn.click(
        fn=predict_digit,
        inputs=sketchpad,
        outputs=output
    )
    
    # 清空
    clear_btn.click(
        fn=lambda: gr.update(value=None),
        outputs=sketchpad
    )

# 启动
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # True为公网分享
        debug=True
    )