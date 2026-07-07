import cv2
import numpy as np
import os
import argparse
import glob

def pack_16bit_to_rg(input_path, output_dir, mask_path=None):
    """
    将 16-bit 灰度 TIFF 图像打包至 8-bit PNG 的 R 通道（高8位）和 G 通道（低8位）。
    B 通道可选择性塞入一个外部 8-bit 遮罩图片，默认为 0。
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 判断输入是单个文件还是目录
    if os.path.isfile(input_path):
        tif_files = [input_path]
    else:
        tif_files = glob.glob(os.path.join(input_path, '*.tif')) + glob.glob(os.path.join(input_path, '*.tiff'))
        
    if not tif_files:
        print(f"没有找到任何 TIFF 文件: {input_path}")
        return

    print(f"开始处理，共找到 {len(tif_files)} 个 TIFF 文件...")

    for file_path in tif_files:
        # 以原始通道和原始深度（16-bit）读取图像
        img_16bit = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
        
        if img_16bit is None:
            print(f"无法读取文件: {file_path}")
            continue

        # 如果读取进来有多通道，先转成 16-bit 单通道灰度图
        if len(img_16bit.shape) == 3:
            print(f"警告: {file_path} 是多通道图像，正在转换为单通道灰度图...")
            img_16bit = cv2.cvtColor(img_16bit, cv2.COLOR_BGR2GRAY)

        if img_16bit.dtype != np.uint16:
            # 如果是 8-bit，尝试转换成 16-bit（虽然没有实际精度提升，但确保脚本不崩溃）
            print(f"警告: {file_path} 实际为 {img_16bit.dtype}，将升轨至 uint16 处理...")
            img_16bit = (img_16bit.astype(np.uint16) << 8)

        # 位运算拆包：高 8 位与低 8 位
        high_8 = (img_16bit >> 8).astype(np.uint8)
        low_8 = (img_16bit & 0xFF).astype(np.uint8)

        h, w = img_16bit.shape
        # 构建标准的 3 通道 8-bit 图像 (OpenCV 默认 BGR)
        # R = channel 2 (high_8)
        # G = channel 1 (low_8)
        # B = channel 0 (mask 或 0)
        packed_img = np.zeros((h, w, 3), dtype=np.uint8)
        
        packed_img[:, :, 2] = high_8  # R
        packed_img[:, :, 1] = low_8   # G

        # 处理可选的 B 通道 Mask 遮罩
        if mask_path:
            # 寻找对应的遮罩文件。如果是目录，尝试寻找同名文件
            current_mask_file = None
            if os.path.isdir(mask_path):
                base_name_no_ext = os.path.splitext(os.path.basename(file_path))[0]
                # 尝试匹配 png, jpg, jpeg, tif 等常见格式的 mask
                for ext in ['.png', '.jpg', '.jpeg', '.tif', '.tiff']:
                    possible_mask = os.path.join(mask_path, base_name_no_ext + ext)
                    if os.path.exists(possible_mask):
                        current_mask_file = possible_mask
                        break
            elif os.path.isfile(mask_path):
                current_mask_file = mask_path

            if current_mask_file:
                mask_img = cv2.imread(current_mask_file, cv2.IMREAD_GRAYSCALE)
                if mask_img is not None:
                    # 缩放到与原图高度图相同的尺寸
                    if mask_img.shape != (h, w):
                        mask_img = cv2.resize(mask_img, (w, h), interpolation=cv2.INTER_LINEAR)
                    packed_img[:, :, 0] = mask_img  # B
                    print(f"  -> 成功嵌入遮罩: {os.path.basename(current_mask_file)}")
                else:
                    print(f"  -> 警告: 无法读取遮罩文件: {current_mask_file}")
            else:
                print(f"  -> 未找到对应的遮罩文件，B通道填充为 0")

        # 输出为无损 PNG
        filename = os.path.basename(file_path)
        out_name = os.path.splitext(filename)[0] + '_packed.png'
        out_path = os.path.join(output_dir, out_name)
        
        cv2.imwrite(out_path, packed_img, [cv2.IMWRITE_PNG_COMPRESSION, 9])
        print(f"成功打包: {out_name} -> {out_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="16-bit 灰度 TIFF 图像打包至 8-bit PNG RG 通道小工具")
    parser.add_argument("-i", "--input", default=".", help="输入 16-bit TIFF 文件或包含 TIFF 的文件夹路径 (默认当前路径)")
    parser.add_argument("-o", "--output", default="./output_pngs", help="输出打包后 PNG 的目标文件夹路径 (默认 ./output_pngs)")
    parser.add_argument("-m", "--mask", default=None, help="可选：遮罩文件或包含对应遮罩文件的文件夹路径 (放入 B 通道)")
    
    args = parser.parse_args()
    pack_16bit_to_rg(args.input, args.output, args.mask)
