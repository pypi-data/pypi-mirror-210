import logging
from logging import NullHandler

from dashscope.aigc.conversation import Conversation, History, HistoryItem
from dashscope.aigc.generation import Generation
from dashscope.aigc.image_synthesis import ImageSynthesis
from dashscope.audio.asr.transcription import Transcription
from dashscope.common.api_key import save_api_key
from dashscope.common.env import (api_key, api_key_file_path,
                                  base_http_api_url, base_websocket_api_url)
from dashscope.deployment import Deployment
from dashscope.file import File
from dashscope.finetune import FineTune
from dashscope.model import Model

__all__ = [
    base_http_api_url, base_websocket_api_url, api_key, api_key_file_path,
    save_api_key, Conversation, Generation, History, HistoryItem,
    ImageSynthesis, Transcription, File, Deployment, FineTune, Model
]

logging.getLogger(__name__).addHandler(NullHandler())
