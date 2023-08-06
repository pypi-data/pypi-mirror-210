## file to view pca / umap / tsne embeddings in 2d or 3d with tf projector and plotly

from mb import pandas as pd
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap


__all__ = ['get_emb','viz_emb']


def get_emb(df: pd.DataFrame, emb= 'embeddings', emb_type='umap', dim=2,keep_original_emb=False,file_save=None, logger=None,**kwargs):
    """
    Visualize embeddings in 2d or 3d with tf projector and plotly

    Args:
        df (pd.DataFrame): dataframe containing embeddings. File location or DataFrame object.
        emb (str): name of embedding column
        emb_type (str, optional): embedding type. Defaults to 'umap'.
        dim (int, optional): embedding dimension. Defaults to 2.
        keep_original_emb (bool, optional): keep original embedding column. Defaults to False.
        file_save (str, optional): file location to save embeddings csv. Defaults to None.
    Output:
        df (pd.DataFrame): dataframe containing embeddings. Original embedding column is dropped.
    """
    
    if df is not pd.DataFrame:
        df = pd.load_any_df(df)
        if logger:
            logger.info('Loaded dataframe from path {}'.format(str(df)))
    
    if logger:
        logger.info('Data shape {}'.format(str(df.shape)))
        logger.info('Data columns {}'.format(str(df.columns)))
        logger.info('Performing {} on {} embeddings'.format(emb_type,emb))
    
    if emb_type=='pca':
        pca = PCA(n_components=dim)
        pca_emb = pca.fit_transform(list(df[emb]))
        if logger:
            logger.info('First PCA transform result : {}'.format(str(pca_emb[0])))
        temp_res = list(pca_emb)
    
    if emb_type=='tsne':
        tsne = TSNE(n_components=dim, verbose=1, perplexity=35, n_iter=250, **kwargs)
        tsne_emb = tsne.fit_transform(list(df[emb]))
        if logger:
            logger.info('First TSNE transform result : {}'.format(str(tsne_emb[0])))
        temp_res = list(tsne_emb)
    
    if emb_type=='umap':
        umap_emb = umap.UMAP(n_neighbors=dim, min_dist=0.3, metric='correlation',**kwargs).fit_transform(list(df[emb]))
        if logger:
            logger.info('First UMAP transform result : {}'.format(str(umap_emb[0])))
        temp_res = list(umap_emb)
    
    df['emb_res'] = temp_res
    if keep_original_emb==False:
        df.drop(emb,axis=1,inplace=True)
        if logger:
            logger.info('Dropped original embedding column')
            
    if file_save:
        df.to_csv(file_save,index=False)
    else:
        df.to_csv('./emb_res.csv',index=False)
    
    return df

def viz_emb(df: pd.DataFrame, emb_column='emb_res' , view_dim=2, viz_type ='plt', file_save=None, logger=None):
    """
    Vizualize embeddings in 2d or 3d with tf projector and plotly
    
    Args:
        df (pd.DataFrame): dataframe containing embeddings. File location or DataFrame object.
        emb_column (str): name of embedding column
        view_dim (int, optional): embedding dimension: 2 or 3 dim. Defaults to 2.
        viz_type (str, optional): visualization type: 'plt' or 'tf'. Defaults to 'plt'.
        file_save (str, optional): file location to save plot. If viz_type='tf', then it wont be saved. Defaults to None.
        logger (logger, optional): logger object. Defaults to None.
    Output:
        None
    """
    
    
