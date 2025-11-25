# 单文件 Gradio 应用：使用 facenet-pytorch (MTCNN + InceptionResnetV1)
# 支持：上传最多 5 张明星图片 + 1 张查询图片，返回与每位明星的相似度并展示画廊。
# 要求：
#   nvidia-smi查看cuda版本
#   conda install pytorch torchvision torchaudio pytorch-cuda=12.4 -c pytorch -c nvidia
#   pip install facenet-pytorch
#
# Run:
#   下载模型等被墙，使用代理
#   proxychains python face_similarity.py

import io
from typing import List, Tuple, Optional

from PIL import Image
import numpy as np
import torch
import torchvision.transforms as T
from facenet_pytorch import InceptionResnetV1, MTCNN
import gradio as gr

# -------------------- 配置 --------------------
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 图像预处理（与 InceptionResnetV1 配合）
transform = T.Compose([
    T.Resize((160, 160)),
    T.ToTensor(),
    T.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

# 初始化 MTCNN 与 InceptionResnetV1（权重会在首次运行时下载）
mtcnn = MTCNN(image_size=160, margin=20, keep_all=False, device=DEVICE)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(DEVICE)

# -------------------- 启动预热逻辑 --------------------
def _startup_preheat():
    """在程序启动时运行一次前向，强制加载权重与触发 CUDA kernel 的初始化。"""
    try:
        # 1) 预热 embedding 模型
        dummy = torch.randn(1, 3, 160, 160).to(DEVICE)
        with torch.no_grad():
            _ = resnet(dummy)
    except Exception:
        pass

    try:
        # 2) 预热 MTCNN（构建内部网络）
        _ = MTCNN(image_size=160, margin=20, keep_all=False, device=DEVICE)
    except Exception:
        pass

# 立即执行一次预热（会在程序启动时运行）
_startup_preheat()

# -------------------- 工具函数 --------------------

def pil_to_tensor(img: Image.Image) -> torch.Tensor:
    if img.mode != 'RGB':
        img = img.convert('RGB')
    return transform(img)


def extract_face_from_pil(img: Image.Image) -> Tuple[torch.Tensor, Optional[Image.Image]]:
    """使用 MTCNN 检测并裁剪人脸，返回用于模型的 tensor(batch=1) 以及用于展示的 PIL 裁剪图（若可用）。
    若检测失败，则返回中心裁剪的替代图像作为展示。
    """
    try:
        # mtcnn 返回 (3,160,160) tensor 或 None
        face_tensor = mtcnn(img)
        if face_tensor is not None:
            # mtcnn 已返回 tensor（未包含 batch dim）
            return face_tensor.unsqueeze(0).to(DEVICE), None
    except Exception:
        pass

    # 回退：中心裁切并 resize
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    cropped_pil = img.crop((left, top, left + side, top + side)).resize((160, 160))
    tensor = pil_to_tensor(cropped_pil).unsqueeze(0).to(DEVICE)
    return tensor, cropped_pil


def get_embedding(face_tensor: torch.Tensor) -> np.ndarray:
    """从 (1,3,160,160) 的 tensor 中得到 L2 归一化的 embedding（512-d）。"""
    with torch.no_grad():
        emb = resnet(face_tensor)
    emb = emb.cpu().numpy().reshape(-1)
    norm = np.linalg.norm(emb)
    if norm > 0:
        emb = emb / norm
    return emb


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))

# -------------------- Gradio 回调函数 --------------------

def compute_similarities(celebrity_files: List[gr.File], query_file: gr.File):
    """
    celebrity_files: list of uploaded celebrity files (0..5)
    query_file: single uploaded file

    返回：summary_text, gallery_images, gallery_captions
    """
    # 输入校验
    if not celebrity_files or len(celebrity_files) == 0:
        return "请上传 1 到 5 张明星照片（建议 5 张）。", [], []
    if query_file is None:
        return "请上传要比较的查询人脸照片。", [], []

    celeb_files = celebrity_files[:5]

    # 读取并处理查询图像
    try:
        # gradio 的 File 对象支持 .name (临时文件路径) 或 .read()
        if hasattr(query_file, 'name'):
            query_img = Image.open(query_file.name).convert('RGB')
        else:
            query_img = Image.open(io.BytesIO(query_file.read())).convert('RGB')
    except Exception:
        return "无法读取查询图片，请确认文件格式正确 (jpg/png)。", [], []

    query_tensor, query_cropped = extract_face_from_pil(query_img)
    query_emb = get_embedding(query_tensor)

    gallery_images = []
    gallery_captions = []
    results = []

    for idx, f in enumerate(celeb_files, start=1):
        try:
            if hasattr(f, 'name'):
                img = Image.open(f.name).convert('RGB')
            else:
                img = Image.open(io.BytesIO(f.read())).convert('RGB')
        except Exception:
            # 无法打开，跳过
            gallery_images.append(Image.new('RGB', (200, 200), color=(128, 128, 128)))
            gallery_captions.append(f"明星{idx}: 无法打开")
            results.append((idx, 0.0, None))
            continue

        face_tensor, cropped_pil = extract_face_from_pil(img)
        emb = get_embedding(face_tensor)
        sim = cosine_similarity(query_emb, emb)  # in [-1,1]
        percent = max(0.0, (sim + 1.0) / 2.0 * 100.0)

        # 准备展示图：优先显示裁剪的人脸，否则缩放原图
        if cropped_pil is not None:
            display_img = cropped_pil
        else:
            display_img = img.resize((200, 200))

        gallery_images.append(display_img)
        gallery_captions.append(f"明星{idx}: {percent:.2f}%")
        results.append((idx, percent, sim))

    # 按相似度降序生成文本摘要
    sorted_results = sorted(results, key=lambda x: (x[1] if x[1] is not None else -1), reverse=True)
    summary_lines = []
    for r in sorted_results:
        idx, pct, cosv = r
        if cosv is None:
            summary_lines.append(f"明星{idx} - 未能检测到人脸或无法计算")
        else:
            summary_lines.append(f"明星{idx} - 相似度: {pct:.2f}% (cos={cosv:.4f})")

    summary_text = "\n".join(summary_lines)

    # 查询图像展示（可选）——这里不单独返回查询图像，但可以在页面上添加
    return summary_text, gallery_images, gallery_captions

# -------------------- Gradio UI --------------------
with gr.Blocks(title="人脸相似度比较（facenet-pytorch）") as demo:
    gr.Markdown("""
    ## 人脸相似度比较
    上传 **最多 5 张** 明星照片，然后上传 **1 张** 查询人脸图片。应用会检测并裁剪人脸（若检测不到则回退到中心裁切），
    使用 InceptionResnetV1 (vggface2) 提取 embedding 并计算余弦相似度。第一次启动会进行模型预热以减少延迟。

    **依赖**: facenet-pytorch, torch, torchvision, gradio
    """)

    with gr.Row():
        with gr.Column(scale=1):
            celeb_input = gr.File(label="上传明星照片（最多5张）", file_count="multiple")
            query_input = gr.File(label="上传查询人脸照片（1张）", file_count="single")
            run_btn = gr.Button("比较相似度")
            run_note = gr.Markdown("提示：首次启动会进行预热，可能花费几秒钟。")

        with gr.Column(scale=1):
            out_text = gr.Textbox(label="相似度结果（按降序）", lines=6)
            gallery = gr.Gallery(label="明星面孔及相似度", columns=[3], height="auto")

    run_btn.click(fn=compute_similarities, inputs=[celeb_input, query_input], outputs=[out_text, gallery, gr.State()])

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # True为公网分享
        debug=True
    )
