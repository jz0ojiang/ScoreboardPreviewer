import os
import json
import webview
import sys
import base64
import tempfile
from parser import ScoreboardParser
from parser.version_parsers import DataVersion3120Parser, DataVersion4325Parser

DEBUG = '--debug' in sys.argv


class Api:
    def __init__(self):
        self.parser = ScoreboardParser(debug=DEBUG)
        # 注册不同版本的解析器
        self.parser.register_parser(3120, DataVersion3120Parser(debug=DEBUG))
        self.parser.register_parser(4325, DataVersion4325Parser(debug=DEBUG))
    
    def parse_scoreboard(self, file_content: str) -> str:
        try:
            # 假设 file_content 是 NBT 文件的二进制内容的 base64 字符串
            # 写入临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.dat') as tmp:
                tmp.write(base64.b64decode(file_content))
                tmp_path = tmp.name
            
            # 使用解析器解析文件
            result = self.parser.parse_nbt_file(tmp_path)
            
            # 清理临时文件
            os.remove(tmp_path)
            
            return result
            
        except Exception as e:
            error_msg = f"解析文件失败: {str(e)}"
            print(error_msg)
            if DEBUG:
                import traceback
                print("详细错误信息:")
                traceback.print_exc()
            return json.dumps({'error': error_msg}, ensure_ascii=False)

if __name__ == '__main__':
    api = Api()
    
    # 创建窗口
    window = webview.create_window(
        'Scoreboard Previewer' + (' (Debug)' if DEBUG else ''), 
        os.path.join('src', 'index.html'), 
        js_api=api,
        width=1200,
        height=800,
        resizable=True
    )
    if DEBUG:
        # 启动应用（启用调试模式）
        print("🎮 启动 Minecraft 记分板预览器...")
        print("💡 提示: 按 F12 打开开发者工具进行调试")
    webview.start(debug=DEBUG)
