# 文档知识图谱构建器

这是一个基于Python的文档知识图谱构建工具，可以从文本中提取实体和关系，并生成可视化的知识图谱。

## 功能特点

- 使用spaCy进行自然语言处理
- 支持多种实体类型识别（人物、组织、地点、日期等）
- 使用多种方法提取实体间关系：
  - 基于动词的关系提取
  - 基于介词的关系提取
  - 基于所有格的关系提取
- 生成高质量的可视化知识图谱
- 支持导出为CSV格式（节点和边分别导出）
- 提供知识图谱统计信息

## 安装要求

- Python 3.7+
- 依赖包（见requirements.txt）

## 安装步骤

1. 克隆此仓库
2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行主程序：
```bash
python knowledge_graph.py
```

2. 程序将自动处理示例文本，并生成：
   - knowledge_graph.png（可视化图谱）
   - nodes_knowledge_graph.csv（节点数据）
   - edges_knowledge_graph.csv（关系数据）
   - 控制台输出统计信息

## 自定义使用

要处理自己的文本，可以修改 `knowledge_graph.py` 中的 `sample_text` 变量，或者创建新的Python脚本：

```python
from knowledge_graph import KnowledgeGraphBuilder

# 创建构建器实例
kg_builder = KnowledgeGraphBuilder()

# 处理文本
your_text = "你的文本内容"
kg_builder.build_graph(your_text)

# 获取统计信息
stats = kg_builder.get_statistics()
print(stats)

# 生成可视化
kg_builder.visualize("your_output.png")

# 导出数据
kg_builder.export_to_csv("your_output.csv")
```

## 输出说明

- PNG文件：包含可视化的知识图谱，使用不同颜色表示不同类型的实体
- nodes_*.csv文件：包含实体信息（实体名称和类型）
- edges_*.csv文件：包含关系信息（源实体、目标实体和关系类型）

## 实体类型

支持的主要实体类型包括：
- PERSON（人物）
- ORG（组织）
- GPE（地理政治实体）
- DATE（日期）
- PRODUCT（产品）
- EVENT（事件）
- WORK_OF_ART（艺术作品）
- LAW（法律）
- LANGUAGE（语言）
- NOUN_PHRASE（名词短语）

## 注意事项

- 确保安装了所有依赖包
- 文本最好是英文，因为当前使用的是英文语言模型
- 图谱的布局是自动生成的，每次运行可能略有不同
- 可视化效果可以通过调整 `visualize` 方法中的参数来优化 