import streamlit as st
from abc import ABC, abstractmethod
import keras
import numpy as np
from transformers import BertTokenizer, BertModel
import torch
import json

@st.cache_data
def load_metrics():
    with open("./demo/resources/metrics.json", "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_resource
def load_vanilla_bert():
    return VanillaBertModel()
    
@st.cache_resource
def load_custom_bert():
    return PreTrainedBertModel()
    
    
class BertAbstractModel(ABC):
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
        self.cut_model = self._load_cut_model()
    
    @abstractmethod
    def _load_cut_model(self):
        pass
    
    @abstractmethod
    def _get_word_embeddings(self, sentence):
        pass
    
    def _compute_mean_embedding(self, word_embeddings, attention_mask):
        padding_mask = attention_mask.numpy() # (1, seq_len)

        # Remove CLS and SEP token
        content_mask = padding_mask.copy()
        content_mask[:, 0] = 0

        sep_positions = padding_mask.sum(axis=1).astype(int) - 1
        for i, sep_pos in enumerate(sep_positions):
            content_mask[i, sep_pos] = 0

        # Mean
        mask_expanded = content_mask[:, :, np.newaxis]  # (1, seq_len, 1)
        sum_embeddings = np.sum(word_embeddings * mask_expanded, axis=1)
        sum_mask = content_mask.sum(axis=1, keepdims=True).clip(min=1e-9)
        embedding = (sum_embeddings / sum_mask)[0]

        return embedding.astype(np.float32)
    
    def get_sentence_embedding(self, sentence):
        word_embeddings, attention_mask = self._get_word_embeddings(sentence)   
        return self._compute_mean_embedding(word_embeddings, attention_mask)
        
    
class VanillaBertModel(BertAbstractModel):
    def _load_cut_model(self):
        return BertModel.from_pretrained("bert-base-uncased")

    def _get_word_embeddings(self, sentence):
        tokens = self.tokenizer(
            sentence,
            return_tensors="pt",
            padding="max_length",
            truncation=True,
            max_length=512
        )
       
        with torch.no_grad():
            hidden = self.cut_model(**tokens).last_hidden_state.numpy()
            
        return hidden, tokens["attention_mask"]
 
        
class PreTrainedBertModel(BertAbstractModel):
    def _load_cut_model(self):
        return keras.models.load_model("./models/K-COG-BERT.keras")

    def _get_word_embeddings(self, sentence):
        tokens = self.tokenizer(
            sentence,
            return_tensors="pt",
            padding="max_length",
            truncation=True,
            max_length=512
        )

        features = {
            "token_ids": tokens["input_ids"],
            "padding_mask": tokens["attention_mask"],
            "segment_ids": tokens["token_type_ids"]
        }

        hidden = self.cut_model.predict(features)
        
        return hidden, tokens["attention_mask"]