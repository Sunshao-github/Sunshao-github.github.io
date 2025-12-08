#!/usr/bin/env python3
"""
Markdown文件管理后端服务
使用FastAPI框架，处理与Supabase的交互
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import supabase
import os
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# 初始化FastAPI应用
app = FastAPI(
    title="Markdown File Manager API",
    description="用于管理Markdown文件的API服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境应该限制
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有请求头
)

# 初始化Supabase客户端
SUPABASE_URL = "https://lyokdigjpgzgloyhkmkm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx5b2tkaWdqcGd6Z2xveWhrbWttIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ3MDc5NzksImV4cCI6MjA4MDI4Mzk3OX0.mGBP2vN7hXnWW8aN246zzwUUSXiqXyemR8kn-LMUI88"
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

# Supabase Storage配置
BUCKET_NAME = "notes"
STORAGE_BASE_URL = f"https://lyokdigjpgzgloyhkmkm.supabase.co/storage/v1/object/public/notes"

# 数据模型
class MarkdownFile(BaseModel):
    name: Optional[str] = None  # 英文/哈希文件名
    display_name: str  # 中文显示名
    title: str
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    content: Optional[str] = None  # 用于上传文件内容
    sort_order: Optional[int] = 0  # 排序字段，默认为0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class FileListResponse(BaseModel):
    files: List[str]

class FileIndexResponse(BaseModel):
    id: Optional[str] = None
    name: str  # 英文/哈希文件名
    display_name: str  # 中文显示名
    title: str
    file_path: str
    file_url: Optional[str] = None
    sort_order: Optional[int] = 0  # 排序字段
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class FileIndexListResponse(BaseModel):
    files: List[FileIndexResponse]

# 导入哈希库
import hashlib

# 生成英文/哈希文件名
def generate_slug(file_name):
    """生成英文/哈希文件名"""
    # 确保文件名包含.md扩展名
    if not file_name.lower().endswith('.md'):
        file_name += '.md'
    
    # 移除文件扩展名
    name_without_ext = os.path.splitext(file_name)[0]
    
    # 生成哈希值
    hash_value = hashlib.md5(name_without_ext.encode('utf-8')).hexdigest()[:10]
    
    # 构建最终文件名（保留原扩展名）
    return f"file_{hash_value}.md"

# 创建表的函数
def create_table():
    """创建markdown_files表"""
    try:
        # 检查表是否存在
        result = supabase_client.table("markdown_files").select("id").limit(1).execute()
        # 表已存在，不打印消息以保持日志简洁
    except Exception as e:
        # 如果表不存在，打印详细信息
        print(f"表不存在: {e}")
        print("请在Supabase控制台手动创建markdown_files表，包含以下字段：")
        print("- id: uuid (primary key, default: gen_random_uuid())")
        print("- name: text (unique)  # 英文/哈希文件名")
        print("- display_name: text  # 中文显示名")
        print("- title: text")
        print("- file_path: text")
        print("- file_url: text")
        print("- sort_order: integer DEFAULT 0  # 排序字段")
        print("- created_at: timestamp with time zone (default: now())")
        print("- updated_at: timestamp with time zone (default: now())")
        print("\n创建表的SQL语句:")
        print("CREATE TABLE public.markdown_files (")
        print("    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),")
        print("    name text UNIQUE NOT NULL,")
        print("    display_name text,")
        print("    title text,")
        print("    file_path text,")
        print("    file_url text,")
        print("    sort_order integer DEFAULT 0,")
        print("    created_at timestamp with time zone DEFAULT now(),")
        print("    updated_at timestamp with time zone DEFAULT now()")
        print(");")
        print("\n请复制以上SQL语句到Supabase控制台执行，然后重启后端服务。")

# 初始化表
create_table()

@app.get("/api/files", response_model=FileListResponse, summary="获取文件列表")
async def get_files():
    """获取所有Markdown文件的列表"""
    try:
        # 从数据库获取所有文件名称
        try:
            db_response = supabase_client.table("markdown_files").select("name").order("sort_order", desc=False).execute()
            db_files = db_response.data if db_response.data else []
            # 提取文件名
            files = [db_file['name'] for db_file in db_files]
        except Exception as e:
            # 如果sort_order字段不存在，尝试不使用sort_order字段查询
            print(f"使用sort_order字段查询失败: {e}")
            db_response = supabase_client.table("markdown_files").select("name").execute()
            db_files = db_response.data if db_response.data else []
            # 提取文件名
            files = [db_file['name'] for db_file in db_files]
            files.sort()  # 如果没有排序字段，按字母顺序排序
        
        return FileListResponse(files=files)
    except Exception as e:
        # 如果从数据库获取失败，尝试从本地文件系统获取
        print(f"Error getting files from database: {e}")
        try:
            # 从本地文件系统获取文件列表
            files = [f for f in os.listdir(NOTES_DIR) if f.endswith(".md")]
            files.sort()
            return FileListResponse(files=files)
        except Exception as e2:
            print(f"Error getting files from local: {e2}")
            # 如果获取失败，返回空列表
            return FileListResponse(files=[])

@app.get("/api/files/index", response_model=FileIndexListResponse, summary="获取文件索引列表")
async def get_file_indexes():
    """获取所有Markdown文件的索引信息，按sort_order升序排列"""
    try:
        # 尝试从数据库获取所有文件索引信息，按sort_order升序排列
        try:
            db_response = supabase_client.table("markdown_files").select("id, name, display_name, title, file_path, file_url, sort_order, created_at, updated_at").order("sort_order", desc=False).execute()
            db_files = db_response.data if db_response.data else []
        except Exception as e:
            # 如果sort_order字段不存在，尝试不使用sort_order字段查询
            print(f"使用sort_order字段查询失败: {e}")
            db_response = supabase_client.table("markdown_files").select("id, name, display_name, title, file_path, file_url, created_at, updated_at").execute()
            db_files = db_response.data if db_response.data else []
        
        # 转换为响应模型
        files = []
        for db_file in db_files:
            file_name = db_file['name']
            # 生成文件URL
            file_url = f"{STORAGE_BASE_URL}/{file_name}"
            
            files.append(FileIndexResponse(
                id=db_file.get('id'),
                name=file_name,
                display_name=db_file.get('display_name', file_name),
                title=db_file.get('title', file_name.replace('.md', '')),
                file_path=db_file.get('file_path', file_name),
                file_url=file_url,
                sort_order=db_file.get('sort_order', 0),
                created_at=db_file.get('created_at'),
                updated_at=db_file.get('updated_at')
            ))
        
        return FileIndexListResponse(files=files)
    except Exception as e:
        print(f"Error getting file indexes: {e}")
        # 如果获取失败，返回空列表
        return FileIndexListResponse(files=[])

@app.get("/api/files/{file_name}", summary="获取文件内容")
async def get_file(file_name: str):
    """获取指定Markdown文件的内容"""
    try:
        # 直接从Supabase Storage获取文件内容
        bucket = supabase_client.storage.from_(BUCKET_NAME)
        content = bucket.download(file_name).decode('utf-8')
        
        return {"content": content}
    except Exception as e:
        print(f"Error getting file content: {e}")
        # 如果获取失败，返回404
        raise HTTPException(status_code=404, detail="文件未找到")

@app.post("/api/files", status_code=201, summary="创建或更新文件")
async def save_file(file: MarkdownFile = Body(...)):
    """创建新文件或更新现有文件"""
    try:
        print(f"接收到保存文件请求: {file}")
        
        # 生成英文/哈希文件名（如果没有提供）
        if not file.name:
            file.name = generate_slug(file.display_name)
            print(f"生成的文件名: {file.name}")
        
        # 如果提供了文件内容
        if file.content:
            # 构建文件路径
            file_path = file.name
            
            # 上传文件到Supabase Storage
            try:
                print(f"上传文件到Supabase Storage，路径: {file_path}")
                
                # 检查文件是否已存在，如果存在则先删除
                try:
                    existing_file = supabase_client.storage.from_(BUCKET_NAME).download(file_path)
                    print(f"文件已存在，先删除旧版本")
                    supabase_client.storage.from_(BUCKET_NAME).remove([file_path])
                except Exception as e:
                    print(f"文件不存在或无法下载，直接上传: {e}")
                
                # 上传文件到Supabase Storage
                supabase_client.storage.from_(BUCKET_NAME).upload(
                    path=file_path,
                    file=file.content.encode('utf-8')
                )
                
                # 构建正确的文件URL
                file_url = f"{STORAGE_BASE_URL}/{file_path}"
                print(f"文件上传成功，URL: {file_url}")
                
                # 准备要插入到数据库的文件信息
                file_info = {
                    "name": file.name,
                    "display_name": file.display_name,
                    "title": file.title,
                    "file_path": file_path,
                    "file_url": file_url,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                
                # 只有当sort_order字段存在于数据库中时才添加该字段
                try:
                    # 尝试查询sort_order字段
                    test_response = supabase_client.table("markdown_files").select("sort_order").limit(1).execute()
                    # 如果查询成功，添加sort_order字段
                    file_info["sort_order"] = file.sort_order if file.sort_order is not None else 0
                except Exception as e:
                    print(f"sort_order字段可能不存在: {e}")
                
                # 插入或更新数据库记录
                try:
                    print(f"将文件信息插入到数据库: {file_info}")
                    
                    # 检查文件是否已存在于数据库
                    existing_file = supabase_client.table("markdown_files").select("id").eq("name", file.name).limit(1).execute()
                    
                    if existing_file.data and len(existing_file.data) > 0:
                        # 如果文件已存在，更新记录
                        update_data = {
                            "display_name": file.display_name,
                            "title": file.title,
                            "file_url": file_url,
                            "updated_at": datetime.now().isoformat()
                        }
                        
                        # 只有当sort_order字段存在于数据库中时才添加该字段
                        try:
                            # 尝试查询sort_order字段
                            test_response = supabase_client.table("markdown_files").select("sort_order").limit(1).execute()
                            # 如果查询成功，添加sort_order字段
                            update_data["sort_order"] = file.sort_order if file.sort_order is not None else 0
                        except Exception as e:
                            print(f"sort_order字段可能不存在: {e}")
                        
                        update_response = supabase_client.table("markdown_files").update(update_data).eq("name", file.name).execute()
                        print(f"数据库记录已更新: {update_response}")
                    else:
                        # 如果文件不存在，插入新记录
                        insert_response = supabase_client.table("markdown_files").insert(file_info).execute()
                        print(f"数据库记录已插入: {insert_response}")
                        
                except Exception as db_error:
                    print(f"数据库操作失败，但文件已成功上传到Storage: {db_error}")
                    # 数据库操作失败不影响文件上传，只是记录日志
                
                return {
                    "message": "文件已成功保存",
                    "name": file.name,
                    "file_url": file_url
                }
            except Exception as storage_error:
                print(f"Supabase Storage上传失败: {storage_error}")
                # 如果Storage上传失败，返回错误
                raise HTTPException(status_code=500, detail=f"Supabase Storage上传失败: {str(storage_error)}")
        else:
            # 如果没有提供文件内容，返回错误
            raise HTTPException(status_code=400, detail="文件内容不能为空")
    except Exception as e:
        print(f"保存文件失败: {e}")
        # 返回通用错误信息
        raise HTTPException(status_code=500, detail=f"保存文件失败: {str(e)}")

@app.delete("/api/files/{file_name}", summary="删除文件")
async def delete_file(file_name: str):
    """删除指定的Markdown文件"""
    try:
        print(f"开始删除文件: {file_name}")
        
        # 先获取文件索引信息，以便知道file_path
        index_response = supabase_client.table("markdown_files").select("file_path").eq("name", file_name).limit(1).execute()
        print(f"数据库查询结果: {index_response.data}")
        
        file_path = None
        if index_response.data and len(index_response.data) > 0:
            file_path = index_response.data[0].get("file_path")
        print(f"获取的file_path: {file_path}")
        
        # 如果file_path为None，直接使用fileName作为file_path
        if not file_path:
            file_path = file_name
            print(f"file_path为None，使用fileName作为file_path: {file_path}")
        
        # 从数据库删除文件索引信息
        response = supabase_client.table("markdown_files").delete().eq("name", file_name).execute()
        print(f"数据库删除结果: {response.data}")
        
        # 从Supabase Storage删除文件
        try:
            # 先尝试使用获取到的file_path删除
            supabase_client.storage.from_(BUCKET_NAME).remove([file_path])
            print(f"文件已从Supabase Storage删除: {file_path}")
        except Exception as storage_error:
            print(f"使用file_path从Supabase Storage删除文件失败: {storage_error}")
            # 如果失败，尝试使用fileName删除
            try:
                supabase_client.storage.from_(BUCKET_NAME).remove([file_name])
                print(f"使用fileName从Supabase Storage删除文件成功: {file_name}")
            except Exception as e:
                print(f"使用fileName从Supabase Storage删除文件也失败: {e}")
        
        if response.data or file_path:
            return {"message": "文件及索引已删除"}
        else:
            raise HTTPException(status_code=404, detail="文件未找到")
    except Exception as e:
        print(f"删除文件时发生错误: {str(e)}")
        # 检查是否是表不存在的错误
        if "Could not find the table" in str(e) or "PGRST205" in str(e):
            # 如果是表不存在的错误，只删除Storage文件
            try:
                supabase_client.storage.from_(BUCKET_NAME).remove([file_name])
                print(f"表不存在，但文件已从Supabase Storage删除: {file_name}")
                return {"message": "文件已删除（表不存在）"}
            except Exception as storage_error:
                print(f"表不存在且从Storage删除文件失败: {storage_error}")
                raise HTTPException(status_code=500, detail="表不存在且无法删除文件")
        # 如果是其他错误，返回500错误
        raise HTTPException(status_code=500, detail=f"删除文件失败: {str(e)}")

@app.get("/api/health", summary="健康检查")
async def health_check():
    """检查API服务是否正常运行"""
    return {"status": "ok", "message": "Markdown File Manager API is running"}



@app.post("/api/admin/auth", summary="管理员登录验证")
async def admin_auth(password: str = Body(..., embed=True)):
    """验证管理员密码"""
    try:
        # 这里可以从环境变量或配置文件中读取密码
        # 为了演示，暂时硬编码，但实际应用中应该使用更安全的方式
        ADMIN_PASSWORD = "090999"
        
        if password == ADMIN_PASSWORD:
            return {"success": True, "message": "登录成功"}
        else:
            return {"success": False, "message": "密码错误"}
    except Exception as e:
        print(f"管理员登录验证失败: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)