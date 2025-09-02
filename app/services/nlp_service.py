import numpy as np
import spacy
import jieba
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
from app.settings import settings
from loguru import logger
from typing import List, Dict, Any, Tuple
import os
import re
import torch
import itertools

from app.utils.data_utils import MyTokenizer, get_idx2tag, convert_pos_to_mask
from app.utils.model import SentenceRE
from app.utils.hparams import hparams
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline


class NLPService:
    def __init__(self):
        try:
            logger.info("正在加载NLP模型...")
            self.nlp = spacy.load(settings.NLP_MODEL)
            # self.vectorizer = TfidfVectorizer(tokenizer=self.tokenize_chinese)
            logger.success("NLP模型加载完成")
            # here = os.path.dirname(os.path.abspath(__file__))

            # 3. 向分词器添加自定义分词规则
            self.nlp.tokenizer.pkuseg_update_user_dict(settings.custom_names)

            # tokenizer = AutoTokenizer.from_pretrained(model_dir)
            # model = AutoModelForTokenClassification.from_pretrained(model_dir)
            # self.ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer)


        except Exception as e:
            logger.error(f"加载NLP模型失败: {str(e)}")
            raise

    def tokenize_chinese(self, text: str) -> List[str]:
        """中文分词"""
        return list(jieba.cut(text))

    async def extract_entities(self, text: str) -> List[Tuple[str, str]]:
        """从文本中提取实体"""
        try:
            doc = self.nlp(text)

            spaCy_entities = [(ent.text, ent.label_) for ent in doc.ents if ent.label_ == "PERSON" and 1 < len(ent.text) < 4]
            # logger.debug(f"从文本中提取到 {len(entities)} 个实体")

            text_names = [name for name in settings.custom_names if name in text]
            # print("文本中出现的custom_names名字:", text_names)

            # 4. 找出在文本中出现但未被spaCy识别的名字
            missing_names = []
            for name in text_names:
                if not any(ent[0] == name for ent in spaCy_entities):
                    missing_names.append((name, "PERSON"))

            # print("未被spaCy识别但存在于文本中的名字:", missing_names)

            # 5. 合并结果
            final_entities = spaCy_entities + missing_names

            return final_entities

        except Exception as e:
            # logger.error(f"实体提取失败: {str(e)}")
            raise

    async def extract_relations(self, text: str, entity1: str, entity2: str) -> str:
        try:
            device = hparams.device
            seed = hparams.seed
            torch.manual_seed(seed)

            pretrained_model_path = hparams.pretrained_model_path
            tagset_file = hparams.tagset_file
            model_file = hparams.model_file

            idx2tag = get_idx2tag(tagset_file)
            hparams.tagset_size = len(idx2tag)
            model = SentenceRE(hparams).to(device)
            model.load_state_dict(torch.load(model_file))
            model.eval()

            tokenizer = MyTokenizer(pretrained_model_path)

            match_obj1 = re.search(entity1, text)
            match_obj2 = re.search(entity2, text)
            if match_obj1 and match_obj2:  # 姑且使用第一个匹配的实体的位置
                e1_pos = match_obj1.span()
                e2_pos = match_obj2.span()
                item = {
                    'h': {
                        'name': entity1,
                        'pos': e1_pos
                    },
                    't': {
                        'name': entity2,
                        'pos': e2_pos
                    },
                    'text': text
                }
                tokens, pos_e1, pos_e2 = tokenizer.tokenize(item)
                encoded = tokenizer.bert_tokenizer.batch_encode_plus([(tokens, None)], return_tensors='pt')
                input_ids = encoded['input_ids'].to(device)
                token_type_ids = encoded['token_type_ids'].to(device)
                attention_mask = encoded['attention_mask'].to(device)
                e1_mask = torch.tensor([convert_pos_to_mask(pos_e1, max_len=attention_mask.shape[1])]).to(device)
                e2_mask = torch.tensor([convert_pos_to_mask(pos_e2, max_len=attention_mask.shape[1])]).to(device)

                with torch.no_grad():
                    logits = model(input_ids, token_type_ids, attention_mask, e1_mask, e2_mask)[0]
                    logits = logits.to(torch.device('cpu'))
                return format(idx2tag[logits.argmax(0).item()])

            else:
                if match_obj1 is None:
                    print('实体1不在句子中')
                if match_obj2 is None:
                    print('实体2不在句子中')

        except Exception as e:
            logger.error(f"关系提取失败: {str(e)}")
            raise

    async def extract_all_relations(self, text: str, entities: list[tuple[str, str]], source: str = None) -> list[dict]:
        """
        将实体两两配对并提取关系

        参数:
            text: 原始文本
            entities: 实体列表，格式如 [('王学兵', 'PERSON'), ('冯钰棋', 'PERSON')]

        返回:
            关系列表，每个元素包含实体对和关系
        """
        relations = []

        # 1. 获取所有实体名称（去重）
        unique_entities = list(
            {ent[0] for ent in entities if ent[1] == "PERSON" and 1 < len(ent[0]) < 4})  # 只处理PERSON类型

        # 2. 生成所有可能的实体对组合（无序排列）
        for entity1, entity2 in itertools.combinations(unique_entities, 2):
            try:
                device = hparams.device
                seed = hparams.seed
                torch.manual_seed(seed)

                pretrained_model_path = hparams.pretrained_model_path
                tagset_file = hparams.tagset_file
                model_file = hparams.model_file

                idx2tag = get_idx2tag(tagset_file)
                hparams.tagset_size = len(idx2tag)
                model = SentenceRE(hparams).to(device)
                model.load_state_dict(torch.load(model_file))
                model.eval()

                tokenizer = MyTokenizer(pretrained_model_path)

                match_obj1 = re.search(entity1, text)
                match_obj2 = re.search(entity2, text)
                if match_obj1 and match_obj2:  # 姑且使用第一个匹配的实体的位置
                    e1_pos = match_obj1.span()
                    e2_pos = match_obj2.span()
                    item = {
                        'h': {
                            'name': entity1,
                            'pos': e1_pos
                        },
                        't': {
                            'name': entity2,
                            'pos': e2_pos
                        },
                        'text': text
                    }
                    tokens, pos_e1, pos_e2 = tokenizer.tokenize(item)
                    encoded = tokenizer.bert_tokenizer.batch_encode_plus([(tokens, None)], return_tensors='pt')
                    input_ids = encoded['input_ids'].to(device)
                    token_type_ids = encoded['token_type_ids'].to(device)
                    attention_mask = encoded['attention_mask'].to(device)
                    e1_mask = torch.tensor([convert_pos_to_mask(pos_e1, max_len=attention_mask.shape[1])]).to(device)
                    e2_mask = torch.tensor([convert_pos_to_mask(pos_e2, max_len=attention_mask.shape[1])]).to(device)

                    with torch.no_grad():
                        logits = model(input_ids, token_type_ids, attention_mask, e1_mask, e2_mask)[0]
                        logits = logits.to(torch.device('cpu'))
                    relation = format(idx2tag[logits.argmax(0).item()])
                    if relation:  # 只保留有效关系
                        relations.append({
                            "head": entity1,
                            "tail": entity2,
                            "relation": relation,
                            "text": text,
                            "source": source
                        })

                else:
                    if match_obj1 is None:
                        print('实体1不在句子中')
                    if match_obj2 is None:
                        print('实体2不在句子中')

            except Exception as e:
                print(f"提取关系失败: {entity1}->{entity2}, 错误: {str(e)}")

        return relations

    async def extract_attributes_with_rules(self, text: str, entity: str) -> List[Dict[str, str]]:
        """从文本中提取给定实体的属性，返回格式为 [{"k": "v"}, ...]"""
        attributes = []
        sentences = re.split(r'(?<=。)', text)  # 按句号分句

        for sentence in sentences:
            if entity not in sentence:
                continue

            # 1. 年龄
            if age_match := re.search(rf"{re.escape(entity)}[^。]*?今年(\d+)岁", sentence):
                attributes.append({"age": age_match.group(1)})

            # 2. 出生年份
            if birth_match := re.search(rf"{re.escape(entity)}[^。]*(?:生于|出生于)(\d{{4}})年", sentence):
                attributes.append({"birth_year": birth_match.group(1)})

            # 3. 职业
            if occupation_match := re.search(rf"{re.escape(entity)}[^。]*(?:职业是|是一名|职业)([^。，]+)", sentence):
                attributes.append({"occupation": occupation_match.group(1).strip()})

            # 4. 住址
            if address_match := re.search(rf"{re.escape(entity)}[^。]*(?:住在|居住于)([^。，]+)", sentence):
                attributes.append({"address": address_match.group(1).strip()})

            # 5. 爱好
            if hobby_match := re.search(rf"{re.escape(entity)}[^。]*(?:爱好是|喜欢)([^。，]+)", sentence):
                attributes.append({"hobby": hobby_match.group(1).strip()})

            # 6. 身份
            if identity_match := re.search(rf"{re.escape(entity)}是([^。，]+?的[^。，]+)", sentence):
                attributes.append({"identity": identity_match.group(1).strip()})

            # 7. 角色
            if role_match := re.search(rf"{re.escape(entity)}[^。]*(?:饰演|扮演|角色是)([^。，]+)", sentence):
                attributes.append({"role": role_match.group(1).strip()})

        return attributes

    # async def calculate_similarity(self, text1: str, text2: str) -> float:
    #     """计算文本相似度"""
    #     try:
    #         vectors = self.vectorizer.fit_transform([text1, text2])
    #         similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    #         logger.debug(f"文本相似度计算完成: {similarity:.4f}")
    #         return similarity
    #     except Exception as e:
    #         logger.error(f"相似度计算失败: {str(e)}")
    #         raise

    # async def find_similar_entities(
    #         self,
    #         entities: List[Dict[str, Any]],
    #         threshold: float = None
    # ) -> List[Dict[str, Any]]:
    #     """发现相似实体"""
    #     try:
    #         if len(entities) < 2:
    #             return []
    #
    #         threshold = threshold or float(settings.SIMILARITY_THRESHOLD)
    #         texts = [e.get('name', '') + " " + e.get('description', '') for e in entities]
    #         sim_matrix = cosine_similarity(self.vectorizer.fit_transform(texts))
    #
    #         similar_pairs = []
    #         for i in range(len(entities)):
    #             for j in range(i + 1, len(entities)):
    #                 if sim_matrix[i][j] >= threshold:
    #                     similar_pairs.append({
    #                         'entity1': entities[i],
    #                         'entity2': entities[j],
    #                         'similarity': float(sim_matrix[i][j])
    #                     })
    #
    #         logger.info(f"发现 {len(similar_pairs)} 对相似实体 (阈值={threshold})")
    #         return similar_pairs
    #     except Exception as e:
    #         logger.error(f"相似实体发现失败: {str(e)}")
    #         raise

    # async def disambiguation(self, original_text: str) -> dict[str, list[dict[str, str | Any]] | str]:
    #     try:
    #         raw_results = self.ner_pipeline(original_text)
    #         entities = []
    #         current_entity = None
    #
    #         for item in raw_results:
    #             # 转换所有numpy数值为Python原生类型
    #             item = {k: float(v) if isinstance(v, np.float32) else v for k, v in item.items()}
    #
    #             if item['entity'].startswith('B-'):
    #                 if current_entity:
    #                     entities.append(current_entity)
    #                 current_entity = {
    #                     'name': item['word'],
    #                     'type': item['entity'][2:],
    #                     'confidence': float(item['score']),  # 显式转换
    #                     'start': item['start'],
    #                     'end': item['end']
    #                 }
    #             elif item['entity'].startswith('I-') and current_entity:
    #                 current_entity['name'] += item['word'].replace('##', '')
    #                 current_entity['end'] = item['end']
    #                 current_entity['confidence'] = max(
    #                     current_entity['confidence'],
    #                     float(item['score'])  # 取最高置信度
    #                 )
    #
    #         if current_entity:
    #             entities.append(current_entity)
    #
    #         return {
    #             "text": original_text,
    #             "entities": entities
    #         }
    #     except Exception as e:
    #         logger.error(f"实体消岐失败: {str(e)}")
    #         raise
