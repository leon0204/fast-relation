import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from app.settings import settings
from loguru import logger
from typing import List, Dict, Any, Tuple
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


class CHATService:
    def __init__(self, quantize=False):
        try:
            logger.info("正在加载CHAT模型...")
            here = os.path.dirname(os.path.abspath(__file__))
            self.model_dir = os.path.join(here, '../pretrained_models/glm-4-9b-chat')
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir, trust_remote_code=True)

            # 直接在初始化时加载模型（避免重复加载）
            self.model = self._load_model(quantize)
            logger.success("CHAT模型加载完成")

        except Exception as e:
            logger.error(f"加载CHAT模型失败: {str(e)}")
            raise

    def _load_model(self, quantize=False):
        """内部方法：加载模型（支持量化）"""
        model_kwargs = {"torch_dtype": torch.float32}
        if quantize:
            try:
                import bitsandbytes
                model_kwargs.update({
                    "load_in_8bit": True,
                    "device_map": "auto"
                })
            except ImportError:
                print("警告: 未安装bitsandbytes，将使用全精度CPU模式")

        model = AutoModelForCausalLM.from_pretrained(
            self.model_dir,
            trust_remote_code=True,
            **model_kwargs
        ).cpu()
        return model

    def generate(self, prompt: str, max_length: int = 30, temperature: float = 0.7) -> str:
        """生成文本补全（直接对外暴露的API方法）"""
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt").cpu()

        with torch.no_grad():
            output = self.model.generate(
                input_ids,
                max_length=max_length,
                do_sample=True,
                temperature=temperature,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id
            )

        completion = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return completion[len(prompt):].strip()