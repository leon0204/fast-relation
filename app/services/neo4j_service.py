from neo4j import GraphDatabase
import logging
from app.schemas.graph import RelationCreate, BulkRelationCreate

logger = logging.getLogger(__name__)


class Neo4jService:
    def __init__(self):
        """
        初始化Neo4j驱动
        :param uri: neo4j://localhost:7687 (集群) 或 bolt://localhost:7687 (单实例)
        :param user: 数据库用户名
        :param password: 密码
        """
        self.driver = GraphDatabase.driver("bolt://47.116.124.192:7687", auth=("neo4j", "neo4j123"))

    def close(self):
        self.driver.close()

    async def create_relation(self, relation: RelationCreate):
        """创建单个关系"""
        cypher = """
        MERGE (head:Person {name: $head})
        MERGE (tail:Person {name: $tail})
        MERGE (head)-[r:%s]->(tail)
        SET r.text = $text,
            r.source = 'NLP',
            r.created_at = datetime()
        """ % relation.relation_type.upper().replace(" ", "_")

        with self.driver.session() as session:
            try:
                session.run(cypher,
                            head=relation.head,
                            tail=relation.tail,
                            text=relation.text)
                logger.info(f"Created relation: {relation.head}->{relation.tail}")
                return True
            except Exception as e:
                logger.error(f"Failed to create relation: {str(e)}")
                raise

    async def bulk_create_relations(self, data: BulkRelationCreate):
        """批量创建关系（更高效）"""
        cypher = """
        UNWIND $relations as rel
        MERGE (head:Person {name: rel.head})
        MERGE (tail:Person {name: rel.tail})
        MERGE (head)-[r:RELATION]->(tail)
        SET r += {text: rel.text, type: rel.type, source: 'NLP'}
        """

        params = {
            "relations": [{
                "head": r.head,
                "tail": r.tail,
                "type": r.relation_type,
                "text": r.text
            } for r in data.relations]
        }

        with self.driver.session() as session:
            try:
                session.run(cypher, params)
                logger.info(f"Created {len(data.relations)} relations")
                return {"status": "success", "count": len(data.relations)}
            except Exception as e:
                logger.error(f"Bulk create failed: {str(e)}")
                raise

    async def infer_transitive_relations(self):
        # 1. 查询满足传递性规则的关系三元组
        query_find = """
        MATCH (a:Person)-[r1:RELATION]->(b:Person)-[r2:RELATION]->(c:Person)
        WHERE r1.type = "KNOWS" AND r2.type = "KNOWS"
        AND NOT (a)-[:RELATION {type: "KNOWS"}]->(c)
        RETURN a.name AS a_name, b.name AS b_name, c.name AS c_name
        """

        # 2. 创建新关系 A→C
        query_create = """
        MATCH (a:Person {name: $a_name}), (c:Person {name: $c_name})
        MERGE (a)-[r:RELATION {type: "KNOWS", text: "Inferred from transitivity", source: "RULE"}]->(c)
        RETURN r
        """

        with self.driver.session() as session:
            # 获取所有需要推理的三元组
            results = session.run(query_find)
            inferred_count = 0

            for record in results:
                print(record["a_name"])
                print(record["c_name"])
                inferred_count += 1

            # 对每个三元组创建新关系

            # for record in results:
            #     session.run(
            #         query_create,
            #         a_name=record["a_name"],
            #         c_name=record["c_name"]
            #     )
            #     inferred_count += 1

            print(f"✅ Inferred {inferred_count} new relations via transitivity")

    async def get_graph_data(self):
            """
            获取图数据，包括节点和关系
            """
            cypher = """
            MATCH (a:Person)-[r:RELATION]->(b:Person)
            RETURN a, r, b
            """
            nodes_set = set()  # 用于存储唯一的节点名称
            nodes_list = []     # 最终的 nodes 列表
            lines_list = []     # 最终的 lines 列表

            with self.driver.session() as session:
                try:
                    result = session.run(cypher)
                    for record in result:
                        a = record["a"]
                        r = record["r"]
                        b = record["b"]

                        # 处理起始节点 a
                        if a["name"] not in nodes_set:
                            nodes_set.add(a["name"])
                            nodes_list.append({
                                "id": a["identity"],  # 使用 name 作为 id，确保唯一性
                                "text": a["name"],
                                "data": {"myicon": a["name"] + "_icon"}  # 示例 data，可根据需求调整
                            })

                        # 处理目标节点 b
                        if b["name"] not in nodes_set:
                            nodes_set.add(b["name"])
                            nodes_list.append({
                                "id": b["name"],
                                "text": b["name"],
                                "data": {"myicon": b["name"] + "_icon"}  # 示例 data，可根据需求调整
                            })

                        # 处理关系 r
                        lines_list.append({
                            "from": a["name"],
                            "to": b["name"],
                            "text": r["type"]
                        })

                    logger.info(f"获取到 {len(nodes_list)} 个节点和 {len(lines_list)} 条关系")
                    return {"nodes": nodes_list, "lines": lines_list}

                except Exception as e:
                    logger.error(f"获取图数据失败: {str(e)}")
                    raise

neo4j_service = Neo4jService()
