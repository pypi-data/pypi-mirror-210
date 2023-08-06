# vector-quantize-tf
[![PyPI](https://img.shields.io/pypi/v/vector-quantize-tf.svg)](https://pypi.org/project/vector-quantize-tf)

残差ベクトル量子化のtensorflowの実装

# インストール
```
pip install vector-quantize-tf
```

# 使い方
```py
from vector_quantize_tf import ResidualVQ

residual_vq = ResidualVQ(
    codebook_size=1024,
    embedding_dim=512,
    num_quantizers=8,
    batch_size=8,
    ema_decay=0.99,
    threshold_ema_dead_code=2,
    commitment_cost=1.0,
)
```
