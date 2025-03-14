from PIL import Image

def crop_image_by_percentage(image_path, output_path, top=0, right=0, bottom=0, left=0):
    """
    按百分比裁剪图片的四个边。

    :param image_path: 输入图片的路径
    :param output_path: 裁剪后图片的保存路径
    :param top: 裁剪顶部的百分比 (0~1, 如 0.1 表示裁剪 10%)
    :param right: 裁剪右边的百分比 (0~1)
    :param bottom: 裁剪底部的百分比 (0~1)
    :param left: 裁剪左边的百分比 (0~1)
    """
    # 打开图片
    image = Image.open(image_path)
    width, height = image.size

    # 根据百分比计算裁剪像素
    top_pixels = int(top * height)
    right_pixels = int(right * width)
    bottom_pixels = int(bottom * height)
    left_pixels = int(left * width)

    # 计算裁剪后的区域
    crop_box = (left_pixels, top_pixels, width - right_pixels, height - bottom_pixels)

    # 裁剪图片
    cropped_image = image.crop(crop_box)

    # 保存裁剪后的图片
    cropped_image.save(output_path)

if __name__ == "__main__":
# 示例用法
    crop_image_by_percentage("input.jpg", "output.jpg", top=0.1, right=0.1, bottom=0.1, left=0.1)
