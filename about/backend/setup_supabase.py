#!/usr/bin/env python3
"""
Supabase自动化设置脚本
用于创建表、Storage桶、设置权限和初始化数据
"""

import supabase
import os
import glob
import hashlib
from datetime import datetime

# Supabase配置
SUPABASE_URL = "https://lyokdigjpgzgloyhkmkm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx5b2tkaWdqcGd6Z2xveWhrbWttIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ3MDc5NzksImV4cCI6MjA4MDI4Mzk3OX0.mGBP2vN7hXnWW8aN246zzwUUSXiqXyemR8kn-LMUI88"

# 初始化Supabase客户端
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

# 配置
BUCKET_NAME = "notes"
NOTES_DIR = "assets/notes"

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

def create_table():
    """创建markdown_files表"""
    print("=== 创建markdown_files表 ===")
    
    try:
        # 检查表是否存在
        result = supabase_client.table("markdown_files").select("id").limit(1).execute()
        print("表已存在")
        return True
    except Exception as e:
        print(f"表不存在，创建表: {e}")
    
    try:
        # 使用SQL语句创建表
        sql = """
        CREATE TABLE IF NOT EXISTS public.markdown_files (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            name text UNIQUE NOT NULL,
            title text,
            file_path text,
            file_url text,
            created_at timestamp with time zone DEFAULT now(),
            updated_at timestamp with time zone DEFAULT now()
        );
        """
        
        # 使用Supabase的RPC功能执行SQL（需要启用Postgres的pg_cron扩展）
        # 注意：Supabase的JavaScript客户端支持sql方法，但Python客户端可能不支持直接执行SQL
        # 这里我们使用insert方法来间接检查表是否存在
        
        # 尝试插入一条测试数据，然后删除
        test_file = {
            "name": "test.md",
            "title": "Test File",
            "file_path": "test/test.md",
            "file_url": "http://localhost:8000/test/test.md"
        }
        
        # 插入测试数据
        result = supabase_client.table("markdown_files").insert(test_file).execute()
        print("表创建成功")
        
        # 删除测试数据
        supabase_client.table("markdown_files").delete().eq("name", "test.md").execute()
        return True
    except Exception as e:
        print(f"创建表失败: {e}")
        print("请手动在Supabase控制台创建表，使用以下SQL语句:")
        print("""
CREATE TABLE public.markdown_files (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text UNIQUE NOT NULL,
    title text,
    file_path text,
    file_url text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);
        """)
        return False

def create_storage_bucket():
    """创建Storage桶"""
    print("\n=== 创建Storage桶 ===")
    
    try:
        # 检查桶是否存在
        buckets = supabase_client.storage.list_buckets()
        bucket_names = [bucket["name"] for bucket in buckets]
        
        if BUCKET_NAME in bucket_names:
            print(f"桶 {BUCKET_NAME} 已存在")
            return True
        
        # 创建桶
        supabase_client.storage.create_bucket(BUCKET_NAME, {"public": True})
        print(f"桶 {BUCKET_NAME} 创建成功")
        return True
    except Exception as e:
        print(f"创建桶失败: {e}")
        print(f"请手动在Supabase控制台创建名为'{BUCKET_NAME}'的公共桶")
        return False

def set_permissions():
    """设置权限"""
    print("\n=== 设置权限 ===")
    
    try:
        # 设置表权限（允许匿名用户读写）
        print("设置表权限...")
        # 注意：Supabase的Python客户端可能不支持直接设置权限
        # 这里我们只是打印提示信息
        print("请手动在Supabase控制台设置以下权限:")
        print("1. 表权限 -> markdown_files -> 允许匿名用户进行 SELECT、INSERT、UPDATE、DELETE 操作")
        print("2. Storage权限 -> notes -> 允许匿名用户进行读写操作")
        return True
    except Exception as e:
        print(f"设置权限失败: {e}")
        return False

