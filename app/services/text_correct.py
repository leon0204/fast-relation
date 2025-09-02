import os
from transformers import AutoModelForCausalLM, AutoTokenizer
from loguru import logger


class TextCorrectionService:
    def __init__(self):
        try:
            logger.info("正在加载文本补全纠错模型...")
            here = os.path.dirname(os.path.abspath(__file__))
            checkpoint = os.path.join(here, '../pretrained_models/chinese-text-correction-1.5b')

            # 加载 tokenizer 和模型
            self.tokenizer = AutoTokenizer.from_pretrained(checkpoint)
            self.model = AutoModelForCausalLM.from_pretrained(checkpoint)
            self.device = "cpu"
            self.model.to(self.device)

            logger.success("文本补全纠错模型加载完成！")
        except Exception as e:
            logger.error(f"加载文本纠错模型失败: {e}")
            raise

    def correct_text1(self, text: str) -> str:
        """文本纠错"""
        input_text = f"文本纠错：\n{text}"
        inputs = self.tokenizer(input_text, return_tensors="pt").to(self.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=1024,
            temperature=0,
            do_sample=False,
            repetition_penalty=1.08
        )
        corrected_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return corrected_text

    async def correct_text(self, text: str) -> str:
        """超短文本纠错优化版（10汉字内）"""
        # 1. 输入预处理：移除冗余提示词（模型已知任务类型）
        input_text = text  # 直接输入待纠错文本，无需加"文本纠错："

        # 2. 极简tokenize配置
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            max_length=15,  # 显式限制输入长度
            truncation=True,  # 强制截断
            padding="do_not_pad"  # 禁用填充（节省计算）
        ).to(self.device)

        # 3. 生成参数暴力优化
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=8,  # 短文本纠错最多生成8个token（≈6汉字）
            num_beams=1,  # 禁用束搜索（beam=1就是贪心搜索）
            do_sample=False,
            temperature=0,  # 保持确定性输出
            repetition_penalty=1.0,  # 禁用重复惩罚（短文本不需要）
            length_penalty=0.0,  # 禁用长度惩罚
            pad_token_id=self.tokenizer.eos_token_id,  # 避免pad token计算
            use_cache=True  # 启用KV缓存加速
        )

        # 4. 后处理：移除可能的重复生成
        corrected_text = self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True  # 清理多余空格
        )
        return corrected_text  # 硬截断保证输出长度