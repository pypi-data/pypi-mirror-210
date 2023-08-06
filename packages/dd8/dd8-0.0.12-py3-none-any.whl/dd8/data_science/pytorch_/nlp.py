import torch
import torch.nn as nn
import torch.optim as optim

class LanguageClassifier(nn.Module):
    def __init__(self) -> None:
        super().__init__()

        self.layers = []

    def add_embedding(self, embedding) -> None:
        self.embedding = embedding

    def add_layer(self, layer) -> None:
        self.layers.append(layer)

    def build(self) -> None:
        # self.fc = nn.Linear(, 1)
        pass

    def forward(self, text, text_lengths):
        embedded = self.embedding(text)
        output, hidden = self.layers[0](embedded)
        for layer in self.layers[1:]:
            output, hidden = layer(output)
          
        return self.fc