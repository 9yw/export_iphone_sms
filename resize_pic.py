from PIL import Image
import io

def resize_image(file_data, file_size, file_type, max_size_kb=500):
    img = Image.open(io.BytesIO(file_data))
    img_format = file_type.split('/')[-1].upper()
    quality = 95

    # 如果图像是 RGBA 模式且目标格式是 JPEG，则转换为 RGB 模式
    if img_format == 'JPEG' and img.mode == 'RGBA':
        img = img.convert('RGB')

    output = io.BytesIO()
    while file_size > max_size_kb * 1024 and quality > 10:
        img.save(output, format=img_format, quality=quality)
        file_size = output.tell()
        output.seek(0)
        quality -= 5

    return output.getvalue(),file_size

# Example usage:
# with open('path/to/large/image.jpg', 'rb') as f:
#     file_data = f.read()
# resized_data = resize_image(file_data, len(file_data), 'image/jpeg')
