from typing import Optional

import anndata as ad

from .scatterplots import embedding, Spatial_class


def Spatial_map(adata, cls):
    cls = str(cls)
    embedding(adata, basis='X_spacial', color=f'{cls}', frameon=False, save=f'_spacial_{cls}.png')



def Spatial_class_location(
        adata: ad.AnnData,
        cls: str,  # TIC和XY文件路径
        *,
        n: str = None,  # 不同的类别
) -> Optional[ad.AnnData]:
    cls = str(cls)
    if n is None:
        for i in adata.obs[cls].values.categories.values:
            Spatial_class(adata, cls, i)

    else:
        Spatial_class(adata, cls, n)


