import os
import shutil
import torch
from torch.nn.functional import cosine_similarity
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

# 加载预训练的CLIP模型和处理器
print("正在加载模型...")
model_name = "openai/clip-vit-large-patch14"
model = CLIPModel.from_pretrained(model_name)
processor = CLIPProcessor.from_pretrained(model_name)

# 将模型移动到GPU（如果可用）
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

def initialize_model(categories):
    text_input = processor(text=categories, return_tensors="pt", padding=True).to(device)
    # 计算文本特征
    with torch.no_grad():
        text_features = model.get_text_features(**text_input).float()
    return text_features

def get_image_embedding(image_path):
    try:
        image = Image.open(image_path).convert("RGB")
        image_input = processor(images=image, return_tensors="pt").to(device)
        with torch.no_grad():
            image_features = model.get_image_features(**image_input).float()
        return image_features
    except Exception as e:
        print(f"Error processing image {image_path}: {str(e)}")
        return None

def classify_image(image_path, text_features, categories):
    image_features = get_image_embedding(image_path)
    if image_features is None:
        return "其他"

    # 对图像特征向量进行L2归一化处理，确保每个向量的长度为1
    image_features /= image_features.norm(dim=-1, keepdim=True)
    # 对文本特征向量进行L2归一化处理，确保每个向量的长度为1
    text_features /= text_features.norm(dim=-1, keepdim=True)

    # 计算相似度
    similarity = (text_features @ image_features.T).cpu().numpy()

    max_similarity = similarity[0].max()
    predicted_class = categories[similarity[0].argmax()]
    if max_similarity < 0.5:
        return "其他"
    else:
        return predicted_class

def classify_images(dataset_path, output_path, text_features, categories):
    for category in categories:
        os.makedirs(os.path.join(output_path, category), exist_ok=True)

    for root, _, files in os.walk(dataset_path):
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                image_path = os.path.join(root, file)
                try:
                    predicted_class = classify_image(image_path, text_features, categories)
                    output_file = os.path.join(output_path, predicted_class, file)
                    output_dir = os.path.dirname(output_file)
                    # 创建文件所在的目录
                    os.makedirs(output_dir, exist_ok=True)
                    if predicted_class == "其他":
                        print(f"{file}归档为’其他‘")
                    else:
                        print(f"Moved {file} ==> {predicted_class}")
                    shutil.move(image_path, output_file)
                except Exception as e:
                    print(f"Error moving file {file}: {e}")

# 以下是示例调用，可根据GUI程序的需要进行调整
if __name__ == "__main__":
    # 模拟GUI输入的分类类别
    input_categories = input("请输入分类类别，多个类别用逗号分隔：")
    categories = [category.strip() for category in input_categories.split(',')]
    text_features = initialize_model(categories)

    # 模拟GUI输入的图片文件夹路径和输出文件夹路径
    dataset_path = input("请输入图片文件夹路径：")
    output_path = input("请输入输出文件夹路径：")

    classify_images(dataset_path, output_path, text_features, categories)
