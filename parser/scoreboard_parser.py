import nbtlib
import json
import re
import traceback
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod


class ScoreboardParser:
    """记分板解析器主类"""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.parsers = {
            # 这里可以注册不同DataVersion的解析器
            # 例如: 3120: DataVersion3120Parser(),
            # 默认解析器
            'default': DefaultScoreboardParser(debug)
        }
    
    def parse_nbt_file(self, nbt_file_path: str) -> str:
        """
        解析NBT文件并返回JSON字符串
        
        Args:
            nbt_file_path: NBT文件路径
            
        Returns:
            JSON字符串格式的解析结果
        """
        try:
            # 加载NBT文件
            nbt_file = nbtlib.load(nbt_file_path)
            
            # 获取DataVersion
            data_version = self._get_data_version(nbt_file)
            
            # 选择对应的解析器
            parser = self._get_parser(data_version)
            
            # 解析记分板数据
            result = parser.parse(nbt_file)
            
            return json.dumps(result, ensure_ascii=False)
            
        except Exception as e:
            error_msg = f"解析文件失败: {str(e)}"
            print(error_msg)
            if self.debug:
                print("详细错误信息:")
                traceback.print_exc()
            return json.dumps({'error': error_msg}, ensure_ascii=False)
    
    def _get_data_version(self, nbt_file) -> int:
        """获取NBT文件的DataVersion"""
        # 尝试从不同位置获取DataVersion
        if 'DataVersion' in nbt_file:
            return nbt_file['DataVersion']
        elif 'data' in nbt_file and 'DataVersion' in nbt_file['data']:
            return nbt_file['data']['DataVersion']
        else:
            # 如果没有找到DataVersion，返回默认值
            return 3120  # 默认DataVersion
    
    def _get_parser(self, data_version: int):
        """根据DataVersion获取对应的解析器，支持智能版本匹配"""
        # 首先尝试精确匹配
        if data_version in self.parsers:
            print(f"使用精确匹配的解析器: DataVersion {data_version}")
            return self.parsers[data_version]
        
        # 如果没有精确匹配，尝试找到最接近的版本
        available_versions = [v for v in self.parsers.keys() if isinstance(v, int)]
        if available_versions:
            # 计算每个版本与目标版本的差值并排序
            version_diffs = [(abs(v - data_version), v) for v in available_versions]
            version_diffs.sort()  # 按差值排序
            
            # 尝试使用最接近的解析器，最多尝试2次
            error_count = 0
            for _, version in version_diffs:
                try:
                    print(f"尝试使用解析器: DataVersion {version} (目标版本: {data_version})")
                    return self.parsers[version]
                except Exception as e:
                    error_count += 1
                    print(f"解析器 {version} 出错: {e}")
                    if self.debug:
                        print("详细错误信息:")
                        traceback.print_exc()
                    if error_count >= 2:
                        print("尝试使用默认解析器")
                        return self.parsers['default']
        
        # 如果找不到合适的版本，使用默认解析器
        print(f"使用默认解析器 (目标版本: {data_version})")
        return self.parsers['default']
    
    def register_parser(self, data_version: int, parser):
        """注册新的DataVersion解析器"""
        self.parsers[data_version] = parser


class BaseScoreboardParser(ABC):
    """记分板解析器基类"""
    
    def __init__(self, debug=False):
        self.debug = debug
    
    @abstractmethod
    def parse(self, nbt_file) -> List[Dict[str, Any]]:
        """解析NBT文件并返回记分板数据"""
        pass
    
    def _extract_objectives(self, nbt_file) -> Dict[str, Dict[str, Any]]:
        """提取记分板目标信息"""
        scoreboards = {}
        objectives = nbt_file['data']['Objectives']
        
        for objective in objectives:
            internal_name = objective['Name']
            display_name_json = json.loads(objective['DisplayName'])
            display_name = display_name_json.get('text', internal_name)
            criteria_name = objective.get('CriteriaName', 'unknown')
            
            scoreboards[internal_name] = {
                'internal_name': internal_name,
                'display_name': display_name,
                'criteria_name': criteria_name,
                'data': []
            }
            
        return scoreboards
    
    def _extract_player_scores(self, nbt_file) -> List[Dict[str, Any]]:
        """提取玩家分数信息"""
        return nbt_file['data']['PlayerScores']
    
    def _populate_scoreboards(self, scoreboards: Dict[str, Dict[str, Any]], 
                            player_scores: List[Dict[str, Any]]) -> None:
        """将玩家分数填充到对应的记分板中"""
        for score_entry in player_scores:
            player_name = score_entry['Name']
            objective_name = score_entry['Objective']
            score_value = score_entry['Score']
            
            if objective_name in scoreboards:
                scoreboards[objective_name]['data'].append({
                    'Name': player_name,
                    'Score': score_value
                })
    
    def _sort_scoreboard_data(self, scoreboard_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """对记分板数据进行排序"""
        def sort_key(item):
            name = item['Name']
            # 非数字/字母开头的项目排到最前面
            if not re.match(r'^[a-zA-Z0-9]', name):
                return (0, name.lower())
            # 其他按分数倒序，然后按名称排序
            return (1, -item['Score'], name.lower())
        
        return sorted(scoreboard_data, key=sort_key)
    
    def _sort_scoreboards(self, scoreboards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """对记分板列表进行排序"""
        return sorted(scoreboards, key=lambda x: x['display_name'])


class DefaultScoreboardParser(BaseScoreboardParser):
    """默认记分板解析器（当前版本）"""
    
    def parse(self, nbt_file) -> List[Dict[str, Any]]:
        """解析NBT文件并返回记分板数据"""
        # 提取记分板信息
        scoreboards = self._extract_objectives(nbt_file)
        
        # 提取玩家分数
        player_scores = self._extract_player_scores(nbt_file)
        
        # 填充记分板数据
        self._populate_scoreboards(scoreboards, player_scores)
        
        # 对每个记分板的数据进行排序
        for scoreboard in scoreboards.values():
            scoreboard['data'] = self._sort_scoreboard_data(scoreboard['data'])
        
        # 转换为列表并排序
        result = list(scoreboards.values())
        result = self._sort_scoreboards(result)
        
        return result 