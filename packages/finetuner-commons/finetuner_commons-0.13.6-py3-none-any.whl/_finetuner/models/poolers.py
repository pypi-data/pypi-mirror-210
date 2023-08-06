from typing import Optional

import torch
import torch.nn.functional as F
from torch import nn
from torch.nn.parameter import Parameter


class GeM(nn.Module):
    def __init__(self, p: int = 3, eps: float = 1e-6):
        super().__init__()
        self.p = Parameter(torch.ones(1) * p)
        self.eps = eps

    def forward(self, x):
        return self._gem(x, p=self.p, eps=self.eps)

    def __repr__(self):
        return (
            self.__class__.__name__
            + '('
            + 'p='
            + '{:.4f}'.format(self.p.data.tolist()[0])
            + ', '
            + 'eps='
            + str(self.eps)
            + ')'
        )

    @staticmethod
    def _gem(x: torch.Tensor, p: int = 3, eps: float = 1e-6):
        return F.avg_pool2d(x.clamp(min=eps).pow(p), (x.size(-2), x.size(-1))).pow(
            1.0 / p
        )

    @staticmethod
    def gem_1d(
        x: torch.Tensor,
        p: float = 3.0,
        eps: float = 1e-6,
        dim: int = 1,
        total: Optional[torch.Tensor] = None,
    ):
        if total is None:
            return torch.mean(x.clamp(min=eps).pow(p), dim).pow(1.0 / p)
        else:
            return torch.min(
                torch.div(x.clamp(min=eps).pow(p), total).pow(1.0 / p),
                torch.max(x, 1)[0],
            )