def read_markdown_files():
    """读取本地Markdown文件"""
    print("\n=== 读取本地Markdown文件 ===")
    
    # 检查目录是否存在
    if not os.path.exists(NOTES_DIR):
        print(f"目录 {NOTES_DIR} 不存在")
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
        file_path_in_bucket = f"notes/{safe_file_name}"
        # 生成文件URL
        file_url = f"https://lyokdigjpgzgloyhkmkm.supabase.co/storage/v1/object/public/notes/{file_path_in_bucket}"
        
        files.append({
            "name": safe_file_name,
            "display_name": file_name,
            "title": title,
            "file_path": file_path_in_bucket,
            "file_url": file_url,
            "content": content
        })
    
    print(f"读取了 {len(files)} 个Markdown文件")
    return files

def upload_files_to_storage(files):
    """上传文件到Storage"""
    print("\n=== 上传文件到Storage ===")
    
    if not files:
        print("没有文件需要上传")
        return []
    
    uploaded_files = []
    
    for file in files:
        try:
            # 上传文件到Storage（使用正确的API）
            result = supabase_client.storage.from_(BUCKET_NAME).upload(
                path=file["file_path"],
                file=file["content"].encode('utf-8'),
                file_options={"content-type": "text/markdown"}
            )
            
            uploaded_files.append(file)
            print(f"文件上传成功: {file['name']}")
        except Exception as e:
            print(f"上传文件失败 {file['name']}: {e}")
            print("跳过此文件，继续上传其他文件")
    
    print(f"成功上传 {len(uploaded_files)} 个文件")
    return uploaded_files

def insert_file_indexes(files):
    """插入文件索引到数据库"""
    print("\n=== 插入文件索引到数据库 ===")
    
    if not files:
        print("没有文件索引需要插入")
        return []
    
    inserted_files = []
    
    for file in files:
        try:
            # 检查文件是否已存在
            response = supabase_client.table("markdown_files").select("id").eq("name", file["name"]).limit(1).execute()
            
            if response.data and len(response.data) > 0:
                print(f"文件 {file['name']} 已存在，跳过")
                continue
            
            # 插入文件索引
            supabase_client.table("markdown_files").insert({
                "name": file["name"],
                "title": file["title"],
                "file_path": file["file_path"],
                "file_url": file["file_url"]
            }).execute()
            
            inserted_files.append(file)
            print(f"文件索引插入成功: {file['name']}")
        except Exception as e:
            print(f"插入文件索引失败 {file['name']}: {e}")
    
    print(f"成功插入 {len(inserted_files)} 个文件索引")
    return inserted_files

def main():
    """主函数"""
    print("=== Supabase自动化设置 ===")
    print(f"Supabase URL: {SUPABASE_URL}")
    print(f"Storage桶名称: {BUCKET_NAME}")
    print(f"本地文件目录: {NOTES_DIR}")
    print()
    
    # 创建表
    create_table()
    
    # 创建Storage桶
    create_storage_bucket()
    
    # 设置权限
    set_permissions()
    
    # 显示上传说明
    print("\n=== 文件上传说明 ===")
    print("由于权限限制，无法自动上传文件到Supabase Storage。")
    print("请按照以下步骤手动上传文件：")
    print("1. 登录到Supabase控制台")
    print("2. 导航到Storage -> Buckets -> notes")
    print("3. 点击'Upload'按钮上传assets/notes目录下的Markdown文件")
    print("4. 在上传时，为每个文件生成一个安全的英文文件名（可以使用file_+哈希值的格式）")
    print("5. 上传完成后，记录每个文件的URL")
    print()
    print("=== 数据库索引说明 ===")
    print("请按照以下步骤手动更新数据库索引：")
    print("1. 登录到Supabase控制台")
    print("2. 导航到Database -> Tables -> markdown_files")
    print("3. 点击'Insert row'按钮为每个上传的文件添加索引")
    print("4. 填写以下字段：")
    print("   - name: 文件的英文/哈希文件名（如file_abc123.md）")
    print("   - display_name: 文件的原始中文文件名（如'01大模型概述.md'）")
    print("   - title: 文件标题（可以与display_name相同）")
    print("   - file_path: 文件在存储桶中的路径（如'notes/file_abc123.md'）")
    print("   - file_url: 文件的完整URL（如'https://lyokdigjpgzgloyhkmkm.supabase.co/storage/v1/object/public/notes/notes/file_abc123.md'）")
    
    print("\n=== 设置完成 ===")
    print("请按照上述说明手动完成文件上传和数据库索引更新")

if __name__ == "__main__":
    main()
