"""
不同DataVersion的记分板解析器
"""

import json
import traceback
from .scoreboard_parser import BaseScoreboardParser


class DataVersion3120Parser(BaseScoreboardParser):
    """DataVersion 3120 的解析器"""
    
    def parse(self, nbt_file) -> list:
        """解析DataVersion 3120的NBT文件"""
        scoreboards = {}
        objectives = nbt_file['data']['Objectives']
        
        for objective in objectives:
            internal_name = objective['Name']
            display_name = self._extract_display_name(objective['DisplayName'], internal_name)
            criteria_name = objective.get('CriteriaName', 'unknown')
            
            scoreboards[internal_name] = {
                'internal_name': internal_name,
                'display_name': display_name,
                'criteria_name': criteria_name,
                'data': []
            }
        
        player_scores = self._extract_player_scores(nbt_file)
        self._populate_scoreboards(scoreboards, player_scores)
        
        for scoreboard in scoreboards.values():
            scoreboard['data'] = self._sort_scoreboard_data(scoreboard['data'])
        
        result = list(scoreboards.values())
        result = self._sort_scoreboards(result)
        
        return result
    
    def _extract_display_name(self, display_name_obj, fallback: str) -> str:
        """提取显示名称"""
        if isinstance(display_name_obj, str):
            try:
                return json.loads(display_name_obj)['text']
            except Exception as e:
                if self.debug:
                    print("详细错误信息:")
                    traceback.print_exc()
                return fallback
        return display_name_obj.get('text', fallback)


class DataVersion4325Parser(BaseScoreboardParser):
    """DataVersion 4325 的解析器"""
    
    def parse(self, nbt_file) -> list:
        """解析DataVersion 4325的NBT文件"""
        scoreboards = {}
        objectives = nbt_file['data']['Objectives']
        
        for objective in objectives:
            internal_name = objective['Name']
            display_name = self._extract_display_name(objective['DisplayName'], internal_name)
            criteria_name = objective.get('CriteriaName', 'dummy')
            
            scoreboards[internal_name] = {
                'internal_name': internal_name,
                'display_name': display_name,
                'criteria_name': criteria_name,
                'data': []
            }
        
        player_scores = self._extract_player_scores(nbt_file)
        self._populate_scoreboards(scoreboards, player_scores)
        
        for scoreboard in scoreboards.values():
            scoreboard['data'] = self._sort_scoreboard_data(scoreboard['data'])
        
        result = list(scoreboards.values())
        result = self._sort_scoreboards(result)
        
        return result
    
    def _extract_display_name(self, display_name_obj, fallback: str) -> str:
        """提取显示名称"""
        if isinstance(display_name_obj, str):
            return display_name_obj
        return display_name_obj.get('text', fallback)
    
    def _populate_scoreboards(self, scoreboards: dict, player_scores: list) -> None:
        """将玩家分数填充到对应的记分板中（4325版本特殊处理）"""
        for score_entry in player_scores:
            player_name = score_entry['Name']
            objective_name = score_entry['Objective']
            score_value = score_entry.get('Score', 0)
            
            if objective_name in scoreboards:
                scoreboards[objective_name]['data'].append({
                    'Name': player_name,
                    'Score': score_value
                })


# 使用示例：
# 在app.py中注册不同版本的解析器：
# 
# from parser.version_parsers import DataVersion3120Parser, DataVersion4325Parser
# 
# api = Api()
# api.parser.register_parser(3120, DataVersion3120Parser())
# api.parser.register_parser(4325, DataVersion4325Parser()) 