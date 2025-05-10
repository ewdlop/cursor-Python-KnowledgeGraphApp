import spacy
import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict, Set
import pandas as pd
from collections import defaultdict

class KnowledgeGraphBuilder:
    def __init__(self):
        # 加载spaCy模型
        self.nlp = spacy.load("en_core_web_sm")
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
        # 提取实体和关系
        entities = self.extract_entities(text)
        relations = self.extract_relations(text)
        
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
        
        # 添加节点标签
        nx.draw_networkx_labels(self.graph, pos, font_size=8)
        
        # 添加边的标签
        edge_labels = nx.get_edge_attributes(self.graph, 'relation')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels,
                                   font_size=6)
        
        plt.legend(scatterpoints=1, frameon=False, labelspacing=1)
        plt.axis('off')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
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

def main():
    # 示例文本
    sample_text = """
    Ross Eustace Geller[2] (born c. 1968)[3] portrayed by David Schwimmer, is one of the six main characters of the NBC sitcom Friends. Ross is considered by many to be the most intelligent member of the group and is noted for his goofy but lovable demeanor.[4] His relationship with Rachel Green was included in TV Guide's list of the best TV couples of all time, as well as Entertainment Weekly's "30 Best 'Will They/Won't They?' TV Couples".[5] Kevin Bright, who was one of the executive producers of the show, had worked with Schwimmer before, so the writers were already developing Ross's character in Schwimmer's voice. Hence, Schwimmer was the first person to be cast on the show.[6]
    """
    
    # 创建知识图谱构建器
    kg_builder = KnowledgeGraphBuilder()
    
    # 构建知识图谱
    kg_builder.build_graph(sample_text)
    
    # 获取统计信息
    stats = kg_builder.get_statistics()
    print("\n知识图谱统计信息：")
    print(f"节点数量: {stats['num_nodes']}")
    print(f"边数量: {stats['num_edges']}")
    print(f"实体类型数量: {stats['entity_types']}")
    print(f"关系类型数量: {stats['relation_types']}")
    
    # 可视化
    kg_builder.visualize()
    
    # 导出到CSV
    kg_builder.export_to_csv()
    
    print("\n知识图谱已生成！请查看以下文件：")
    print("- knowledge_graph.png（可视化图谱）")
    print("- nodes_knowledge_graph.csv（节点数据）")
    print("- edges_knowledge_graph.csv（关系数据）")

if __name__ == "__main__":
    main() 