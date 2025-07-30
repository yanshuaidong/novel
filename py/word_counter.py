#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说章节字数统计工具
用于统计指定txt文件的字数
"""

import os
import sys


def count_words_in_file(file_path):
    """
    统计文件中的字数
    
    Args:
        file_path (str): 文件路径
        
    Returns:
        dict: 包含字符数、中文字符数、英文单词数等统计信息
    """
    try:
        # 尝试不同的编码方式读取文件
        encodings = ['utf-8', 'gbk', 'gb2312', 'ascii']
        content = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    content = file.read()
                print(f"文件编码: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            print("错误: 无法读取文件，请检查文件编码")
            return None
            
        # 统计各种字数
        total_chars = len(content)  # 总字符数（包括空格、换行等）
        
        # 统计中文字符数
        chinese_chars = 0
        for char in content:
            if '\u4e00' <= char <= '\u9fff':  # 中文字符范围
                chinese_chars += 1
        
        # 统计英文字母数
        english_chars = 0
        for char in content:
            if char.isalpha() and ord(char) < 128:  # ASCII英文字母
                english_chars += 1
        
        # 统计数字数
        digit_chars = 0
        for char in content:
            if char.isdigit():
                digit_chars += 1
        
        # 统计英文单词数（简单按空格分割）
        words = content.split()
        english_words = len([word for word in words if any(c.isalpha() and ord(c) < 128 for c in word)])
        
        # 统计行数
        lines = content.split('\n')
        total_lines = len(lines)
        non_empty_lines = len([line for line in lines if line.strip()])
        
        # 去除空白字符后的总字符数
        content_without_whitespace = ''.join(content.split())
        effective_chars = len(content_without_whitespace)
        
        return {
            'total_chars': total_chars,
            'effective_chars': effective_chars,
            'chinese_chars': chinese_chars,
            'english_chars': english_chars,
            'digit_chars': digit_chars,
            'english_words': english_words,
            'total_lines': total_lines,
            'non_empty_lines': non_empty_lines,
            'file_size': os.path.getsize(file_path)
        }
        
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{file_path}'")
        return None
    except Exception as e:
        print(f"错误: 读取文件时出现问题 - {e}")
        return None


def print_statistics(stats, file_path):
    """
    打印统计结果
    
    Args:
        stats (dict): 统计信息字典
        file_path (str): 文件路径
    """
    print("\n" + "="*50)
    print(f"文件: {file_path}")
    print("="*50)
    print(f"总字符数:     {stats['total_chars']:,}")
    print(f"有效字符数:   {stats['effective_chars']:,} (去除空格、换行等)")
    print(f"中文字符数:   {stats['chinese_chars']:,}")
    print(f"英文字母数:   {stats['english_chars']:,}")
    print(f"数字字符数:   {stats['digit_chars']:,}")
    print(f"英文单词数:   {stats['english_words']:,}")
    print(f"总行数:       {stats['total_lines']:,}")
    print(f"非空行数:     {stats['non_empty_lines']:,}")
    print(f"文件大小:     {stats['file_size']:,} 字节")
    print("="*50)
    
    # 给出小说字数的建议
    if stats['chinese_chars'] > 0:
        print(f"\n📖 小说字数统计建议:")
        print(f"   - 按中文字符计算: {stats['chinese_chars']:,} 字")
        if stats['chinese_chars'] < 2000:
            print(f"   - 篇幅: 短篇 (一般2000字以下)")
        elif stats['chinese_chars'] < 10000:
            print(f"   - 篇幅: 中篇章节 (2000-10000字)")
        else:
            print(f"   - 篇幅: 长篇章节 (10000字以上)")


def main():
    """
    主函数
    """
    print("📚 小说章节字数统计工具")
    print("-" * 30)
    
    # 如果命令行提供了文件路径参数
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # 交互式输入文件路径
        file_path = input("请输入要统计的文件路径 (例如: 抄/2章节.txt): ").strip()
    
    # 如果是相对路径，尝试在当前目录查找
    if not os.path.isabs(file_path) and not os.path.exists(file_path):
        # 尝试在项目根目录查找
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        full_path = os.path.join(parent_dir, file_path)
        if os.path.exists(full_path):
            file_path = full_path
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"❌ 错误: 文件 '{file_path}' 不存在")
        print("请检查文件路径是否正确")
        return
    
    # 统计字数
    print(f"\n正在统计文件: {file_path}")
    stats = count_words_in_file(file_path)
    
    if stats:
        print_statistics(stats, file_path)
    
    # 询问是否继续统计其他文件
    while True:
        choice = input("\n是否要统计其他文件? (y/n): ").strip().lower()
        if choice in ['y', 'yes', '是', 'Y']:
            file_path = input("请输入要统计的文件路径: ").strip()
            if os.path.exists(file_path):
                stats = count_words_in_file(file_path)
                if stats:
                    print_statistics(stats, file_path)
            else:
                print(f"❌ 文件 '{file_path}' 不存在")
        else:
            break
    
    print("\n感谢使用小说字数统计工具! 📖")


if __name__ == "__main__":
    main()