import spacy
import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict, Set
import pandas as pd
from collections import defaultdict
import PyPDF2
from docx import Document
from pathlib import Path
from tqdm import tqdm
import argparse
import re

class DocumentProcessor:
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        """
        从PDF文件中提取文本
        """
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                # 创建PDF阅读器对象
                pdf_reader = PyPDF2.PdfReader(file)
                
                # 获取页数
                num_pages = len(pdf_reader.pages)
                
                # 遍历每一页
                for page_num in tqdm(range(num_pages), desc="处理PDF页面"):
                    # 获取页面对象
                    page = pdf_reader.pages[page_num]
                    # 提取文本
                    text += page.extract_text() + "\n"
                
                return text
        except Exception as e:
            print(f"处理PDF文件时出错: {str(e)}")
            return ""

    @staticmethod
    def extract_text_from_docx(docx_path: str) -> str:
        """
        从Word文档中提取文本
        """
        try:
            doc = Document(docx_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            print(f"处理Word文档时出错: {str(e)}")
            return ""

    @staticmethod
    def split_text(text: str, max_length: int = 1000000) -> List[str]:
        """
        将长文本分割成较小的块
        """
        # 如果文本长度在限制范围内，直接返回
        if len(text) <= max_length:
            return [text]
        
        # 按句子分割文本
        sentences = re.split(r'[.!?。！？]+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # 如果单个句子超过最大长度，需要进一步分割
            if len(sentence) > max_length:
                # 按段落分割
                paragraphs = sentence.split('\n')
                for paragraph in paragraphs:
                    if len(paragraph) > max_length:
                        # 按逗号分割
                        parts = paragraph.split('，')
                        for part in parts:
                            if len(current_chunk) + len(part) <= max_length:
                                current_chunk += part + "，"
                            else:
                                if current_chunk:
                                    chunks.append(current_chunk.strip())
                                current_chunk = part + "，"
                    else:
                        if len(current_chunk) + len(paragraph) <= max_length:
                            current_chunk += paragraph + "\n"
                        else:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = paragraph + "\n"
            else:
                if len(current_chunk) + len(sentence) <= max_length:
                    current_chunk += sentence + "。"
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + "。"
        
        # 添加最后一个块
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

class KnowledgeGraphBuilder:
    def __init__(self):
        # 加载spaCy模型
        self.nlp = spacy.load("en_core_web_sm")
        # 设置最大文本长度
        self.nlp.max_length = 1000000
        # 创建有向图对象
        self.graph = nx.DiGraph()
        # 实体类型颜色映射
        self.entity_colors = {
            'PERSON': 'lightblue',
            'ORG': 'lightgreen',
            'GPE': 'lightyellow',
            'DATE': 'lightpink',
            'PRODUCT': 'lightgray',
            'EVENT': 'lightcoral',
            'WORK_OF_ART': 'lightsalmon',
            'LAW': 'lightseagreen',
            'LANGUAGE': 'lightsteelblue'
        }
        # Neo4j标签映射
        self.neo4j_labels = {
            'PERSON': 'Person',
            'ORG': 'Organization',
            'GPE': 'Location',
            'DATE': 'Date',
            'PRODUCT': 'Product',
            'EVENT': 'Event',
            'WORK_OF_ART': 'WorkOfArt',
            'LAW': 'Law',
            'LANGUAGE': 'Language',
            'NOUN_PHRASE': 'Entity'
        }
        
    def extract_entities(self, text: str) -> List[Tuple[str, str]]:
        """
        从文本中提取实体和关系，使用更复杂的规则
        """
        doc = self.nlp(text)
        entities = []
        
        # 提取命名实体
        for ent in doc.ents:
            if ent.label_ in self.entity_colors:
                entities.append((ent.text, ent.label_))
        
        # 提取复合名词短语
        for chunk in doc.noun_chunks:
            if chunk.root.pos_ == "NOUN" and not any(token.ent_type_ for token in chunk):
                entities.append((chunk.text, "NOUN_PHRASE"))
        
        return entities
    
    def extract_relations(self, text: str) -> List[Tuple[str, str, str]]:
        """
        使用更复杂的方法提取实体间的关系
        """
        doc = self.nlp(text)
        relations = []
        
        # 1. 基于动词的关系提取
        for token in doc:
            if token.pos_ == "VERB":
                subject = None
                object_ = None
                
                # 寻找主语和宾语
                for child in token.children:
                    if child.dep_ in ["nsubj", "nsubjpass"]:
                        # 获取完整的主语短语
                        subject = " ".join([t.text for t in child.subtree])
                    elif child.dep_ in ["dobj", "pobj"]:
                        # 获取完整的宾语短语
                        object_ = " ".join([t.text for t in child.subtree])
                
                if subject and object_:
                    relations.append((subject, token.text, object_))
        
        # 2. 基于介词的关系提取
        for token in doc:
            if token.pos_ == "ADP":
                # 获取介词短语的完整内容
                prep_phrase = " ".join([t.text for t in token.subtree])
                if token.head.pos_ == "NOUN":
                    head_phrase = " ".join([t.text for t in token.head.subtree])
                    relations.append((head_phrase, token.text, prep_phrase))
        
        # 3. 基于所有格的关系提取
        for token in doc:
            if token.dep_ == "poss":
                possessor = " ".join([t.text for t in token.subtree])
                possessed = " ".join([t.text for t in token.head.subtree])
                relations.append((possessor, "has", possessed))
        
        # 4. 基于并列关系的提取
        for token in doc:
            if token.dep_ == "conj":
                head = token.head
                if head.pos_ == "NOUN":
                    head_phrase = " ".join([t.text for t in head.subtree])
                    conj_phrase = " ".join([t.text for t in token.subtree])
                    relations.append((head_phrase, "related_to", conj_phrase))
        
        return relations
    
    def build_graph(self, text: str):
        """
        构建知识图谱，包含更多实体和关系类型
        """
        # 分割长文本
        text_chunks = DocumentProcessor.split_text(text)
        print(f"文本已分割为 {len(text_chunks)} 个块进行处理")
        
        # 处理每个文本块
        for i, chunk in enumerate(text_chunks, 1):
            print(f"正在处理第 {i}/{len(text_chunks)} 个文本块...")
            # 提取实体和关系
            entities = self.extract_entities(chunk)
            relations = self.extract_relations(chunk)
            
            # 添加实体节点
            for entity, label in entities:
                self.graph.add_node(entity, type=label)
            
            # 添加关系边
            for subject, relation, object_ in relations:
                # 检查实体是否在图中
                if subject in self.graph and object_ in self.graph:
                    self.graph.add_edge(subject, object_, relation=relation)
                # 如果实体不在图中，尝试添加它们
                elif subject not in self.graph:
                    self.graph.add_node(subject, type="NOUN_PHRASE")
                    self.graph.add_edge(subject, object_, relation=relation)
                elif object_ not in self.graph:
                    self.graph.add_node(object_, type="NOUN_PHRASE")
                    self.graph.add_edge(subject, object_, relation=relation)
    
    def visualize(self, output_file: str = "knowledge_graph.png"):
        """
        改进的可视化方法，使用不同颜色表示不同类型的实体
        """
        plt.figure(figsize=(15, 10))
        pos = nx.spring_layout(self.graph, k=1, iterations=50)
        
        # 按实体类型分组绘制节点
        for entity_type, color in self.entity_colors.items():
            nodes = [node for node, attrs in self.graph.nodes(data=True) 
                    if attrs.get('type') == entity_type]
            if nodes:
                nx.draw_networkx_nodes(self.graph, pos, nodelist=nodes,
                                     node_color=color, node_size=2000,
                                     alpha=0.7, label=entity_type)
        
        # 绘制边
        nx.draw_networkx_edges(self.graph, pos, edge_color='gray',
                             arrows=True, arrowsize=20, width=2)
        
        # 添加节点标签，处理特殊字符
        labels = {node: node.replace('$', '\\$').replace('_', '\\_') 
                 for node in self.graph.nodes()}
        nx.draw_networkx_labels(self.graph, pos, labels=labels, font_size=8)
        
        # 添加边的标签，处理特殊字符
        edge_labels = {}
        for u, v, data in self.graph.edges(data=True):
            relation = data.get('relation', '')
            if relation:
                edge_labels[(u, v)] = relation.replace('$', '\\$').replace('_', '\\_')
        
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels,
                                   font_size=6)
        
        plt.legend(scatterpoints=1, frameon=False, labelspacing=1)
        plt.axis('off')
        
        # 保存图片时使用更高的DPI和更宽松的边界
        plt.savefig(output_file, dpi=300, bbox_inches='tight', 
                   pad_inches=0.5, format='png')
        plt.close()
    
    def export_to_csv(self, output_file: str = "knowledge_graph.csv"):
        """
        导出更详细的知识图谱数据
        """
        # 创建节点数据
        nodes_data = []
        for node, attrs in self.graph.nodes(data=True):
            nodes_data.append({
                'entity': node,
                'type': attrs.get('type', '')
            })
        
        # 创建边数据
        edges_data = []
        for u, v, data in self.graph.edges(data=True):
            edges_data.append({
                'source': u,
                'target': v,
                'relation': data.get('relation', '')
            })
        
        # 保存节点数据
        pd.DataFrame(nodes_data).to_csv(f"nodes_{output_file}", index=False)
        # 保存边数据
        pd.DataFrame(edges_data).to_csv(f"edges_{output_file}", index=False)
    
    def generate_neo4j_queries(self, output_file: str = "neo4j_queries.cypher") -> str:
        """
        生成Neo4j Cypher查询语句
        """
        queries = []
        
        # 1. 创建约束
        constraints = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Person) REQUIRE n.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Organization) REQUIRE n.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Location) REQUIRE n.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Date) REQUIRE n.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Product) REQUIRE n.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Event) REQUIRE n.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:WorkOfArt) REQUIRE n.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Law) REQUIRE n.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Language) REQUIRE n.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Entity) REQUIRE n.name IS UNIQUE"
        ]
        queries.extend(constraints)
        
        # 2. 创建节点
        for node, attrs in self.graph.nodes(data=True):
            entity_type = attrs.get('type', 'NOUN_PHRASE')
            neo4j_label = self.neo4j_labels.get(entity_type, 'Entity')
            # 转义单引号
            node_name = node.replace("'", "\\'")
            query = f"MERGE (n:{neo4j_label} {{name: '{node_name}'}})"
            queries.append(query)
        
        # 3. 创建关系
        for u, v, data in self.graph.edges(data=True):
            relation = data.get('relation', 'RELATED_TO')
            # 转义单引号
            u_name = u.replace("'", "\\'")
            v_name = v.replace("'", "\\'")
            relation = relation.replace("'", "\\'")
            query = f"""
            MATCH (a), (b)
            WHERE a.name = '{u_name}' AND b.name = '{v_name}'
            MERGE (a)-[r:{relation.upper()}]->(b)
            """
            queries.append(query)
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(queries))
        
        return '\n'.join(queries)
    
    def get_statistics(self) -> Dict:
        """
        获取知识图谱的统计信息
        """
        return {
            'num_nodes': self.graph.number_of_nodes(),
            'num_edges': self.graph.number_of_edges(),
            'entity_types': len(set(attrs.get('type') for _, attrs in self.graph.nodes(data=True))),
            'relation_types': len(set(data.get('relation') for _, _, data in self.graph.edges(data=True)))
        }

