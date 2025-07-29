#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说章节文件名批量重命名工具
将汉字章节数字转换为阿拉伯数字

例如：
- "地两百四十三章 击杀大斗师！" -> "243章 击杀大斗师！"
- "第八百二十八章  分尸【第二更！】" -> "828章  分尸【第二更！】"
"""

import os
import re
from pathlib import Path


def chinese_to_arabic(chinese_num_str):
    """
    将汉字数字转换为阿拉伯数字
    
    Args:
        chinese_num_str (str): 汉字数字字符串
        
    Returns:
        int: 转换后的阿拉伯数字
    """
    # 汉字数字映射表
    chinese_digits = {
        '零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
        '六': 6, '七': 7, '八': 8, '九': 9, '两': 2
    }
    
    # 去掉可能的前缀"第"和后缀"章"
    chinese_num_str = chinese_num_str.replace('第', '').replace('章', '')
    
    if not chinese_num_str:
        return 0
    
    # 如果已经是阿拉伯数字，直接返回
    if chinese_num_str.isdigit():
        return int(chinese_num_str)
    
    result = 0
    current = 0
    
    i = 0
    while i < len(chinese_num_str):
        char = chinese_num_str[i]
        
        if char in chinese_digits:
            current = chinese_digits[char]
        elif char == '十':
            if current == 0:  # 处理"十"开头的情况，如"十五"
                current = 1
            current *= 10
            # 检查是否后面还有数字
            if i + 1 < len(chinese_num_str) and chinese_num_str[i + 1] in chinese_digits:
                i += 1
                current += chinese_digits[chinese_num_str[i]]
            result += current
            current = 0
        elif char == '百':
            if current == 0:
                current = 1
            current *= 100
            # 检查后面是否有十位数
            if i + 1 < len(chinese_num_str):
                remaining = chinese_num_str[i + 1:]
                if remaining.startswith('零') and len(remaining) > 1:
                    # 处理"百零X"的情况
                    i += 2  # 跳过"零"
                    if i < len(chinese_num_str) and chinese_num_str[i] in chinese_digits:
                        current += chinese_digits[chinese_num_str[i]]
                elif remaining[0] in chinese_digits:
                    # 处理"百X"的情况（X是个位数）
                    i += 1
                    current += chinese_digits[chinese_num_str[i]]
                elif remaining.startswith('十'):
                    # 处理"百十X"或"百一十X"等情况
                    continue  # 让下一轮循环处理"十"
            result += current
            current = 0
        elif char == '千':
            if current == 0:
                current = 1
            current *= 1000
            result += current
            current = 0
        elif char == '万':
            if current == 0 and result == 0:
                current = 1
            result = (result + current) * 10000
            current = 0
        
        i += 1
    
    result += current
    return result


def extract_chapter_info(filename):
    """
    从文件名中提取章节信息
    
    Args:
        filename (str): 文件名
        
    Returns:
        tuple: (章节数字, 剩余部分) 或 (None, None) 如果不匹配
    """
    # 匹配模式：以"第"或"地"开头，包含汉字数字，以"章"结尾
    patterns = [
        r'^(第[零一二三四五六七八九十百千万两]+章)\s*(.*)',  # 第xxx章
        r'^(地[零一二三四五六七八九十百千万两]+章)\s*(.*)',  # 地xxx章（可能是"第"的错别字）
    ]
    
    for pattern in patterns:
        match = re.match(pattern, filename)
        if match:
            chapter_part = match.group(1)
            remaining_part = match.group(2)
            
            # 提取汉字数字部分
            chinese_num_match = re.search(r'[零一二三四五六七八九十百千万两]+', chapter_part)
            if chinese_num_match:
                chinese_num = chinese_num_match.group()
                arabic_num = chinese_to_arabic(chinese_num)
                return arabic_num, remaining_part
    
    return None, None


def rename_files(directory_path, dry_run=True):
    """
    批量重命名文件
    
    Args:
        directory_path (str): 目录路径
        dry_run (bool): 是否为试运行模式（只显示结果，不实际重命名）
    """
    directory = Path(directory_path)
    
    if not directory.exists():
        print(f"错误：目录 {directory_path} 不存在")
        return
    
    renamed_count = 0
    error_count = 0
    
    print(f"{'=' * 60}")
    print(f"{'试运行模式' if dry_run else '实际重命名模式'}")
    print(f"处理目录: {directory_path}")
    print(f"{'=' * 60}")
    
    # 获取所有.txt文件
    txt_files = list(directory.glob("*.txt"))
    
    for file_path in txt_files:
        filename = file_path.name
        
        # 提取章节信息
        chapter_num, remaining_part = extract_chapter_info(filename)
        
        if chapter_num is not None:
            # 构造新文件名
            new_filename = f"{chapter_num}章 {remaining_part}" if remaining_part else f"{chapter_num}章.txt"
            if not new_filename.endswith('.txt'):
                new_filename += '.txt'
            
            # 去掉多余的空格
            new_filename = re.sub(r'\s+', ' ', new_filename).strip()
            
            if filename != new_filename:
                print(f"原文件名: {filename}")
                print(f"新文件名: {new_filename}")
                
                if not dry_run:
                    try:
                        new_file_path = file_path.parent / new_filename
                        
                        # 检查新文件名是否已存在
                        if new_file_path.exists():
                            print(f"  警告: 目标文件已存在，跳过重命名")
                            error_count += 1
                        else:
                            file_path.rename(new_file_path)
                            print(f"  ✓ 重命名成功")
                            renamed_count += 1
                    except Exception as e:
                        print(f"  ✗ 重命名失败: {e}")
                        error_count += 1
                else:
                    print(f"  → 将会重命名")
                    renamed_count += 1
                
                print("-" * 40)
            else:
                print(f"跳过（无需重命名）: {filename}")
    
    print(f"\n{'=' * 60}")
    print(f"处理完成!")
    print(f"{'预计' if dry_run else '实际'}重命名文件数: {renamed_count}")
    if error_count > 0:
        print(f"错误/跳过文件数: {error_count}")
    print(f"总文件数: {len(txt_files)}")
    print(f"{'=' * 60}")


def main():
    """主函数"""
    # 设置小说章节目录路径
    novel_chapters_dir = "novel_chapters"
    
    print("小说章节文件名批量重命名工具")
    print("=" * 60)
    
    # 检查目录是否存在
    if not os.path.exists(novel_chapters_dir):
        print(f"错误：目录 {novel_chapters_dir} 不存在")
        print("请确保该脚本在正确的目录中运行")
        return
    
    # 首先进行试运行
    print("\n1. 试运行模式 - 预览重命名结果")
    rename_files(novel_chapters_dir, dry_run=True)
    
    # 询问用户是否继续
    while True:
        choice = input("\n是否执行实际重命名？(y/n): ").strip().lower()
        if choice in ['y', 'yes', '是']:
            print("\n2. 执行实际重命名")
            rename_files(novel_chapters_dir, dry_run=False)
            break
        elif choice in ['n', 'no', '否']:
            print("取消重命名操作")
            break
        else:
            print("请输入 y 或 n")


# 测试函数
def test_chinese_to_arabic():
    """测试汉字数字转换功能"""
    test_cases = [
        ("二", 2),
        ("五", 5),
        ("十", 10),
        ("十五", 15),
        ("二十", 20),
        ("二十三", 23),
        ("一百", 100),
        ("一百零五", 105),
        ("一百二十", 120),
        ("两百四十三", 243),
        ("两百八十八", 288),
        ("两百八十二", 282),
        ("三百", 300),
        ("五百五十八", 558),
        ("六百零五", 605),
        ("八百二十八", 828),
        ("一千", 1000),
        ("一千四百零一", 1401),
        ("一千六百二十三", 1623),
        ("九千九百九十九", 9999),
    ]
    
    print("测试汉字数字转换功能:")
    print("-" * 30)
    
    for chinese, expected in test_cases:
        result = chinese_to_arabic(chinese)
        status = "✓" if result == expected else "✗"
        print(f"{status} {chinese} -> {result} (期望: {expected})")


if __name__ == "__main__":
    # 如果需要测试转换功能，取消下面的注释
    # test_chinese_to_arabic()
    # print()
    
    main()
