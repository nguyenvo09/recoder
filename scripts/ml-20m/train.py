import numpy as np

import pandas as pd

from recoder import Recoder
from recoder.data import RecommendationDataset
from recoder.nn import MSELoss, MultinomialNLLLoss
from recoder.metrics import AveragePrecision, Recall, NDCG

from torch.nn import BCEWithLogitsLoss

import torch

# torch.set_num_threads(4)

data_dir = 'data/ml-20m/pro_sg/'
model_dir = 'models/ml-20m/'

common_params = {
  'user_col': 'uid',
  'item_col': 'sid',
  'inter_col': 'watched',
}

train_df = pd.read_csv(data_dir + 'train.csv')
val_tr_df = pd.read_csv(data_dir + 'validation_tr.csv')
val_te_df = pd.read_csv(data_dir + 'validation_te.csv')

train_dataset = RecommendationDataset(data=train_df, **common_params)
val_te_dataset = RecommendationDataset(data=val_te_df, **common_params)
val_tr_dataset = RecommendationDataset(data=val_tr_df, **common_params,
                                       target_dataset=val_te_dataset)

params = {
  'model_params': {
    'hidden_layers_sizes': [200],
    'activation_type': 'tanh',
    'is_constrained': False,
    'dropout_prob': 0.0,
    'noise_prob': 0.5,
    'last_layer_act': 'none',
  },
  'batch_size': 500,
  'optimizer_type': 'adam',
  'lr': 1e-3,
  'weight_decay': 2e-5,
  'num_epochs': 100,
  'optimizer_lr_milestones': [60, 80],
  'loss_module': BCEWithLogitsLoss(size_average=False),
  'train_dataset': train_dataset,
  'val_dataset': val_tr_dataset,
  'apply_ns': True,
  'use_cuda': False,
  # 'model_file': model_dir + 'bce_ns_d_0.0_n_0.5_200_epoch_50.model',
}

mode = 'train'
trainer = Recoder(mode=mode, **params)
model_checkpoint = model_dir + 'bce_ns_d_0.0_n_0.5_200'

metrics = [Recall(k=20, normalize=True), Recall(k=50, normalize=True),
           NDCG(k=100)]

try:
  trainer.train(summary_frequency=10, val_epoch_freq=1,
                model_checkpoint=model_checkpoint, checkpoint_freq=10,
                eval_num_recommendations=100, metrics=metrics)
except (KeyboardInterrupt, SystemExit):
  trainer.save_state(model_checkpoint)
  raise