#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多线程小说爬虫运行脚本
使用示例和配置说明
"""

from main import main, set_thread_count
from config import THREAD_CONFIG

def run_with_custom_settings():
    """使用自定义设置运行爬虫"""
    
    print("=== 多线程小说爬虫配置 ===")
    print(f"当前配置:")
    print(f"  - 线程数: {THREAD_CONFIG['max_workers']}")
    print(f"  - 请求延时: {THREAD_CONFIG['request_delay']} 秒")
    print(f"  - 请求超时: {THREAD_CONFIG['timeout']} 秒")
    print()
    
    # 询问用户是否要修改线程数
    try:
        user_input = input("是否要修改线程数？(当前: {}, 直接回车保持不变): ".format(THREAD_CONFIG['max_workers']))
        if user_input.strip():
            thread_count = int(user_input.strip())
            set_thread_count(thread_count)
            print()
    except ValueError:
        print("输入无效，使用默认线程数")
        print()
    except KeyboardInterrupt:
        print("\n用户取消操作")
        return
    
    # 开始爬取
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断爬取操作")
    except Exception as e:
        print(f"\n\n爬取过程中发生错误: {e}")

def run_fast_mode():
    """快速模式：使用更多线程，无延时"""
    print("=== 快速模式 ===")
    print("使用10个线程，无请求延时")
    
    # 临时修改配置
    original_workers = THREAD_CONFIG['max_workers']
    original_delay = THREAD_CONFIG['request_delay']
    
    THREAD_CONFIG['max_workers'] = 10
    THREAD_CONFIG['request_delay'] = 0
    
    try:
        main()
    finally:
        # 恢复原始配置
        THREAD_CONFIG['max_workers'] = original_workers
        THREAD_CONFIG['request_delay'] = original_delay

def run_safe_mode():
    """安全模式：使用较少线程，有延时"""
    print("=== 安全模式 ===")
    print("使用3个线程，1秒请求延时")
    
    # 临时修改配置
    original_workers = THREAD_CONFIG['max_workers']
    original_delay = THREAD_CONFIG['request_delay']
    
    THREAD_CONFIG['max_workers'] = 3
    THREAD_CONFIG['request_delay'] = 1.0
    
    try:
        main()
    finally:
        # 恢复原始配置
        THREAD_CONFIG['max_workers'] = original_workers
        THREAD_CONFIG['request_delay'] = original_delay

if __name__ == "__main__":
    print("多线程小说爬虫")
    print("=" * 50)
    print("请选择运行模式:")
    print("1. 自定义设置 (推荐)")
    print("2. 快速模式 (10线程，无延时)")
    print("3. 安全模式 (3线程，1秒延时)")
    print("4. 直接使用配置文件设置")
    print()
    
    try:
        choice = input("请输入选择 (1-4): ").strip()
        
        if choice == "1":
            run_with_custom_settings()
        elif choice == "2":
            run_fast_mode()
        elif choice == "3":
            run_safe_mode()
        elif choice == "4":
            main()
        else:
            print("无效选择，使用默认配置运行")
            main()
            
    except KeyboardInterrupt:
        print("\n\n程序已退出")
    except Exception as e:
        print(f"\n\n发生错误: {e}") 