#!/usr/bin/env python3
"""
手动上传Markdown文件到Supabase存储桶脚本
"""

import supabase
import os
import glob
import hashlib
from datetime import datetime

# Supabase配置
SUPABASE_URL = "https://lyokdigjpgzgloyhkmkm.supabase.co"
# 请确保使用正确的服务角色密钥（service role key）而不是匿名密钥
# 可以选择使用硬编码密钥（用于测试）或手动输入
USE_HARDCODED_KEY = True  # 设置为True以使用硬编码密钥

if USE_HARDCODED_KEY:
    # 硬编码的服务角色密钥（仅用于测试环境）
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx5b2tkaWdqcGd6Z2xveWhrbWttIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDcwNzk3OSwiZXhwIjoyMDgwMjgzOTc5fQ.mGBP2vN7hXnWW8aN246zzwUUSXiqXyemR8kn-LMUI88"
else:
    SUPABASE_KEY = input("请输入Supabase服务角色密钥（service role key）: ").strip()

BUCKET_NAME = "notes"
NOTES_DIR = "assets/notes"

# 初始化Supabase客户端
try:
    supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✓ Supabase客户端初始化成功")
except Exception as e:
    print(f"✗ Supabase客户端初始化失败: {e}")
    print("请检查您的URL和密钥是否正确")
    exit(1)

# 生成英文/哈希文件名
def generate_slug(file_name):
    """生成英文/哈希文件名"""
    # 移除文件扩展名
    name_without_ext = os.path.splitext(file_name)[0]
    
    # 生成哈希值
    hash_value = hashlib.md5(name_without_ext.encode('utf-8')).hexdigest()[:10]
    
    # 构建最终文件名（保留原扩展名）
    ext = os.path.splitext(file_name)[1]
    return f"file_{hash_value}{ext}"

def read_markdown_files():
    """读取本地Markdown文件"""
    print("\n=== 读取本地Markdown文件 ===")
    
    # 检查目录是否存在
    if not os.path.exists(NOTES_DIR):
        print(f"✗ 目录 {NOTES_DIR} 不存在")
        return []
    
    # 获取所有Markdown文件
    md_files = glob.glob(os.path.join(NOTES_DIR, "*.md"))
    
    files = []
    for file_path in md_files:
        file_name = os.path.basename(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 生成标题（去掉.md后缀）
        title = file_name.replace('.md', '')
        # 生成安全的英文文件名
        safe_file_name = generate_slug(file_name)
        # 生成文件路径
        file_path_in_bucket = f"{safe_file_name}"  # 直接上传到存储桶根目录
        # 生成文件URL
        file_url = f"https://lyokdigjpgzgloyhkmkm.supabase.co/storage/v1/object/public/notes/{file_path_in_bucket}"
        
        files.append({
            "original_name": file_name,
            "name": safe_file_name,
            "display_name": file_name,
            "title": title,
            "file_path": file_path_in_bucket,
            "file_url": file_url,
            "content": content
        })
    
    print(f"✓ 读取了 {len(files)} 个Markdown文件")
    for file in files:
        print(f"  - {file['original_name']} -> {file['name']}")
    
    return files

def upload_files_to_storage(files):
    """上传文件到Storage"""
    print("\n=== 上传文件到Storage ===")
    
    if not files:
        print("✗ 没有文件需要上传")
        return []
    
    uploaded_files = []
    
    for file in files:
        try:
            # 获取存储桶引用
            bucket = supabase_client.storage.from_(BUCKET_NAME)
            
            # 检查文件是否已存在
            try:
                bucket.download(file["file_path"])
                print(f"⚠ 文件已存在，跳过: {file['name']}")
                uploaded_files.append(file)
                continue
            except:
                pass  # 文件不存在，继续上传
            
            # 上传文件到Storage
            result = bucket.upload(
                path=file["file_path"],
                file=file["content"].encode('utf-8'),
                file_options={"content-type": "text/markdown"}
            )
            
            uploaded_files.append(file)
            print(f"✓ 文件上传成功: {file['original_name']} -> {file['name']}")
        except Exception as e:
            print(f"✗ 上传文件失败 {file['original_name']}: {e}")
            print("  跳过此文件，继续上传其他文件")
    
    print(f"\n✓ 成功上传 {len(uploaded_files)} 个文件")
    return uploaded_files

def insert_file_indexes(files):
    """插入文件索引到数据库"""
    print("\n=== 插入文件索引到数据库 ===")
    
    if not files:
        print("✗ 没有文件索引需要插入")
        return []
    
    inserted_files = []
    
    for file in files:
        try:
            # 检查文件是否已存在
            response = supabase_client.table("markdown_files").select("id").eq("name", file["name"]).limit(1).execute()
            
            if response.data and len(response.data) > 0:
                print(f"⚠ 文件索引已存在，跳过: {file['name']}")
                inserted_files.append(file)
                continue
            
            # 插入文件索引
            supabase_client.table("markdown_files").insert({
                "name": file["name"],
                "display_name": file["display_name"],
                "title": file["title"],
                "file_path": file["file_path"],
                "file_url": file["file_url"]
            }).execute()
            
            inserted_files.append(file)
            print(f"✓ 文件索引插入成功: {file['name']}")
        except Exception as e:
            print(f"✗ 插入文件索引失败 {file['name']}: {e}")
    
    print(f"\n✓ 成功插入 {len(inserted_files)} 个文件索引")
    return inserted_files

def main():
    """主函数"""
    print("=== 手动上传Markdown文件到Supabase存储桶 ===")
    print(f"Supabase URL: {SUPABASE_URL}")
    print(f"Storage桶名称: {BUCKET_NAME}")
    print(f"本地文件目录: {NOTES_DIR}")
    print()
    
    # 读取本地Markdown文件
    files = read_markdown_files()
    
    if not files:
        print("\n没有文件需要处理，程序退出")
        return
    
    # 确认上传
    confirm = input("\n是否要上传这些文件？(y/n): ").strip().lower()
    if confirm != 'y':
        print("上传取消，程序退出")
        return
    
    # 上传文件到Storage
    uploaded_files = upload_files_to_storage(files)
    
    # 确认插入索引
    if uploaded_files:
        confirm = input("\n是否要将文件索引插入到数据库？(y/n): ").strip().lower()
        if confirm == 'y':
            # 插入文件索引到数据库
            insert_file_indexes(uploaded_files)
    
    print("\n=== 上传完成 ===")
    print("请登录到Supabase控制台检查上传结果：")
    print("1. 存储桶: https://app.supabase.com/project/lyokdigjpgzgloyhkmkm/storage/buckets/notes")
    print("2. 数据库表: https://app.supabase.com/project/lyokdigjpgzgloyhkmkm/database/tables/public.markdown_files")

if __name__ == "__main__":
    main()
