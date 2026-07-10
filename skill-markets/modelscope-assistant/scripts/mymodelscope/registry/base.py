"""
注册表客户端抽象基类

所有模型源（HuggingFace, CivitAI, ModelScope 等）的 RegistryClient 实现此接口。
"""

from abc import ABC, abstractmethod


class RegistryClient(ABC):
    """模型源注册表客户端抽象基类"""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """返回源标识名称，如 'modelscope', 'huggingface'"""
        ...

    @abstractmethod
    def search_by_hash(self, sha256: str) -> dict | None:
        """通过 SHA256 哈希搜索模型。

        返回标准化模型字典或 None。
        """
        ...

    @abstractmethod
    def search_by_name(self, name: str, limit: int = 5) -> list[dict]:
        """通过名称搜索模型。

        返回标准化模型字典列表。
        """
        ...

    @abstractmethod
    def get_model_info(self, source_id: str) -> dict | None:
        """获取模型详细信息。

        Args:
            source_id: 模型在平台的唯一标识（如 'Qwen/Qwen3-0.5B'）

        返回标准化模型字典或 None。
        """
        ...

    @abstractmethod
    def download(self, source_id: str, save_dir: str) -> str:
        """下载模型到指定目录。

        Args:
            source_id: 模型在平台的唯一标识
            save_dir: 保存目录路径

        Returns:
            模型文件保存到的本地路径。
        """
        ...
