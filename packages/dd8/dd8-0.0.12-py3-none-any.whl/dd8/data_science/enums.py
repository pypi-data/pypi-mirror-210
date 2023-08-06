# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 14:54:00 2022

@author: yqlim
"""
import enum

@enum.unique
class ENUM_MACHINE_LEARNING_TYPE(enum.Enum):
    SUPERVISED = 1
    UNSUPERVISED = 2
    REINFORCEMENT = 3
