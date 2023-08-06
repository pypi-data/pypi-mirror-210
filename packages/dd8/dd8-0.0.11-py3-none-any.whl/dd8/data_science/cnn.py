# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 16:07:00 2022

@author: yqlim
"""
from typing import Union, List
import torch.nn as nn

class ConvolutionalNeuralNetwork(nn.Module):
    def __init__(self, input_dim: int, output_dim: int):
        super(ConvolutionalNeuralNetwork, self).__init__()
        self.components = []

    def conv2d_block(self, input_channels: int, output_channels: int, dropout: float,
                        kernel_size: int, stride: int, padding: int, **kwargs) -> nn.Sequential:
        self.components.append( nn.Sequential(
            nn.Conv2d(in_channels=input_channels, out_channels=output_channels, **kwargs),
            nn.BatchNorm2d(num_features=output_channels),
            nn.ReLU(),
            nn.Dropout2d(p=dropout)
        ))
    
    def conv1d_block(self, input_channels: int, output_channels: int, dropout: float,
                        kernal_size: int, stride: int, padding: int, **kwargs):
        self.components.append( nn.Sequential(
            nn.Conv1d(in_channels=input_channels, out_channels=output_channels, **kwargs),
            nn.BatchNorm1d(num_features=input_channels),
            nn.ReLU(),
            nn.Dropout1d(p=dropout)
        ))

    def fully_connected_block(self, num_hidden: int, num_labels: int, dropout: float):
        self.components.append( nn.Sequential(
            nn.Linear(num_hidden=num_hidden, num_labels=num_labels),
            nn.ReLu(),
            nn.Dropout(p=dropout)
        ))

    def forward(self, X):
        _ = self.components[0](X)
        for component in self.components[1:]:
            _ = component(_)

        return _