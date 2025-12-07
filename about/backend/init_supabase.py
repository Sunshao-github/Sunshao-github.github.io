#!/usr/bin/env python3
"""
初始化Supabase表并插入数据
"""

import supabase
import os
import glob
from datetime import datetime

# Supabase配置
SUPABASE_URL = "https://lyokdigjpgzgloyhkmkm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx5b2tkaWdqcGd6Z2xveWhrbWttIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ3MDc5NzksImV4cCI6MjA4MDI4Mzk3OX0.mGBP2vN7hXnWW8aN246zzwUUSXiqXyemR8kn-LMUI88"

# 初始化Supabase客户端
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

# Markdown文件目录
NOTES_DIR = "assets/notes"

def read_markdown_files():
    """读取本地Markdown文件"""
    files = []
    
    # 检查目录是否存在
    if not os.path.exists(NOTES_DIR):
        print(f"目录 {NOTES_DIR} 不存在")
        return files
    
    # 获取所有Markdown文件
    md_files = glob.glob(os.path.join(NOTES_DIR, "*.md"))
    
    for file_path in md_files:
        file_name = os.path.basename(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        files.append({
            "name": file_name,
            "content": content
        })
    
    print(f"读取了 {len(files)} 个Markdown文件")
    return files

def insert_files_to_supabase(files):
    """将文件插入到Supabase"""
    if not files:
        print("没有文件需要插入")
        return
    
    for file in files:
        try:
            # 检查文件是否已存在
            response = supabase_client.table("markdown_files").select("id").eq("name", file["name"]).single().execute()
            
            if response.data:
                print(f"文件 {file['name']} 已存在，跳过")
            else:
                # 插入新文件
                supabase_client.table("markdown_files").insert({
                    "name": file["name"],
                    "content": file["content"],
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }).execute()
                print(f"文件 {file['name']} 插入成功")
        except Exception as e:
            print(f"处理文件 {file['name']} 时出错: {e}")

def main():
    """主函数"""
    print("初始化Supabase表并插入数据...")
    
    # 读取本地Markdown文件
    files = read_markdown_files()
    
    # 将文件插入到Supabase
    insert_files_to_supabase(files)
    
    print("初始化完成！")

if __name__ == "__main__":
    main()
