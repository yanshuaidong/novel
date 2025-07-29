import re
import os
from bs4 import BeautifulSoup

def extract_chapter_urls_from_html(html_file_path):
    """
    从HTML文件中提取所有章节的URL地址
    
    参数说明：
    html_file_path: HTML文件的路径
    
    返回值：
    list: 包含所有章节URL的列表
    """
    try:
        # 读取HTML文件
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 查找所有章节链接
        # 根据HTML结构，章节链接在 <li class="line3"><a href="/doupocangqiong/xxxxx.html">章节标题</a></li>
        chapter_links = []
        
        # 查找所有class为"line3"的li元素
        li_elements = soup.find_all('li', class_='line3')
        
        for li in li_elements:
            # 在每个li中查找a标签
            a_tag = li.find('a')
            if a_tag and a_tag.get('href'):
                href = a_tag.get('href')
                # 如果是相对路径，需要补充完整的域名
                if href.startswith('/doupocangqiong/'):
                    full_url = f"https://www.doupocangqiong.org{href}"
                    chapter_title = a_tag.get_text().strip()
                    chapter_links.append({
                        'url': full_url,
                        'title': chapter_title
                    })
        
        print(f"成功提取到 {len(chapter_links)} 个章节链接")
        return chapter_links
        
    except Exception as e:
        print(f"提取章节URL时出错: {str(e)}")
        return []

def save_urls_to_config(chapter_links, config_file_path='/Users/zxxk/ysd/Project/novel/py/config.py'):
    """
    将章节URL列表保存到config.py文件中
    
    参数说明：
    chapter_links: 章节链接列表，每个元素包含url和title
    config_file_path: config.py文件的路径
    """
    try:
        # 构造urls数组的Python代码
        urls_content = "urls = [\n"
        
        for chapter in chapter_links:
            urls_content += f'    "{chapter["url"]}",  # {chapter["title"]}\n'
        
        urls_content += "]\n"
        
        # 写入config.py文件
        with open(config_file_path, 'w', encoding='utf-8') as file:
            file.write(urls_content)
        
        print(f"成功将 {len(chapter_links)} 个URL保存到 {config_file_path}")
        return True
        
    except Exception as e:
        print(f"保存URLs到config文件时出错: {str(e)}")
        return False

def main():
    """
    主函数：从HTML文件提取章节URL并保存到config.py
    """
    print("=== 章节URL提取工具开始运行 ===")
    
    # HTML文件路径
    html_file_path = "/Users/zxxk/ysd/Project/novel/js/downloaded_pages/page_2025-07-29T02-48-43-637Z.html"
    
    # 检查HTML文件是否存在
    if not os.path.exists(html_file_path):
        print(f"错误：HTML文件不存在 - {html_file_path}")
        return
    
    # 提取章节URL
    chapter_links = extract_chapter_urls_from_html(html_file_path)
    
    if not chapter_links:
        print("未能提取到任何章节URL")
        return
    
    # 显示提取到的前几个章节信息
    print("\n前5个章节信息：")
    for i, chapter in enumerate(chapter_links[:5]):
        print(f"{i+1}. {chapter['title']}")
        print(f"   URL: {chapter['url']}")
    
    if len(chapter_links) > 5:
        print(f"... 还有 {len(chapter_links) - 5} 个章节")
    
    # 保存到config.py文件
    config_file_path = "/Users/zxxk/ysd/Project/novel/py/config.py"
    if save_urls_to_config(chapter_links, config_file_path):
        print(f"\n=== 处理完成 ===")
        print(f"共提取 {len(chapter_links)} 个章节URL")
        print(f"已保存到 {config_file_path}")
        print("现在可以运行 main.py 来下载所有章节内容")
    else:
        print("保存失败，请检查文件权限")

if __name__ == "__main__":
    main()
