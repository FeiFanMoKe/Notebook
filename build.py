import os
import json
from pathlib import Path


class HTMLTreeGenerator:
    def __init__(self, root_dir="."):
        self.root_dir = Path(root_dir)
        self.tree_structure = {}

    def scan_html_files(self):
        """扫描文件夹中的所有HTML文件"""
        html_files = []
        for file_path in self.root_dir.rglob("*.html"):
            if file_path.name != "index.html":  # 排除index.html本身
                relative_path = file_path.relative_to(self.root_dir)
                html_files.append(relative_path)
        return html_files

    def build_tree_structure(self, html_files):
        """构建树状结构"""
        tree = {}

        for file_path in html_files:
            parts = file_path.parts
            current_dict = tree

            # 构建文件夹结构
            for part in parts[:-1]:  # 排除文件名
                if part not in current_dict:
                    current_dict[part] = {"folders": {}, "files": []}
                current_dict = current_dict[part]["folders"]

            # 添加文件
            folder_name = parts[-2] if len(parts) > 1 else ""
            if folder_name:
                if folder_name not in tree:
                    tree[folder_name] = {"folders": {}, "files": []}
                tree[folder_name]["files"].append({
                    "name": parts[-1],
                    "path": str(file_path).replace("\\", "/")
                })
            else:
                # 根目录文件
                if "root_files" not in tree:
                    tree["root_files"] = {"folders": {}, "files": []}
                tree["root_files"]["files"].append({
                    "name": parts[-1],
                    "path": str(file_path).replace("\\", "/")
                })

        return tree

    def build_tree_structure_v2(self, html_files):
        """改进的树状结构构建"""
        tree = {"folders": {}, "files": []}

        for file_path in html_files:
            parts = file_path.parts
            current_node = tree

            # 遍历文件夹层级
            for i, part in enumerate(parts[:-1]):
                if part not in current_node["folders"]:
                    current_node["folders"][part] = {"folders": {}, "files": []}
                current_node = current_node["folders"][part]

            # 添加文件到当前节点
            current_node["files"].append({
                "name": parts[-1],
                "path": str(file_path).replace("\\", "/")
            })

        return tree

    def generate_tree_html(self, node, level=0):
        """递归生成树状HTML"""
        html = ""

        # 生成文件夹
        for folder_name, folder_node in node["folders"].items():
            folder_id = f"folder_{abs(hash(folder_name))}_{level}"
            html += f"""
            <li class="folder-item">
                <div class="folder-header" onclick="toggleFolder('{folder_id}')">
                    <span class="folder-icon">📁</span>
                    <span class="folder-name">{folder_name}</span>
                    <span class="toggle-icon">▶</span>
                </div>
                <ul class="folder-content" id="{folder_id}">
                    {self.generate_tree_html(folder_node, level + 1)}
                </ul>
            </li>
            """

        # 生成文件
        for file_info in node["files"]:
            html += f"""
            <li class="file-item">
                <span class="file-icon">📄</span>
                <a href="{file_info['path']}" class="file-link">{file_info['name']}</a>
            </li>
            """

        return html

    def generate_index_html(self):
        """生成完整的index.html文件"""
        html_files = self.scan_html_files()
        tree = self.build_tree_structure_v2(html_files)
        tree_html = self.generate_tree_html(tree)

        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文档目录</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
        }}

        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 24px;
            margin-bottom: 8px;
        }}

        .header p {{
            opacity: 0.9;
            font-size: 14px;
        }}

        .tree-container {{
            padding: 20px;
        }}

        .tree {{
            list-style: none;
        }}

        .folder-item, .file-item {{
            margin: 4px 0;
        }}

        .folder-header {{
            display: flex;
            align-items: center;
            padding: 8px 12px;
            cursor: pointer;
            border-radius: 6px;
            transition: background-color 0.2s;
            user-select: none;
        }}

        .folder-header:hover {{
            background-color: #f0f0f0;
        }}

        .folder-icon, .file-icon {{
            margin-right: 8px;
            font-size: 16px;
        }}

        .folder-name {{
            flex: 1;
            font-weight: 500;
            color: #333;
        }}

        .toggle-icon {{
            font-size: 12px;
            transition: transform 0.2s;
            color: #666;
        }}

        .folder-content {{
            list-style: none;
            margin-left: 20px;
            border-left: 2px solid #e0e0e0;
            padding-left: 16px;
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease-out;
        }}

        .folder-content.expanded {{
            max-height: 2000px;
        }}

        .folder-header.expanded .toggle-icon {{
            transform: rotate(90deg);
        }}

        .file-item {{
            display: flex;
            align-items: center;
            padding: 6px 12px;
        }}

        .file-link {{
            color: #0066cc;
            text-decoration: none;
            flex: 1;
            padding: 4px 0;
            border-radius: 4px;
            transition: color 0.2s;
        }}

        .file-link:hover {{
            color: #0052a3;
            text-decoration: underline;
        }}

        .stats {{
            padding: 16px 20px;
            border-top: 1px solid #e0e0e0;
            background-color: #f9f9f9;
            color: #666;
            font-size: 14px;
            text-align: center;
        }}

        .empty-state {{
            text-align: center;
            padding: 40px 20px;
            color: #666;
        }}

        .empty-state .icon {{
            font-size: 48px;
            margin-bottom: 16px;
            opacity: 0.5;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 文档目录</h1>
            <p>点击文件夹展开/收起，点击文件名访问文档</p>
        </div>

        <div class="tree-container">
            {f'<ul class="tree">{tree_html}</ul>' if tree_html.strip() else '''
            <div class="empty-state">
                <div class="icon">📭</div>
                <h3>暂无HTML文件</h3>
                <p>在当前目录中没有找到HTML文件</p>
            </div>
            '''}
        </div>

        <div class="stats">
            共找到 {len(html_files)} 个HTML文件
        </div>
    </div>

    <script>
        function toggleFolder(folderId) {{
            const folder = document.getElementById(folderId);
            const header = folder.previousElementSibling;

            if (folder.classList.contains('expanded')) {{
                folder.classList.remove('expanded');
                header.classList.remove('expanded');
            }} else {{
                folder.classList.add('expanded');
                header.classList.add('expanded');
            }}
        }}

        // 页面加载完成后的初始化
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('文档目录已加载');
        }});
    </script>
</body>
</html>"""

        return html_content

    def create_index_file(self, output_path="index.html"):
        """创建index.html文件"""
        html_content = self.generate_index_html()

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ 已生成 {output_path}")
        print(f"🔍 扫描目录: {self.root_dir.absolute()}")

        html_files = self.scan_html_files()
        print(f"📄 找到 {len(html_files)} 个HTML文件:")
        for file_path in html_files:
            print(f"   - {file_path}")


def main():
    """主函数"""
    print("🚀 开始生成HTML文档目录...")

    # 可以指定要扫描的目录，默认为当前目录
    scan_directory = input("请输入要扫描的目录路径（直接回车使用当前目录）: ").strip()
    if not scan_directory:
        scan_directory = "."

    # 检查目录是否存在
    if not os.path.exists(scan_directory):
        print(f"❌ 目录不存在: {scan_directory}")
        return

    generator = HTMLTreeGenerator(scan_directory)
    generator.create_index_file()

    print("\n✨ 完成！你可以:")
    print("1. 在浏览器中打开 index.html 查看效果")
    print("2. 将整个文件夹上传到 GitHub，在仓库设置中启用 GitHub Pages")
    print("3. 访问 https://yourusername.github.io/yourrepository 查看在线版本")


if __name__ == "__main__":
    main()