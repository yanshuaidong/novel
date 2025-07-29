#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《斗破苍穹》小说章节汇总脚本
将novel_chapters目录下的所有章节文件合并成一个完整的小说文件
"""

import os
import re
from pathlib import Path

def extract_chapter_number(filename):
    """从文件名中提取章节号"""
    # 匹配形如 "1章" "123章" 等格式
    match = re.search(r'(\d+)章', filename)
    if match:
        return int(match.group(1))
    return float('inf')  # 非章节文件排到最后

def is_chapter_file(filename):
    """判断是否为章节文件"""
    # 检查是否包含"章"字且为txt文件
    return '章' in filename and filename.endswith('.txt')

def merge_novel_chapters():
    """合并所有章节文件"""
    # 设置路径
    chapters_dir = Path("novel_chapters")
    output_file = "《斗破苍穹》.txt"
    
    if not chapters_dir.exists():
        print(f"错误：找不到章节目录 {chapters_dir}")
        return
    
    # 获取所有章节文件
    all_files = list(chapters_dir.glob("*.txt"))
    chapter_files = [f for f in all_files if is_chapter_file(f.name)]
    
    # 按章节号排序
    chapter_files.sort(key=lambda x: extract_chapter_number(x.name))
    
    print(f"找到 {len(chapter_files)} 个章节文件")
    
    # 合并文件
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # 写入标题
        outfile.write("《斗破苍穹》\n")
        outfile.write("=" * 50 + "\n\n")
        
        for i, chapter_file in enumerate(chapter_files, 1):
            print(f"正在处理第 {i} 个文件: {chapter_file.name}")
            
            try:
                with open(chapter_file, 'r', encoding='utf-8') as infile:
                    content = infile.read().strip()
                    
                    # 从文件名提取章节标题
                    chapter_title = chapter_file.stem  # 去掉.txt扩展名
                    
                    # 写入章节标题（用作分隔符）
                    outfile.write(f"\n{'=' * 5}\n")
                    outfile.write(f"{chapter_title}\n")
                    outfile.write(f"{'=' * 5}\n\n")
                    
                    # 写入章节内容
                    outfile.write(content)
                    outfile.write("\n\n")
                    
            except Exception as e:
                print(f"处理文件 {chapter_file.name} 时出错: {e}")
                continue
    
    print(f"\n合并完成！输出文件：{output_file}")
    print(f"共处理了 {len(chapter_files)} 个章节")

def show_chapter_list():
    """显示章节列表预览"""
    chapters_dir = Path("novel_chapters")
    
    if not chapters_dir.exists():
        print(f"错误：找不到章节目录 {chapters_dir}")
        return
    
    all_files = list(chapters_dir.glob("*.txt"))
    chapter_files = [f for f in all_files if is_chapter_file(f.name)]
    chapter_files.sort(key=lambda x: extract_chapter_number(x.name))
    
    print("章节列表预览：")
    print("-" * 60)
    
    for i, chapter_file in enumerate(chapter_files[:10], 1):  # 只显示前10个
        chapter_num = extract_chapter_number(chapter_file.name)
        print(f"{i:3d}. 第{chapter_num}章 - {chapter_file.name}")
    
    if len(chapter_files) > 10:
        print(f"... 还有 {len(chapter_files) - 10} 个章节")
    
    print(f"\n总共找到 {len(chapter_files)} 个章节文件")

if __name__ == "__main__":
    print("《斗破苍穹》章节汇总工具")
    print("=" * 40)
    
    # 显示章节列表
    show_chapter_list()
    
    # 询问是否继续
    response = input("\n是否开始合并章节？(y/n): ").strip().lower()
    
    if response in ['y', 'yes', '是', '']:
        merge_novel_chapters()
    else:
        print("操作已取消")
