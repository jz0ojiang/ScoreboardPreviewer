# 记分板解析器模块

这个模块提供了灵活的记分板解析功能，支持不同DataVersion的NBT文件解析。

## 架构说明

### 主要组件

1. **ScoreboardParser** - 主解析器类
   - 负责根据DataVersion选择合适的解析器
   - 管理不同版本的解析器注册
   - 提供统一的解析接口
   - **支持智能版本匹配**：自动找到最接近的DataVersion解析器

2. **BaseScoreboardParser** - 解析器基类
   - 提供通用的解析方法
   - 包含排序、数据提取等通用功能
   - 可以被特定版本的解析器继承和重写

3. **DefaultScoreboardParser** - 默认解析器
   - 继承自BaseScoreboardParser
   - 处理当前版本的记分板数据

## 已支持的DataVersion

### DataVersion 3120
- **字段结构**：`Objectives[].DisplayName`, `CriteriaName`, `Name`
- **特点**：所有字段都存在，`CriteriaName`默认为`'unknown'`

### DataVersion 4325
- **字段结构**：`Objectives[].DisplayName`, `Name`
- **特点**：
  - `CriteriaName`字段可能不存在，如果不存在默认为`'dummy'`
  - `PlayerScores[].Score`字段可能不存在，如果不存在默认为`0`
  - `DisplayName`支持字符串和对象两种格式

## 智能版本匹配

解析器支持智能版本匹配机制：

1. **精确匹配**：首先尝试找到完全匹配的DataVersion解析器
2. **最接近匹配**：如果没有精确匹配，找到差距最小的版本（差距≤100）
3. **默认回退**：如果都找不到合适的，使用默认解析器

### 匹配示例

```python
# 假设注册了以下解析器：
parser.register_parser(3120, DataVersion3120Parser())
parser.register_parser(4325, DataVersion4325Parser())

# 当遇到DataVersion 3120时：
# 1. 精确匹配，使用DataVersion3120Parser()

# 当遇到DataVersion 4325时：
# 1. 精确匹配，使用DataVersion4325Parser()

# 当遇到DataVersion 3110时：
# 1. 没有精确匹配的3110
# 2. 最接近的是3120（差距10），在可接受范围内
# 3. 使用DataVersion3120Parser()

# 当遇到DataVersion 3500时：
# 1. 没有精确匹配的3500
# 2. 最接近的是3120（差距380），超出可接受范围
# 3. 使用默认解析器
```

## 使用方法

### 基本使用

```python
from parser import ScoreboardParser

# 创建解析器实例
parser = ScoreboardParser()

# 解析NBT文件
result = parser.parse_nbt_file("path/to/scoreboard.dat")
```

### 添加新的DataVersion解析器

1. 创建新的解析器类：

```python
from parser.scoreboard_parser import BaseScoreboardParser

class DataVersion5000Parser(BaseScoreboardParser):
    def parse(self, nbt_file) -> list:
        # 实现特定版本的解析逻辑
        # 可以重写基类的方法来处理不同的数据结构
        pass
```

2. 注册解析器：

```python
from parser import ScoreboardParser
from parser.version_parsers import DataVersion5000Parser

parser = ScoreboardParser()
parser.register_parser(5000, DataVersion5000Parser())
```

### 在API中使用

```python
class Api:
    def __init__(self):
        self.parser = ScoreboardParser()
        # 注册不同版本的解析器
        self.parser.register_parser(3120, DataVersion3120Parser())
        self.parser.register_parser(4325, DataVersion4325Parser())
    
    def parse_scoreboard(self, file_content: str) -> str:
        # 处理base64到临时文件的逻辑
        # 然后使用解析器
        result = self.parser.parse_nbt_file(tmp_path)
        return result
```

## 通用方法

BaseScoreboardParser提供了以下通用方法，可以被子类覆盖：

- `_extract_objectives()` - 提取记分板目标信息
- `_extract_player_scores()` - 提取玩家分数信息
- `_populate_scoreboards()` - 将玩家分数填充到记分板
- `_sort_scoreboard_data()` - 对记分板数据进行排序
- `_sort_scoreboards()` - 对记分板列表进行排序

### 覆盖基类方法示例

```python
class DataVersion4325Parser(BaseScoreboardParser):
    def _populate_scoreboards(self, scoreboards: dict, player_scores: list) -> None:
        """覆盖基类方法，处理4325版本的特殊情况"""
        for score_entry in player_scores:
            player_name = score_entry['Name']
            objective_name = score_entry['Objective']
            score_value = score_entry.get('Score', 0)
            
            if objective_name in scoreboards:
                scoreboards[objective_name]['data'].append({
                    'Name': player_name,
                    'Score': score_value
                })
```

这样可以根据不同版本的数据结构特点，灵活地覆盖需要特殊处理的方法。

## DataVersion检测

解析器会自动检测NBT文件中的DataVersion字段，并选择合适的解析器。

支持的DataVersion检测位置：
- 根级别的`DataVersion`字段
- `data.DataVersion`字段
- 如果都找不到，使用默认值3120

## 调试信息

解析器会在控制台输出版本匹配信息，帮助你了解使用了哪个解析器：

```
使用精确匹配的解析器: DataVersion 3120
使用最接近的解析器: DataVersion 3120 (目标版本: 3110)
使用默认解析器 (目标版本: 3500)
```

### DEBUG模式

解析器支持DEBUG模式，提供不同级别的错误信息：

```python
# 启用DEBUG模式
parser = ScoreboardParser(debug=True)

# 普通模式
parser = ScoreboardParser(debug=False)  # 默认
```

#### DEBUG模式特性

- **详细错误追踪**：使用`traceback.print_exc()`提供完整的错误堆栈
- **版本匹配信息**：显示详细的解析器选择过程
- **错误定位**：精确显示错误发生的文件和行号

#### 普通模式特性

- **简洁错误信息**：只显示基本的错误消息
- **性能优化**：减少不必要的调试输出
- **生产环境友好**：适合最终用户使用

### 错误追踪

解析器使用Python的`traceback`模块提供详细的错误信息，包括：

- 错误发生的具体位置（文件名、行号）
- 完整的调用栈信息
- 详细的错误描述

当解析过程中出现错误时，会输出类似以下信息：

```
解析记分板 Objectives 时出错: 'DisplayName'
详细错误信息:
Traceback (most recent call last):
  File "parser/scoreboard_parser.py", line 45, in _extract_objectives
    display_name_json = json.loads(objective['DisplayName'])
KeyError: 'DisplayName'
```

这有助于快速定位和解决问题。

## 代码优化

### 最新改进

1. **统一DisplayName处理**：创建了`_extract_display_name`方法，支持字符串和对象两种格式
2. **简化错误处理**：移除了冗余的try-except块，让错误向上传播
3. **代码清理**：移除了不必要的注释和重复代码
4. **更好的可维护性**：提高了代码的可读性和维护性 