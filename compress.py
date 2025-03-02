from PIL import Image
import os
import shutil
import io
import rawpy  # 需要安装 rawpy 库来处理 Raw 文件（如 .orf）

def compress_images(input_folder, output_folder, max_size=3*1024*1024):

    def is_image_file(file_path):
        """判断文件是否为图片"""
        image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"}
        raw_extensions = {".cr2", ".cr3", ".dng", ".nef", ".arw", ".sr2", ".srf", ".pef", ".raf", ".mmf", ".mos", ".kdc", ".er", ".orf"}
        _, ext = os.path.splitext(file_path)
        return ext.lower() in image_extensions or ext.lower() in raw_extensions

    def convert_orf_to_jpg(input_path, output_path):
        """将 .orf 文件转换为 .jpg 文件"""
        with rawpy.imread(input_path) as raw:
            rgb = raw.postprocess()  # 处理 Raw 数据
        with Image.fromarray(rgb) as img:
            img.save(output_path, "JPEG")  # 保存为 JPG 格式

    def adjust_image_size(input_path, output_path, max_size):
        """调整图像大小和质量以满足最大文件大小限制"""
        target_quality = 75  # 起始质量
        min_quality = 10  # 最低质量

        while True:
            # 打开图片
            with Image.open(input_path) as img:
                # 压缩图片并调整质量
                temp_buffer = io.BytesIO()
                img.save(temp_buffer, format=img.format, quality=target_quality)
                current_size = temp_buffer.getbuffer().nbytes

            if current_size <= max_size:  # 如果文件大小符合要求，保存并退出
                with open(output_path, "wb") as f:
                    f.write(temp_buffer.getvalue())
                return True
            else:  # 如果文件还是太大，降低质量
                if target_quality > min_quality:
                    target_quality -= 5
                else:
                    # 无法进一步降低质量，直接压缩到最低质量
                    img.save(output_path, format=img.format, quality=min_quality)
                    return True

    def compress_images(input_folder, output_folder, max_size=3 * 1024 * 1024):
        """压缩指定文件夹中的所有图片，保持文件夹结构"""
        # 确保输出文件夹存在
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # 遍历输入文件夹的所有文件和子文件夹
        for root, dirs, files in os.walk(input_folder):
            for file in files:
                input_file_path = os.path.join(root, file)
                output_file_path = input_file_path.replace(input_folder, output_folder)
                output_dir = os.path.dirname(output_file_path)
                os.makedirs(output_dir, exist_ok=True)

                # 判断文件是否为图片
                if is_image_file(input_file_path):
                    # 如果是 .orf 文件，转换为 .jpg
                    if os.path.splitext(input_file_path)[1].lower() == ".orf":
                        jpg_output_path = os.path.splitext(output_file_path)[0] + ".jpg"
                        try:
                            print(f"正在将 .orf 文件转换为 .jpg：{input_file_path}")
                            output_file_path = jpg_output_path
                            convert_orf_to_jpg(input_file_path, output_file_path)
                        except Exception as e:
                            print(f"转换失败：{input_file_path}，错误：{str(e)}")
                            continue
                    else:
                        # 如果生成的 .jpg 文件不存在，复制原始文件
                        shutil.copy2(input_file_path, output_file_path)

                    # 判断原图大小是否超过限制
                    if os.path.exists(output_file_path):
                        file_size = os.path.getsize(output_file_path)
                        if file_size > max_size:
                            # 如果原图过大，需要压缩
                            try:
                                temp_path = output_file_path + ".temp"
                                print(f"正在压缩文件：{output_file_path}")
                                adjust_image_size(output_file_path, temp_path, max_size)
                                shutil.move(temp_path, output_file_path)
                            except Exception as e:
                                print(f"压缩失败：{output_file_path}，错误：{str(e)}")
                        else:
                            # 原图大小未超过限制，直接复制
                            try:
                                pass
                            except Exception as e:
                                print(f"复制失败：{output_file_path}，错误：{str(e)}")
                else:
                    # 文件不是图片，复制到输出文件夹
                    try:
                        shutil.copy2(input_file_path, output_file_path)
                    except Exception as e:
                        print(f"复制非图片文件失败：{input_file_path}，错误：{str(e)}")