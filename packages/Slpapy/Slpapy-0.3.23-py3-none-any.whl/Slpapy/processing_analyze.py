from typing import Optional
import anndata as ad
import numpy as np
import pandas as pd
import scanpy as sc
from scipy.sparse import csr_matrix
from sklearn import preprocessing
from sklearn.cluster import KMeans
from .Spatial_map_pic import Spatial_map,Spatial_class_location

sc.settings.verbosity = 3  # 设置日志等级: errors (0), warnings (1), info (2), hints (3)
sc.logging.print_header()
sc.settings.set_figure_params(dpi=720, facecolor='white')


def XYadata(adata):
    df = preprocessing.normalize(np.c_[np.array(adata.obs['X']), np.array(adata.obs['Y'])])
    counts = csr_matrix(df, dtype=np.float32)
    XYmatrix = ad.AnnData(counts)
    # 为x和y轴提供索引
    XYmatrix.obs_names = adata.obs_names
    XYmatrix.var_names = ['X_a', 'Y_a']
    t = adata.obs
    adata = ad.concat([adata, XYmatrix], axis=1)
    adata.obs = t
    adata.obsm['X_spacial'] = np.array(adata.obs.loc[:, 'X':'Y'])
    print('Space integration complete')
    return adata


def pp_analyze(adata, onlyhighly):
    # 显示在所有细胞中在每个单细胞中产生最高计数分数的脂质
    # sc.pl.highest_expr_genes(adata, n_top=20, save='_highest_expr_protein.png')
    # 小提琴图：表达基因的数量，每个细胞包含的表达量，线粒体基因表达量的百分比。
    adata.var['mt'] = adata.var_names.str.startswith('MT-')  # 将线粒体基因标记为 mt
    sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], percent_top=None,
                               log1p=False, inplace=True)
    sc.pl.violin(adata, 'total_counts', jitter=0.4, multi_panel=True,
                 save='_total_counts.png')
    adata = adata[adata.obs['total_counts'] != 0, :]
    # 归一化，使得不同细胞样本间可比
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    # 存储数据
    adata.raw = adata
    # 选择高变异基因
    if onlyhighly == True:
        sc.pp.highly_variable_genes(adata, min_mean=0.0125, max_mean=3, min_disp=0.5)
        sc.pl.highly_variable_genes(adata, save='_highly_variable_lipid.png')
        adata = adata[:, adata.var.highly_variable]
    adata.obsm['X_spacial'] = np.array(adata.obs.loc[:, 'X':'Y'])
    # 回归每个细胞的总计数和表达的线粒体基因的百分比的影响。
    sc.pp.regress_out(adata, ['total_counts', 'pct_counts_mt'])
    # 保存mz值
    mz = adata.var
    mz.to_csv('./mz.csv')
    adata.write('./pp_done.h5ad')
    return adata


def se_analyze(adata, n_neighbors, n_pcs, resolution):
    # 将每个脂质缩放到单位方差。阈值超过标准偏差 10。，如非高斯分布，则不建议使用
    # sc.pp.scale(adata, max_value=10)
    # 绘制 PCA 图降维
    sc.tl.pca(adata, svd_solver='arpack')  #
    # Neighborhood graph使用数据矩阵的 PCA 表示来计算细胞的邻域图
    sc.pp.neighbors(adata, n_neighbors=n_neighbors, n_pcs=n_pcs, )
    sc.tl.umap(adata, min_dist=0.01, alpha=1, spread=2)  #
    # Leiden 图聚类
    # 计算
    sc.tl.leiden(adata, resolution=resolution)
    return adata


def third_analyze(adata):
    sc.pl.pca_variance_ratio(adata, log=True, save='_spacial.png')
    sc.pl.umap(adata, color=['leiden'], save='_spacial.png')
    sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon')
    result = adata.uns['rank_genes_groups']
    groups = result['names'].dtype.names
    res = pd.DataFrame({group + '_' + key: result[key][group] for group in groups for key in
                        ['names', 'pvals', 'logfoldchanges', 'pvals_adj', 'scores']})
    res.to_csv("dif.csv")
    sc.pl.rank_genes_groups(adata, n_genes=25, sharey=False, save='_Wilcoxon.png')
    sc.pl.rank_genes_groups_dotplot(adata, n_genes=10, save='_dotplot_Wilcoxon.png')
    return adata




def Basic_processing_flow(
        adata: ad.AnnData,
        *,
        use_spacial: bool = False,
        orgknn: bool = False,
        onlyhighly: bool = False,
        n_neighbors: int = 20,
        n_pcs: int = 30,
        resolution: int = 0.8

) -> Optional[ad.AnnData]:
    adata = pp_analyze(adata, onlyhighly)
    if use_spacial == True:
        adata = XYadata(adata)
        adata = se_analyze(adata, n_neighbors, n_pcs, resolution)
        adata = third_analyze(adata)
        adata.obs['leidenXY'] = adata.obs['leiden']
        Spatial_map(adata, 'leidenXY')
    elif orgknn == True:
        adata = se_analyze(adata, n_neighbors, n_pcs, resolution)
        estimator = KMeans(n_clusters=adata.obs['leiden'].values.codes.max() + 1)  # 构造聚类器
        estimator.fit(
            np.c_[adata.X, preprocessing.normalize(np.c_[np.array(adata.obs['X']), np.array(adata.obs['Y'])])])
        label_pred = estimator.labels_  # 获取聚类标签
        adata.obs['KNNlableXY'] = label_pred.T
        adata.obs['KNNlableXY'] = adata.obs['KNNlableXY'].astype('category')
        sc.tl.rank_genes_groups(adata, 'KNNlableXY', method='wilcoxon')
        sc.pl.rank_genes_groups(adata, n_genes=25, sharey=False, save='_KXY_Wilcoxon.png')
        sc.pl.rank_genes_groups_dotplot(adata, n_genes=10, save='_dotplot_Wilcoxon.png')
        result = adata.uns['rank_genes_groups']
        groups = result['names'].dtype.names
        res = pd.DataFrame({group + '_' + key: result[key][group] for group in groups for key in
                            ['names', 'pvals', 'logfoldchanges', 'pvals_adj', 'scores']})
        res.to_csv("dif.csv")
        sc.pl.pca_variance_ratio(adata, log=True, save='_KXY.png')
        sc.pl.umap(adata, color=['KNNlableXY'], save='_KXY.png')
        Spatial_map(adata, 'KNNlableXY')
    else:
        adata = se_analyze(adata, n_neighbors, n_pcs, resolution)
        adata = third_analyze(adata)
        Spatial_map(adata, 'leiden')

    Spatial_class_location(adata, 'leiden')
    adata.write('./analyze_done.h5ad')
    return adata


#选择上方函数返回的adata数据中obs,根据选择筛选后进行比较
def cluster_compare(
        adata: ad.AnnData,
        list1: list,
        list2: list,
) -> Optional[ad.AnnData]:
    #选择上方函数返回的adata数据中obs,根据选择筛选后进行比较
    bdata = adata[adata.obs['leiden'].isin(list1 + list2), :]
    #对于bdata中的list1和list2在bdata.obs['leidens']进行重新编号
    bdata.obs['leidens'] = bdata.obs['leiden'].cat.rename_categories(
        {i: 'list1' for i in list1} | {i: 'list2' for i in list2})
    Spatial_map(bdata, 'leidens')
    sc.pl.rank_genes_groups(bdata, n_genes=25, sharey=False, save='_Wilcoxon.png')
    sc.pl.rank_genes_groups_dotplot(bdata, n_genes=10, save='_dotplot_Wilcoxon.png')
    return bdata