def process_document(file_path: str, output_prefix: str = None) -> None:
    """
    处理文档并生成知识图谱
    """
    # 获取文件扩展名
    file_ext = Path(file_path).suffix.lower()
    
    # 提取文本
    print("正在提取文本...")
    if file_ext == '.pdf':
        text = DocumentProcessor.extract_text_from_pdf(file_path)
    elif file_ext in ['.docx', '.doc']:
        text = DocumentProcessor.extract_text_from_docx(file_path)
    else:
        print(f"不支持的文件类型: {file_ext}")
        return
    
    if not text:
        print("未能从文档中提取到文本")
        return
    
    # 设置输出文件名前缀
    if output_prefix is None:
        output_prefix = Path(file_path).stem
    
    # 创建知识图谱构建器
    print("正在构建知识图谱...")
    kg_builder = KnowledgeGraphBuilder()
    kg_builder.build_graph(text)
    
    # 获取统计信息
    stats = kg_builder.get_statistics()
    print("\n知识图谱统计信息：")
    print(f"节点数量: {stats['num_nodes']}")
    print(f"边数量: {stats['num_edges']}")
    print(f"实体类型数量: {stats['entity_types']}")
    print(f"关系类型数量: {stats['relation_types']}")
    
    # 可视化
    print("\n正在生成可视化...")
    kg_builder.visualize(f"{output_prefix}_graph.png")
    
    # 导出到CSV
    print("正在导出数据...")
    kg_builder.export_to_csv(f"{output_prefix}_graph.csv")
    
    # 生成Neo4j查询
    print("正在生成Neo4j查询...")
    kg_builder.generate_neo4j_queries(f"{output_prefix}_queries.cypher")
    
    print(f"\n处理完成！输出文件：")
    print(f"- {output_prefix}_graph.png（可视化图谱）")
    print(f"- nodes_{output_prefix}_graph.csv（节点数据）")
    print(f"- edges_{output_prefix}_graph.csv（关系数据）")
    print(f"- {output_prefix}_queries.cypher（Neo4j查询语句）")

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='从文档构建知识图谱')
    parser.add_argument('file_path', help='输入文件路径（支持PDF和Word文档）')
    parser.add_argument('--output', '-o', help='输出文件前缀（可选）')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 处理文档
    process_document(args.file_path, args.output)

if __name__ == "__main__":
    main() 