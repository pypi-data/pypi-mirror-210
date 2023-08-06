"""
GXN•OMP and GXN•EN classes
--------------------------

Classes implementing the GXN•OMP and GXN•EN  algorithms

"""


from tqdm import tqdm
from sklearn.model_selection import KFold,StratifiedKFold
from sklearn.linear_model import OrthogonalMatchingPursuitCV
from sklearn.linear_model import ElasticNetCV
from sklearn.model_selection import GridSearchCV
import numpy as np
import pandas as pd
import networkx.algorithms.community as nx_comm
import networkx as nx
from os.path import join
import seaborn as sns
import gseapy as gp
from copy import deepcopy
import matplotlib.pyplot as plt
from gseapy.plot import gseaplot, heatmap
from GXN.data.GO.go_loader import load_go
from goatools.mapslim import mapslim
from goatools.go_enrichment import GOEnrichmentStudy
from kneed import KneeLocator
from sklearn.svm import LinearSVR
from sklearn.svm import l1_min_c
import pickle as p
import os
from networkx import quotient_graph
from networkx.algorithms.tree.branchings import Edmonds
from sklearn.metrics import r2_score
from grenadine.Preprocessing.discretization import discretize_genexp

class ContinuousTargetStratifiedKFold:
    def __init__(self, n_splits=5, nb_bins=5, random_state=33, shuffle=True):
        self.nb_bins = nb_bins
        self.n_splits = n_splits
        self.skf = StratifiedKFold(n_splits=n_splits, random_state=random_state, shuffle=shuffle)

    def split(self,X,y,groups=None):
        y_discrete = discretize_genexp(y,'efd',self.nb_bins)
        return list(self.skf.split(X, y_discrete))

    def get_n_splits(self,X=None, y=None, groups=None):
        return self.n_splits

def edge_data_function(graph, nodesA, nodesB):
    e_0 = list(graph.edges())[0]
    edge_data = list(graph[e_0[0]][e_0[1]].keys())
    new_edge_data = {d:0 for d in edge_data}
    for e in graph.edges():
        if e[0] in nodesA and e[1] in nodesB:
            for d in new_edge_data:
                new_edge_data[d] += graph[e[0]][e[1]][d]
    return new_edge_data

#np.percentile(motifs.values.flatten(),99)
def motifs_scores_to_tf_score(scores_feather_file,
                              motifs2tfs_file,
                              join_function='sum',
                              progress_bar=True):
    motifs_scores = pd.read_feather(scores_feather_file)
    motifs_scores.index = motifs_scores["motifs"]
    del motifs_scores["motifs"]
    motifs2tf = pd.read_csv(motifs2tfs_file,sep="\t",header=0)
    motif2tf_mapper = {}
    for i in tqdm(motifs2tf.index,disable=not progress_bar):
        m = motifs2tf.loc[i,"#motif_id"]
        tf = motifs2tf.loc[i,"gene_name"]
        if m not in motif2tf_mapper:
            motif2tf_mapper[m] = []
            motif2tf_mapper[m].append(tf)

    tfs_scores = {}
    for m in tqdm(motifs_scores.index,disable=not progress_bar):
        tfs = motif2tf_mapper[m]
        for tf in tfs:
            if tf not in tfs_scores:
                tfs_scores[tf] = []
            score_local = motifs_scores.loc[m]
            tfs_scores[tf].append(score_local)

    tfs_scores_joined = {}
    for tf in tqdm(tfs_scores,disable=not progress_bar):
        df = pd.DataFrame(tfs_scores[tf])
        if join_function == 'sum':
            score_local_join = df.sum()
        elif join_function == 'max':
            score_local_join = df.max()
        elif join_function == 'mean':
            score_local_join = df.mean()
        tfs_scores_joined[tf] = score_local_join
    tfs_scores_joined = pd.DataFrame(tfs_scores_joined)
    return tfs_scores_joined

def clean_txt_go_terms(txt):
    """
    Receives a GO name and returns a clean version for plots (development replaced by dev., system replaced by sys., and "\n" are used to separate words)

    Args:
        txt (str): input name

    Returns:
        string: clean name

    """
    txt = txt.lower()
    txt = "dev.".join(txt.split("development"))
    txt = "sys. ".join(txt.split("system "))
    txt = "\n".join(txt.split())
    return txt.title()

class __General_GXN__:
    """
    Class that infers a GXN from gene expression data, using a predifined predictor

    Args:
        predictor (object): A regressor model following the scikit-learn implementation
            that should have a fit and a score functions. This predictor is used to infer
            each TG expression a a function of the regulators expressions
        predictor_parameters (dict): Meta-parameters for the regressor model

    """
    def __init__(self, predictor, **predictor_parameters):
        """
        Constructor of "__General_GXN__"  class

        Args:
            predictor (object): A regressor model following the scikit-learn implementation
                that should have a fit and a score functions. This predictor is used to infer
                each TG expression a a function of the regulators expressions
            predictor_parameters (dict): Meta-parameters for the regressor model

        """
        self.predictor = predictor
        self.predictor_parameters = predictor_parameters
        self.C = None
        self.C_non_refined = None
        self.G = None
        self.communities = None
        self.GSEA = None
        self.ododag = load_go(False)
        self.ododag_slim = load_go(True)
        self.community_label = 'C'
        self.GO = None
        self.model_per_gene = None
        self.tfs_per_tg = None
        self.model_evaluations = None
        self.suitable_models_ratio = None
        self.sparsity = None
        self.modularity = None
        self.communities_descriptions = None
        self.rolling_multi_resolution = None
        self.kn = None
        self.evaluation_features = [ "mean_test_score",
                                    "mean_train_score",
                                    'std_test_score',
                                    'std_train_score',
                                    "mean_fit_time",
                                    "std_fit_time",
                                    "mean_score_time",
                                    "std_score_time"]

    def _run_fit_exception(self):
        """
        Launch an exception if the model is not fitted

        """
        raise Exception("Please use the `fit_predict` method to" +\
        "create a GXN model before using this function")

    def _run_gsea_exception(self):
        """
        Launch an exception if the model is not fitted

        """
        raise Exception("Please use the `gsea_analysis` to run a GSEA analysis"+\
        "before using this function")


    def save(self,folder):
        """
        Saves the GXN model using pickle library in a user-defined folder. If the folder does not exist, it is created

        Args:
            folder (str):  folder where the model should be saved

        """
        if not os.path.isdir(folder):
            os.mkdir(folder)
        p.dump(self.predictor, open(join(folder,"predictor.pickle"),"wb"))
        p.dump(self.predictor_parameters, open(join(folder,"predictor_parameters.pickle"),"wb"))
        p.dump(self.C, open(join(folder,"C.pickle"),"wb"))
        p.dump(self.C_non_refined, open(join(folder,"C_non_refined.pickle"),"wb"))
        p.dump(self.G, open(join(folder,"G.pickle"),"wb"))
        p.dump(self.communities, open(join(folder,"communities.pickle"),"wb"))
        p.dump(self.GSEA, open(join(folder,"GSEA.pickle"),"wb"))
        p.dump(self.community_label, open(join(folder,"community_label.pickle"),"wb"))
        p.dump(self.GO, open(join(folder,"GO.pickle"),"wb"))
        p.dump(self.model_per_gene, open(join(folder,"model_per_gene.pickle"),"wb"))
        p.dump(self.tfs_per_tg, open(join(folder,"tfs_per_tg.pickle"),"wb"))
        p.dump(self.model_evaluations, open(join(folder,"model_evaluations.pickle"),"wb"))
        p.dump(self.suitable_models_ratio, open(join(folder,"suitable_models_ratio.pickle"),"wb"))
        p.dump(self.sparsity, open(join(folder,"sparsity.pickle"),"wb"))
        p.dump(self.modularity, open(join(folder,"modularity.pickle"),"wb"))
        p.dump(self.communities_descriptions, open(join(folder,"communities_descriptions.pickle"),"wb"))
        p.dump(self.rolling_multi_resolution, open(join(folder,"rolling_multi_resolution.pickle"),"wb"))
        p.dump(self.kn, open(join(folder,"kn.pickle"),"wb"))


    def load(self,folder):
        """
        Load the GXN model from the saving folder provided by the used

        Args:
            folder (str):  folder where the model is saved

        """
        if not os.path.isdir(folder):
            raise Exception("The folder "+str(folder)+" does not exist, the model cannot be loaded")
        self.predictor = p.load(open(join(folder,"predictor.pickle"),"rb"))
        self.predictor_parameters = p.load(open(join(folder,"predictor_parameters.pickle"),"rb"))
        self.C = p.load(open(join(folder,"C.pickle"),"rb"))
        self.C_non_refined = p.load(open(join(folder,"C_non_refined.pickle"),"rb"))
        self.G = p.load(open(join(folder,"G.pickle"),"rb"))
        self.communities = p.load(open(join(folder,"communities.pickle"),"rb"))
        self.GSEA = p.load(open(join(folder,"GSEA.pickle"),"rb"))
        self.community_label = p.load(open(join(folder,"community_label.pickle"),"rb"))
        self.GO = p.load(open(join(folder,"GO.pickle"),"rb"))
        self.model_per_gene = p.load(open(join(folder,"model_per_gene.pickle"),"rb"))
        self.tfs_per_tg = p.load(open(join(folder,"tfs_per_tg.pickle"),"rb"))
        self.model_evaluations = p.load(open(join(folder,"model_evaluations.pickle"),"rb"))
        self.suitable_models_ratio = p.load(open(join(folder,"suitable_models_ratio.pickle"),"rb"))
        self.sparsity = p.load(open(join(folder,"sparsity.pickle"),"rb"))
        self.modularity = p.load(open(join(folder,"modularity.pickle"),"rb"))
        self.communities_descriptions = p.load(open(join(folder,"communities_descriptions.pickle"),"rb"))
        self.rolling_multi_resolution = p.load(open(join(folder,"rolling_multi_resolution.pickle"),"rb"))
        self.kn = p.load(open(join(folder,"kn.pickle"),"rb"))

    def feature_importance_function(self,predictor):
        """
        Compute and return feature importance of inner predictor

        Returns:
            numpy.array: importance scores for each feature

        """
        if hasattr(predictor, 'feature_importances_'):
            return predictor.feature_importances_
        elif hasattr(predictor,"coef_"):
            if len(predictor.coef_.shape) > 1:
                return np.abs(predictor.coef_).mean(axis=0)
            else:
                return np.abs(predictor.coef_.flatten())
        else:
            raise Exception("the predictor "+str(predictor)+" does not have a 'feature_importances_' for 'coef_' attribute, the feature importance cannot be computed")


    def fit_predict(self,
                    gene_expression_matrix,
                    tf_list = None,
                    tg_list = None,
                    tg_tf_constrain_matrix=None,
                    progress_bar=False,
                    R2_score_samples=True,
                    cv=KFold(n_splits=5,random_state=666,shuffle=True),
                    #ContinuousTargetStratifiedKFold(n_splits=10, nb_bins=5)
                    ):
        """
        Scores transcription factors-target gene co-expressions using a predictor.

        Args:
            gene_expression_matrix (pandas.DataFrame):  gene expression matrix where
                rows are samples (conditions) and  columns are genes.
                The value at row i and column j represents the expression of gene i
                in condition j.
            tf_list (list or numpy.array): list of transcription factors ids.
            tg_list (list or numpy.array): list of target genes ids.
            tg_tf_constrain_matrix (pandas.DataFrame): constrain matrix where
                rows are genes and  columns are regulators.
                The value at row i and column j is True if the regulator j can
                control the target gene i, and False otherwise
            progress_bar: bool, if true include progress bar
            cv: int, cross-validation generator or an iterable, default=None
            Determines the cross-validation splitting strategy.
            Possible inputs for cv are those of GridSearchCV  from sklearn

        Returns:
            pandas.DataFrame: GXN scores matrix.
            dict: Dictionnary with genes as keys and models as values
            pandas.DataFrame: Summary of TG predictors evaluations

        """
        if tg_list is None:
            tg_list = gene_expression_matrix.columns
        if tf_list is None:
            tf_list = gene_expression_matrix.columns
        tf_list_present = set(gene_expression_matrix.columns).intersection(tf_list)
        tg_list_present = list(set(gene_expression_matrix.columns).intersection(tg_list))

        if not len(tf_list_present):
            raise Exception('None of the tfs in '+str(tf_list)+\
            " is present in the gene_expression_matrix genes list"+\
            str(gene_expression_matrix.columns))
        if not len(tg_list_present):
            raise Exception('None of the tgs in '+str(tg_list)+\
            " is present in the gene_expression_matrix genes list"+\
            str(gene_expression_matrix.columns))
        tg_list_present.sort()

        # compute tf scores for each gene
        scores_tf_per_gene = []
        self.model_per_gene = {}
        self.tfs_per_tg = {}
        model_evaluations = {}
        for gene in tqdm(tg_list_present,disable=not progress_bar):
            # Exclude the current gene from the tfs list
            if tg_tf_constrain_matrix is not None and gene in tg_tf_constrain_matrix.index:
                current_constrain = tg_tf_constrain_matrix.loc[gene]
                active_tfs = current_constrain[current_constrain].index
                tfs2test = list(set(active_tfs).difference(set([gene])))
                #print(tfs2test)
            else:
                tfs2test = list(tf_list_present.difference(set([gene])))
            self.tfs_per_tg[gene] = tfs2test
            X = gene_expression_matrix[tfs2test].values
            y = gene_expression_matrix[gene].values
            #local_predictor_parameters = deepcopy(self.predictor_parameters)
            #local_predictor_parameters["cv"] = [local_predictor_parameters["cv"][0].split(X,y)]
            clf = GridSearchCV(self.predictor,
                               self.predictor_parameters,
                               n_jobs=1,
                               cv=cv,
                               verbose=0,
                               return_train_score=True)
            clf.fit(X,y)
            score = self.feature_importance_function(clf.best_estimator_)
            self.model_per_gene[gene] = clf
            scores = pd.Series(score,index=tfs2test)
            scores_tf_per_gene.append(scores)
            model_evaluations[gene] = {f:self.model_per_gene[gene].cv_results_[f][0] for f in self.evaluation_features}
            if R2_score_samples:
                model_evaluations[gene]["test_score_samples"] = self.compute_R2_score_samples(deepcopy(clf.best_estimator_),X,y,cv)
        df_results = pd.DataFrame(scores_tf_per_gene, index=tg_list_present)
        df_results = df_results.fillna(0)
        self.C = df_results
        self.C_non_refined = deepcopy(self.C)
        self.model_evaluations = pd.DataFrame(model_evaluations).T
        return(self.C, self.model_per_gene, self.model_evaluations)

    def compute_R2_score_samples(self,predictor,X,y,cv):
        """
        Trains a model on k-1 CV splits, predicts the values for the remaining
        split. Concatenates the predictions for all the validation splits and
        computes the R2 score on such concatenation of predictions, as explained
        in `stackexchange forum <https://stats.stackexchange.com/questions/34611/meanscores-vs-scoreconcatenation-in-cross-validation>`_
        and in this `article <https://www.kdd.org/exploration_files/v12-1-p49-forman-sigkdd.pdf>`_

        Args:
            predictor: the regressor for which the R2 score should be computed
            X (numpy.array): Descriptors dataset
            y (numpy.array): target variable
            cv (object): cross-validation object like scikit-learn implementation, should contail a split function

        Returns:
            float: R2 score of concatenated predictions

        """
        y_pred_full = []
        y_test_full = []
        for index_train,index_test in cv.split(X,y):
            X_train = X[index_train,:]
            X_test = X[index_test,:]
            y_train = y[index_train]
            y_test = y[index_test]
            predictor.fit(X_train,y_train)
            y_pred = predictor.predict(X_test)
            y_pred_full += list(y_pred)
            y_test_full += list(y_test)
        return r2_score(y_test_full,y_pred_full)

    def score(self,
              gene_expression_matrix,
              tg_list = None,
              progress_bar=False,):
        """
        Return the validation R2 score for each TG model

        Args:
            gene_expression_matrix (pandas.DataFrame):  gene expression matrix where
                rows are samples (conditions) and  columns are genes.
                The value at row i and column j represents the expression of gene i
                in condition j.
            tg_list (list or numpy.array): list of target genes ids.
            progress_bar: bool, if true include progress bar

        Returns:
            pandas.Series: $R^2$ validation scores for the model associated to each TG

        """
        if tg_list is None:
            tg_list = gene_expression_matrix.columns
        tg_list_present = list(set(gene_expression_matrix.columns).intersection(tg_list))
        tg_list_present = list(set(tg_list_present).intersection(list(self.tfs_per_tg.keys())))
        if self.C is not None:
            scores = {}
            for gene in tqdm(tg_list_present,disable=not progress_bar):
                # Exclude the current gene from the tfs list
                tfs2test = self.tfs_per_tg[gene]
                X = gene_expression_matrix[tfs2test].values
                y = gene_expression_matrix[gene].values
                clf = self.model_per_gene[gene].best_estimator_
                scores[gene] = clf.score(X,y)
            scores = pd.Series(scores)
            return(scores)
        else:
            self._run_fit_exception()


    def predict(self,
                gene_expression_matrix,
                tg_list = None,
                progress_bar=False,):
        """
        Predict gene expression levels of TGs, from the expression of TFs
        using the GXN model

        Args:
            gene_expression_matrix (pandas.DataFrame):  gene expression matrix
                where rows are samples (conditions) and  columns are genes.
                The value at row i and column j represents the expression of
                gene i in condition j.
            tg_list (list or numpy.array): list of target genes ids.
            progress_bar: bool, if true include progress bar

        Returns:
            pandas.DataFrame: Predicted levels of expression

        """
        if tg_list is None:
            tg_list = gene_expression_matrix.columns
        tg_list_present = list(set(gene_expression_matrix.columns).intersection(tg_list))
        tg_list_present = list(set(tg_list_present).intersection(list(self.tfs_per_tg.keys())))
        if self.C is not None:
            predictions = {}
            for gene in tqdm(tg_list_present,disable=not progress_bar):
                # Exclude the current gene from the tfs list
                tfs2test = self.tfs_per_tg[gene]
                X = gene_expression_matrix[tfs2test].values
                y = gene_expression_matrix[gene].values
                clf = self.model_per_gene[gene].best_estimator_
                predictions[gene] = pd.Series(clf.predict(X),
                                    index=gene_expression_matrix.index)
            predictions = pd.DataFrame(predictions)
            return(predictions)
        else:
            self._run_fit_exception()

    def refine_C(self,metric_threshold=0.5, metric="mean_test_score"):
        """
        Remove all TGs for which it was not possible to build a suitable regression
        model (validation score lower than a threshold) are removed from the
        coefficient matrix $C$, as well as all the TFs that have never been used
        in a regression model

        Args:
            metric_threshold (float): validation score threshold.

        """
        if self.C is not None:
            self.C = deepcopy(self.C_non_refined)
            correct_tgs = self.model_evaluations[metric]>metric_threshold
            C = self.C.loc[correct_tgs[correct_tgs].index]
            used_tfs = np.abs(C).sum()>0
            C = C.T[used_tfs].T
            self.C = C
        else:
            self._run_fit_exception()

    def refine_C_outliers_vector(self,outliers,outlier_tag="Outlier"):
        if self.C is not None:
            self.C = deepcopy(self.C_non_refined)
            C = self.C.loc[outliers[outliers!=outlier_tag].index]
            used_tfs = np.abs(C).sum()>0
            C = C.T[used_tfs].T
            self.C = C
        else:
            self._run_fit_exception()


    def compute_suitable_models_ratio(self,metric_threshold=0.5,metric="mean_test_score"):
        """
        Compute the ratio of models that have a validation score higher
        than a given threshold (and thus considered as suitable)

        Args:
            metric_threshold (float): validation score threshold.

        Returns:
            float: ratio (between 0 and 1) of suitable models

        """
        if self.C is not None:
            nb_correct_models = (self.model_evaluations[metric]>metric_threshold).sum()
            self.suitable_models_ratio = nb_correct_models/len(self.model_evaluations.index)
            return self.suitable_models_ratio
        else:
            self._run_fit_exception()

    def compute_sparsity(self):
        """
        Compute the sparsity of the GXN model (number of actual links/number
        of possible links) here self loops are not considered.

        Returns:
            float: sparsity level (between 0 and 1)

        """

        if self.C is not None:
            nb_genes = len(self.C.columns)
            nb_tfs = len(self.C.index)
            full_connections = (nb_genes-1)*nb_tfs
            current_connections = (self.C.fillna(0)!=0).sum(axis=0).sum()
            self.sparsity = current_connections/full_connections
            return self.sparsity
        else:
            self._run_fit_exception()

    def __C_to_edge_list(self):
        """
        Convert matrix C to edge list

        """
        if self.C is not None:
            A = self.C.fillna(0)
            A_unsktack = A.unstack(level=0)
            A_unsktack = A_unsktack[A_unsktack!=0]
            edge_list = A_unsktack.reset_index()
            edge_list.columns = ["TF","TG","Score"]
            edge_list["AbsScore"] = np.abs(edge_list["Score"])
            return edge_list
        else:
            self._run_fit_exception()

    def get_networkx_graph(self):
        """
        Return the GXN (stored as a matrix coefficient $C$), as a networkx
        directed graph

        Returns:
            networkx.DiGraph: the networkx graph associated to the GXN model

        """
        if self.C is not None:
            edge_list = self.__C_to_edge_list()
            self.G = nx.from_pandas_edgelist(edge_list,
                                            source='TF',
                                            target='TG',
                                            edge_attr=["Score","AbsScore"],
                                            create_using=nx.DiGraph())
            return self.G
        else:
            self._run_fit_exception()

    def get_communities(self,weights="Score",resolution=1,label="C"):
        """
        Use the networkx `greedy_modularity_communities` function to split the
        GXN in communities, communities are stored in `communities` attribute

        Args:
            weights (str): attribute to be considered as weight
            resolution (float): resolution for the `greedy_modularity_communities`
                method,  higher resolution leads to many small communities while
                lower resolution leads to few and larger communities
            label (str): prefix to label the communities

        """
        if self.C is not None:
            self.get_networkx_graph()
            self.communities = list(nx_comm.greedy_modularity_communities(self.G,
                                                                          resolution=resolution,
                                                                          weight=weights))
            self.community_label = label
        else:
            self._run_fit_exception()

    def get_ego(self,gene):
        """
        Use the networkx `ego_graph` function to return the ego graph of a
        particular TG or TF

        Args:
            gene (str): TG or TF name

        Returns:
            networkw.DiGraph: Ego graph of the desired gene

        """
        if self.G is None:
            self.get_networkx_graph()
        if gene in self.G.nodes():
            return nx.ego_graph(self.G,gene,undirected=True)
        else:
            raise Exception("Gene "+str(gene)+" is not present in the GXN")

    def compute_modularity(self,weight="Score",resolution=1):
        """
        Use the networkx `modularity` function to compute the modularity of
        the current communities split stored in `communities` attribute

        Args:
            weights (str): attribute to be considered as weight
            resolution (float): resolution for the `greedy_modularity_communities`
                method,  higher resolution produced many small communities while
                lower resolution produced few and larger communities, provide
                the same resolution that was used to create the communities

        """
        if self.communities is None:
            self.get_communities()
        self.modularity = nx_comm.modularity(self.G.to_undirected(),
                                             self.communities,
                                             resolution=resolution,
                                             weight=weight)
        return self.modularity

    def make_branching_G(self,G=None,attr="Score"):
        """
        Use the networkx `Edmonds.find_optimum` function to represent the
        GXN network as a branching, for visualization purposes

        Args:
            G (networkx.DiGraph): Network that should be turned into a branching if G is None, then the GXN network is analyzed
            attr (str): name for the edge attribute used as weight

        Returns:
            networkw.DiGraph: Branching graph of the desired network

        """
        if G is None:
            G = self.G
            if G is None:
                self.get_networkx_graph()
        edmundo = Edmonds(G)
        branching = edmundo.find_optimum(attr=attr, default=0,
                                         kind='max', style='branching',
                                         preserve_attrs=False)
        return branching

    def get_community_G(self,id_community):
        """
        Builds a subgraph associated to the target community

        Args:
            id_community (int): Number of the community that should be represented

        Returns:
            networkx.DiGraph(): Community graph

        """
        if self.communities is None:
            self.get_communities()
        community = self.communities[id_community]
        grn_inferred_community = self.G.subgraph(community).copy()
        return(grn_inferred_community)

    def plot_community(self,id_community,threshold=0.2,
                       new_figure=True,abs_threshold=True,
                       **visual_parameters):
        """
        Gets the target community and plots it calling the `plot_network` method

        Args:
            id_community (int): Number of the community that should be represented
            threshold (float): Only edges with weight higher than `threshold` are represented
            new_figure (bool): True if a new figure should be built
            abs_threshold (bool): True if the threshold is applied to the absolute value of the weight

        """
        grn_inferred_community = self.get_community_G(id_community)
        self.plot_network(grn_inferred_community,threshold,
                          new_figure=new_figure,abs_threshold=abs_threshold,
                          **visual_parameters)



    def plot_network(self,graph,threshold,new_figure=True,
                     abs_threshold=True,**visual_parameters):
        """
        Plots the network sent as parameter

        Args:
            graph (networkx.Graph): Network to be plotted
            threshold (float): Only edges with weight higher than `threshold` are represented
            new_figure (bool): True if a new figure should be built
            abs_threshold (bool): True if the threshold is applied to the absolute value of the weight

        """

        G = graph.copy()
        colnodes = []
        if abs_threshold:
            G.remove_edges_from([(n1, n2) for n1, n2, w in G.edges(data="Score") if np.abs(w) < threshold])
        else:
            G.remove_edges_from([(n1, n2) for n1, n2, w in G.edges(data="Score") if w < threshold])
        G.remove_nodes_from(list(nx.isolates(G)))
        nb_nodes = len(G.nodes)

        visual_params_default = {"figsize":(3*int(np.sqrt(nb_nodes)),
                                            3*int(np.sqrt(nb_nodes))),
                                 "prog":"dot",
                                 "edge_cmap":plt.cm.coolwarm,
                                 "node_color":"cadetBlue",
                                 "nodes_size":7,
                                 "edge_vmin":-2,
                                 "edge_vmax":2,
                                 "with_labels":True,
                                 "alpha":0.9,
                                 "font_weight":"normal",#bold
                                 "arrowsize":10,
                                 "arrowstyle":"fancy",
                                 "node_shape":"o",
                                 'width':2,
                                 "node_size_scale":200,
                                 "bbox":{'boxstyle':'round',
                                         'ec':(1.0, 1.0, 1.0),
                                         'fc':(1.0, 1.0, 1.0),
                                         'alpha':0.2},
                                 "edge_label_alpha":0.6,
                                 "edge_label_font_size":6,
                                 "cmap":None,
                                 "vmax":2,
                                 "vmin":-2
                                 }
        visual_params_default.update(visual_parameters)
        if "node_color" in visual_parameters and type(visual_parameters["node_color"]) == pd.Series:
            visual_params_default["node_color"] = [visual_params_default["node_color"][n] for n in G.nodes()]
        colnodes = []
        font_size = []
        if type(visual_params_default["node_color"]) != list:
            for node in G:
                colnodes.append(visual_params_default["node_color"])
        else:
            colnodes = visual_params_default["node_color"]
        for node in G:
            font_size.append(visual_params_default["nodes_size"])
        nodes_degrees = dict(G.degree)
        node_sizes = [(nodes_degrees[k]+1)*visual_params_default["node_size_scale"] for k in nodes_degrees]

        # Define scores for the edge colors as 1/(log(rank)+1)
        edge_colors = []
        for edge in G.edges():
            s = G[edge[0]][edge[1]]["Score"]
            edge_colors.append(s)#np.log(grn_inferred_community[edge[0]][edge[1]]["rank"]+1))


        # Define the fire size
        if new_figure:
            plt.figure(figsize=visual_params_default["figsize"])

        pos = nx.nx_agraph.graphviz_layout(G,prog=visual_params_default["prog"])
        # Plot the network
        # neato, dot, twopi, circo, fdp, sfdp.
        nx.draw_networkx(G,pos = pos, edge_cmap=visual_params_default["edge_cmap"],#RdYlBu,
                node_color=colnodes,edge_color=edge_colors,
                edge_vmin=visual_params_default["edge_vmin"],
                edge_vmax=visual_params_default["edge_vmax"],
                with_labels=visual_params_default["with_labels"],
                alpha=visual_params_default["alpha"],
                font_size=0,
                arrowsize=visual_params_default["arrowsize"],
                arrowstyle=visual_params_default["arrowstyle"],
                node_shape=visual_params_default["node_shape"],
                width=visual_params_default["width"],
                node_size=node_sizes,
                cmap = visual_params_default["cmap"],
                vmax=visual_params_default["vmax"],
                vmin = visual_params_default["vmin"],
                )
        i=0
        for node, (x, y) in pos.items():
            plt.text(x, y, node, fontsize=font_size[i], ha='center', va='center')
            i+=1

        edge_labels = {}
        for edge in G.edges():
            edge_labels[edge] = str(np.round(G[edge[0]][edge[1]]["Score"],1))

        nx.draw_networkx_edge_labels(G,pos,
                                    edge_labels=edge_labels,
                                    font_size=visual_params_default["edge_label_font_size"],
                                    alpha=visual_params_default["edge_label_alpha"],
                                    bbox=visual_params_default["bbox"])



    def gsea_analysis(self,gene_expression_matrix,tissues,**gsea_params):
        """
        Runs a GSEA analysis to study over and under expression of communities
        in the tissues present in a gene expression matrix. Results are stored
        in the `GSEA` attribute

        Args:
            gene_expression_matrix (pandas.DataFrame):  gene expression matrix where
                rows are samples (conditions) and  columns are genes.
                The value at row i and column j represents the expression of gene i
                in condition j.
            tissues (pandas.Series): index are condition names and values the corresponding tissue

        """
        if self.C is None:
            self._run_fit_exception()
        if self.communities is None:
            self.get_communities()
        gsea_base_params = {'method':"diff_of_classes",
                            'permutation_num':1000,
                            'min_size':10,
                            'max_size':1000,
                            'ascending':False,
                            'seed':666,
                            'verbose':True,
                            'outdir':None,
                            'permutation_type':'gene_set'}
        gsea_base_params.update(gsea_params)
        x = gene_expression_matrix
        gseq_res = {}
        for tissue in np.unique(tissues):
            print("Proceeding to analyze tissue:" + str(tissue))
            x_local = pd.concat((x[tissues[tissues==tissue].dropna().index],
                                 x[tissues[tissues!=tissue].dropna().index]),
                                 axis=1)
            class_vector = []
            for c in x_local.columns:
                if tissues[c]==tissue:
                    class_vector.append(tissue)
                else:
                    class_vector.append("Other")
            gene_sets = {self.community_label+str(i):list(cc) for i,cc in enumerate(self.communities)}
            gseq_res[tissue] = gp.gsea(data=x_local,
                                       gene_sets=gene_sets,
                                       cls=class_vector,
                                       **gsea_base_params)
        self.GSEA = gseq_res

    def plot_gsea_curve(self, tissue, community):
        """
        Plot the GSEA curve for a given community and a given collection of conditions (tissue)

        Args:
            tissue (str): id of tissue (collection of conditions)
            community (int): community number

        """
        if self.C is None:
            self._run_fit_exception()
        if self.GSEA is None:
            self._run_gsea_exception()
        term = self.community_label+str(community)
        gseaplot(self.GSEA[tissue].ranking,
                 term=term,
                 **self.GSEA[tissue].results[term])

    def filter_gsea(self,fdr_threshold=0.001,p_val_threshold=0.001):
        """
        Filter GSEA links according to `fdr_threshold` and `p_val_threshold`
        threshold, and only keep links that exhibit both low FDP and Pval

        Args:
            fdr_threshold (float): FDR threshold $\in ]0,1]$
            p_val_threshold (float): P-value threshold $\in ]0,1]$

        Returns:
            pd.DataFrame: GSEA scores retained
            pd.DataFrame: GSEA FDR retained
            pd.DataFrame: GSEA pvalues retained
            networkx.Graph: GSEA graph (nodes: tissues and communities, edges: links between communities and tissues when over/under expressed as a set)

        """
        if self.C is None:
            self._run_fit_exception()
        if self.GSEA is None:
            self._run_gsea_exception()
        gsea_M = {}
        gsea_fdr = {}
        gsea_pval = {}
        gsea_G = nx.Graph()
        for tissue in self.GSEA:
            gsea_M[tissue] = {}
            gsea_fdr[tissue] = {}
            gsea_pval[tissue] = {}
            m = self.GSEA[tissue].res2d
            for gs in m.index:
                if m.loc[gs]["FDR q-val"] <= fdr_threshold and m.loc[gs]["FWER p-val"] <= p_val_threshold:
                    nes = m.loc[gs]["NES"]
                    if np.isinf(nes):
                        nes = nes * np.sign(m.loc[gs]["ES"])
                    gsea_G.add_edge(tissue, m.loc[gs]["Term"], nes= nes, fdr=m.loc[gs]["FDR q-val"], pval=m.loc[gs]["FWER p-val"])
                    gsea_M[tissue][gs] = m.loc[gs]["NES"]
                    gsea_fdr[tissue][gs] = m.loc[gs]["FDR q-val"]
                    gsea_pval[tissue][gs] = m.loc[gs]["FWER p-val"]
        return gsea_M,gsea_fdr,gsea_pval,gsea_G

    def go_analysis(self,geneid2go_dict,p_fdr_bh_threshold=1e-3,**go_enrichment_params):
        """
        Run GO enrichment analysis

        Args:
            geneid2go_dict (dict): dictionary that provides the GO terms list (values) associated to each gene (keys)
            p_fdr_bh_threshold (float): FDR enrichment threshold
            go_enrichment_params (dict): dictionary providing parameters for the GOEnrichment tool

        Returns:
            pandas.DataFrame: GO enrichment analysis result, columns include "community" (community id), "GO" (GO term), "Name" (GO name), "p_uncorrected" (un-corrected p value),"p_corrected" (multiple test corrected p-value)

        """
        go_enrichment_params_base = {'propagate_counts':False,
                                     "alpha":0.05,
                                     "methods":["fdr_bh"]}
        go_enrichment_params_base.update(go_enrichment_params)
        goeaobj = GOEnrichmentStudy(geneid2go_dict.keys(), # List of protein-coding genes
                                    geneid2go_dict, # geneid/GO associations
                                    self.ododag,
                                    **go_enrichment_params_base)
        self.GO = []
        groups = {self.community_label+str(i):list(cc) for i,cc in enumerate(self.communities)}
        for g in tqdm(groups):
            genes = groups[g]
            goea_results_all = goeaobj.run_study(genes,prt=None)#
            goea_results_sig = [r for r in goea_results_all if r.p_fdr_bh < p_fdr_bh_threshold]
            enriched = [{"community":g,
                         "GO":r.GO,
                         "Name":r.name,
                         "p_uncorrected":r.p_uncorrected,
                         "p_corrected":r.p_fdr_bh} for r in goea_results_sig if r.enrichment=='e']
            self.GO += enriched
        self.GO = pd.DataFrame(self.GO)
        return self.GO

    def get_GO_graph(self, term='GO:0048856', p_corrected_threshold=1e-2,clean_txt_go_terms=clean_txt_go_terms):#0060249
        """
        Convert the GO results into a graph (nodes: GO terms and communities, edges links between communities and their associated GO terms)

        Args:
            term (str): parent GO term for which only children terms are preserved to make nodes, if term is None, all GOs are kept
            p_corrected_threshold (float): Corrected p value enrichment threshold to keep edges
            clean_txt_go_terms (function): function that takes a string as input (GO term name), clean it and return clean version.

        Returns:
            networkx.Graph: GO graph (nodes: selected GO terms and communities, edges links between communities and their associated GO terms)

        """
        if term is not None:
            results_filter = self.GO[[term in mapslim(go,self.ododag,self.ododag_slim)[1] for go in self.GO["GO"]]]
        else:
            results_filter = self.GO
        results_filter = results_filter[results_filter["p_corrected"]<p_corrected_threshold]
        results_filter["score"] = -np.log10(results_filter["p_corrected"])
        GO_graph = nx.Graph()
        for idx in results_filter.index:
            GO_graph.add_edge(results_filter.loc[idx,"community"],
                              clean_txt_go_terms(results_filter.loc[idx,"Name"]),
                              score=results_filter.loc[idx,"score"])
        return GO_graph

    def plot_go_goas_network(self,G,**visual_parameters):
        """
        (Deprecated) Plot the joint GO-GSEA network

        Args:
            G (networkx.Graph): joint GO-GSEA network
            visual_parameters (dict): graphical parameters

        """
        nb_nodes = len(G.nodes)
        communities = [self.community_label+str(c) for c in range(len(self.communities))]
        visual_params_default = {"figsize":(1.3*int(np.sqrt(nb_nodes)),
                                            1.3*int(np.sqrt(nb_nodes))),
                                 "prog":"dot",
                                 "edge_cmap":plt.cm.coolwarm,
                                 "communities_color":"navajowhite",
                                 "GOs_color":"lavender",
                                 "GSEAs_color":"lightseagreen",
                                 "communities_nodes_size":10,
                                 "GOs_nodes_size":7,
                                 "GSEAs_nodes_size":7,
                                 "edge_vmin":-3,
                                 "edge_vmax":3,
                                 "with_labels":True,
                                 "alpha":0.9,
                                 "font_weight":"normal",#bold
                                 "arrowsize":10,
                                 "arrowstyle":"fancy",
                                 "node_shape":"o",
                                 'width':2,
                                 "node_size_scale":200,
                                 "bbox":{'boxstyle':'round',
                                         'ec':(1.0, 1.0, 1.0),
                                         'fc':(1.0, 1.0, 1.0),
                                         'alpha':0.2},
                                 "edge_label_alpha":0.6,
                                 "edge_label_font_size":6,
                                 }
        visual_params_default.update(visual_parameters)
        colnodes = []
        font_size = []
        for node in G:
            if node in communities:
                colnodes.append(visual_params_default["communities_color"])
                font_size.append(visual_params_default["communities_nodes_size"])
            elif self.GSEA is not None and node in list(self.GSEA.keys()):
                colnodes.append(visual_params_default["GSEAs_color"])
                font_size.append(visual_params_default["GSEAs_nodes_size"])
            else:
                colnodes.append(visual_params_default["GOs_color"])
                font_size.append(visual_params_default["GOs_nodes_size"])

        edge_colors = []
        edge_labels = {}
        for edge in G.edges():
            s=0
            if "score" in G[edge[0]][edge[1]]:
                s = G[edge[0]][edge[1]]["score"]
                edge_labels[edge] = str(np.round(G[edge[0]][edge[1]]["score"],1))
            elif "nes" in G[edge[0]][edge[1]]:
                s = G[edge[0]][edge[1]]["nes"]
                edge_labels[edge] = str(np.round(G[edge[0]][edge[1]]["nes"],1))
            elif "weight" in G[edge[0]][edge[1]]:
                s = G[edge[0]][edge[1]]["weight"]
                edge_labels[edge] = str(np.round(G[edge[0]][edge[1]]["weight"],1))
            edge_colors.append(s)
        # Define the node size prop. to its degree
        nodes_degrees = dict(G.degree)
        node_sizes = [(nodes_degrees[k]+1)*visual_params_default["node_size_scale"] for k in nodes_degrees]

        # Plot the network
        # neato, dot, twopi, circo, fdp, sfdp.
        pos = nx.nx_agraph.graphviz_layout(G,prog=visual_params_default["prog"])

        plt.figure(figsize=visual_params_default["figsize"])
        nx.draw_networkx(G,pos = pos, edge_cmap=visual_params_default["edge_cmap"],#RdYlBu,
                node_color=colnodes,edge_color=edge_colors,
                edge_vmin=visual_params_default["edge_vmin"],
                edge_vmax=visual_params_default["edge_vmax"],
                with_labels=visual_params_default["with_labels"],
                alpha=visual_params_default["alpha"],
                font_size=0,
                arrowsize=visual_params_default["arrowsize"],
                arrowstyle=visual_params_default["arrowstyle"],
                node_shape=visual_params_default["node_shape"],
                width=visual_params_default["width"],
                node_size=node_sizes,
                )
        i=0
        for node, (x, y) in pos.items():
            plt.text(x, y, node, fontsize=font_size[i], ha='center', va='center')
            i+=1

        nx.draw_networkx_edge_labels(G,pos,
                                    edge_labels=edge_labels,
                                    font_size=visual_params_default["edge_label_font_size"],
                                    alpha=visual_params_default["edge_label_alpha"],
                                    bbox=visual_params_default["bbox"])

    def get_GSEA_GO_network(self, GSEA_graph, GO_graph):
        """
        Make a joint GSEA-GO network from a GSEA graph and a GO graph (nodes:
        tissues, GO terms, communities, edges: enriched relationships between
        communities and GO terms, and communities and tissues)

        Args:
            GSEA_graph (networkx.Graph): GSEA graph (nodes: tissues and communities)
            GO_graph (networkx.Graph): GO graph (nodes: GO terms and communities)

        Returns:
            networkx.Graph: Joint GSEA-GO network

        """
        common_nodes = set(GSEA_graph.nodes()).intersection(GO_graph.nodes())
        g = nx.Graph()
        for c in common_nodes:
            for e in GSEA_graph.edges(c):
                g.add_edge(e[0],e[1],weight=np.round(GSEA_graph.get_edge_data(*list(e))["nes"],2))
            for e in GO_graph.edges(c):
                g.add_edge(e[0],e[1],weight=np.round(GO_graph.get_edge_data(*list(e))["score"],2))
        return g


    def results_summary(self):
        """
        Return the model evaluations summary (including the number of non-zero coefficients)

        Returns:
            pandas.DataFrame: Model evaluations summary, each row represents a TG and the columns represent the descriptors charactering and assessing each model

        """
        ZERO = 1e-10
        non_zero = []
        for tg in self.model_evaluations.index:
            non_zero.append((np.abs(self.C_non_refined.loc[tg])>ZERO).sum())
        self.model_evaluations["non_zero"] = non_zero
        return self.model_evaluations

    def get_gene_communities_membership(self):
        """
        Return a pd.Series with the community membership of each gene

        Returns:
            pandas.Series: keys are gene ids, and values the community of each gene

        """
        communities_membership = {}
        for i,c in enumerate(self.communities):
            for gene in list(c):
                communities_membership[gene] = i
        for gene in self.C_non_refined.index:
            if gene not in communities_membership:
                communities_membership[gene] = -1
        return(pd.Series(communities_membership))

    def community_heatmap_average_per_tissue(self,X,tissue,community,**clustermap_params):
        """
        Plot the level of expression of the genes from a given community as a clustermap grouped by tissue origin

        Args:
            X (pandas.DataFrame): gene expression matrix (columns are genes and rows are conditions)
            tissue (pandas.Series or list): tissue of each condition
            community (int): id of the community to be represented
            clustermap_params (dict): Seaborn clustermap parameters

        """
        X_community_avg = X[self.communities[community]].groupby(tissue).mean()
        clustermap_params_ = {"cmap":"coolwarm","center":0,"annot":True}
        clustermap_params_.update(clustermap_params)
        sns.clustermap(X_community_avg.T,**clustermap_params_)

    def compute_intra_community_sse(self,X,community):
        """
        Compute the gene expressions SSE within a community

        Args:
            X (pandas.DataFrame): gene expression matrix (columns are genes and rows are conditions)
            community (int): id of the community to be represented

        Returns:
            float: intra-community SSE

        """
        c = self.communities[community]
        X_community = X[c]
        sse = (X_community.var(axis=1)*X_community.shape[1]).sum()
        return sse

    def get_community_description(self,X,community):
        """
        Compute descriptors for a given community

        Args:
            X (pandas.DataFrame): gene expression matrix (columns are genes and rows are conditions)
            community (int): id of the community to be represented

        Returns:
            dict: community descriptors (SSE and Number of nodes)

        """
        sse = self.compute_intra_community_sse(X,community)
        nb_nodes = len(self.communities[community])
        return {"SSE":sse, "Nb nodes":nb_nodes}

    def get_communities_description(self,X):
        """
        Compute descriptors for all communities

        Args:
            X (pandas.DataFrame): gene expression matrix (columns are genes and rows are conditions)

        Returns:
            pandas.DataFrame: communities descriptors (SSE and Number of nodes)

        """
        descriptions = {}
        for i,c in enumerate(self.communities):
            descriptions[i] = self.get_community_description(X,i)
        return pd.DataFrame(descriptions).T

    def inter_communities_graph(self):
        """
        Builds the inter-communities graph, where nodes are communities and edges
        represent the links between communities (the edges weights are computed
        as weighted sum of the edges between communities)

        Returns:
            networkx.DiGraph: inter-communities graph (nodes: communities, edges:
            links between communities (the edges weights are computed
            as weighted sum of the edges between communities)

        """
        gxompG_edge_data_function = lambda nodesA,nodesB: edge_data_function(self.G, nodesA, nodesB)
        self.G_communities = quotient_graph(self.G, self.communities,
                                            edge_data=gxompG_edge_data_function,
                                            relabel=True,create_using=nx.DiGraph)
        for i,c in enumerate(self.communities):
            sum_scores = 0
            sum_abs_scores = 0
            g = self.get_community_G(i)
            for e in g.edges():
                sum_scores+=g[e[0]][e[1]]["Score"]
                sum_abs_scores+=g[e[0]][e[1]]["AbsScore"]
            self.G_communities.add_edge(i,i,**{"Score":sum_scores,"AbsScore":sum_abs_scores})
        return self.G_communities

    def communities_knee_locator(self,
                                 communities_descriptions,
                                 **KneeLocator_params):
        """
        Apply the KneeLocator method to detect the knee in the communities SSE
        graphs to detect the best resolution

        Args:
            communities_descriptions (pandas.DataFrame): pandas.DataFrame: communities descriptors (SSE and Number of nodes)
            KneeLocator_params (dict): parameters for the KneeLocator method

        Returns:
            KneeLocator: KneeLocator object containing the knees detected

        """
        KneeLocator_params_default = {"curve":'convex',
                                      "direction":'decreasing',
                                      "S":5}
        KneeLocator_params_default.update(KneeLocator_params)
        sse_avg = communities_descriptions.groupby("resolution").mean()["SSE"]
        x = sse_avg.index
        y = sse_avg
        kn = KneeLocator(x, y, **KneeLocator_params_default)
        return kn


    def community_multi_resolution_analysis(self,
                                            X,
                                            resolutions=np.arange(0.5,5,0.25),
                                            rolling_average_window=5,
                                            **KneeLocator_params):
        """
        Detect communities for different values of resolution, computes communities
        descriptions (SSE, number of communities), applies a rolling average to the
        curve obtained and runs the KneeLocator method to detect the best resolution

        Args:
            X (pandas.DataFrame): gene expression matrix (columns are genes and rows are conditions)
            resolutions (list): list of resolutions to be tested
            rolling_average_window (int): rolling average window size
            KneeLocator_params (dict): parameters for the KneeLocator method

        Returns:
            pandas.DataFrame: communities_descriptions (SSE and communities sizes) for different resolutions
            pandas.DataFrame: rolling mean of the communities_descriptions
            list: list of knees detected by the KneeLocator method

        """
        side_points = rolling_average_window//2
        lside_vector = [min(resolutions)-(i+1)*0.1 for i in range(side_points)]
        rside_vector = [max(resolutions)+(i+1)*0.1 for i in range(side_points)]
        resolutions_ = lside_vector+list(resolutions)+rside_vector
        KneeLocator_params_default = {"curve":'convex',
                                      "direction":'decreasing',
                                      "S":100}
        KneeLocator_params_default.update(KneeLocator_params)
        communities_descriptions = []
        for r in tqdm(resolutions_):
            self.get_communities(weights="Score",resolution=r)
            description = self.get_communities_description(X)
            description["resolution"] = r
            communities_descriptions.append(description)
        communities_descriptions = pd.concat(communities_descriptions)
        rolling_multi_resolution = communities_descriptions.groupby("resolution").mean().rolling(rolling_average_window,center=True).mean().dropna()
        kn = self.communities_knee_locator(rolling_multi_resolution,**KneeLocator_params_default)
        communities_descriptions = communities_descriptions[communities_descriptions["resolution"].isin(resolutions)]
        self.communities_descriptions = communities_descriptions
        self.rolling_multi_resolution = rolling_multi_resolution
        self.kn = kn
        return communities_descriptions,rolling_multi_resolution,list(kn.all_knees)



    def make_tissue_report(self,tissue,gsea_G,GSEA_GO_G,folder,X,tissues,tfs):
        """
        Make a report associated to a given tissue: plots GSEA, GO and joint GSEA-GO networks
        plot the GSEA curves, and heatmaps for each community and save the tfs from the community as well as their average gene expression

        Args:
            tissue (str): tissue id
            gsea_G (networkx.Graph): GSEA graph
            GSEA_GO_G (networkx.Graph): GSEA-GO graph
            folder (str): path to the folder to save the results
            X (pandas.DataFrame): gene expression matrix (columns are genes and rows are conditions)
            tissues (pandas.Series): index are condition names and values the corresponding tissue
            tfs (list): list of TFs or regulators

        """
        tissue_folder = os.path.join(folder,tissue)
        tfs_description = {"TFs":[],"community":[]}
        if not os.path.exists(tissue_folder):
            os.mkdir(tissue_folder)
        if tissue in gsea_G.nodes():
            g = nx.ego_graph(gsea_G,tissue)
            plt.figure()
            self.plot_go_goas_network(g,prog="neato",GSEAs_nodes_size=12,communities_nodes_size=9)
            plt.savefig(os.path.join(tissue_folder,"gsea.pdf"))
            plt.clf()

            plt.figure()
            gsea_go_ego_tissue = nx.ego_graph(GSEA_GO_G,tissue,2)
            for t in list(set(tissues).difference(set([tissue]))):
                if t in gsea_go_ego_tissue.nodes:
                    gsea_go_ego_tissue.remove_node(t)
            self.plot_go_goas_network(gsea_go_ego_tissue,prog="neato",
                                        communities_color="navajowhite",
                                        GOs_color="lightsteelblue",
                                        GSEAs_color="indianred",
                                        communities_nodes_size=7,
                                        GOs_nodes_size=5,
                                        GSEAs_nodes_size=8,
                                        node_size_scale=30)
            plt.savefig(os.path.join(tissue_folder,"go_gsea.pdf"))
            plt.clf()

            for community in g[tissue]:
                if g[tissue][community]["nes"]>0:
                    c = int(community.split("|$")[1])
                    plt.figure()
                    self.community_heatmap_average_per_tissue(X,tissues,c,annot=False)
                    plt.savefig(os.path.join(tissue_folder,community+"_heatmap.pdf"))
                    plt.clf()

                    plt.figure()
                    self.plot_gsea_curve(tissue, c)
                    plt.savefig(os.path.join(tissue_folder,community+"_gsea.pdf"))
                    plt.clf()

                    tfs_com = self.communities[c].intersection(tfs)
                    tfs_description["TFs"]+=tfs_com
                    tfs_description["community"]+=[c for tf in tfs_com]

            tfs_description = pd.DataFrame(tfs_description)
            avg_profile = []
            for i,tf in enumerate(tfs_description["TFs"]):
                avg_profile.append(X[tf].groupby(tissues).mean()[tissue])
            tfs_description["avg expression"] = avg_profile
            tfs_description = tfs_description.sort_values("avg expression",ascending=False).reset_index()
            tfs_description.to_csv(os.path.join(tissue_folder,"TFs.csv"))


class GXN_OMP(__General_GXN__):
    """
    Class that infers a GXN from gene expression data, using the OMP algorithm

    Args:
        nb_features (int): Maximal number of regulators per TG, this parameter corresponds to $d_0^{max}$ in the article
        params_OMPcv_update (dict): Other parameters for the OrthogonalMatchingPursuitCV method

    """
    def __init__(self,nb_features,**params_OMPcv_update):
        """
        Constructor of the class GXN_OMP

        Args:
            nb_features (int): Maximal number of regulators per TG, this parameter corresponds to $d_0^{max}$ in the article
            params_OMPcv_update (dict): Other parameters for the OrthogonalMatchingPursuitCV method
        """
        params_OMPcv = {"fit_intercept":[False],
                       "n_jobs":[1],
                       'max_iter':[nb_features],
                       'cv':[KFold(n_splits=5,random_state=666,shuffle=True)]}
        params_OMPcv.update(params_OMPcv_update)
        __General_GXN__.__init__(self,
                                 OrthogonalMatchingPursuitCV(),
                                 **params_OMPcv)
    def feature_importance_function(self,predictor):
        """
        Compute and return feature importance of inner predictor

        Returns:
            numpy.array: importance scores for each feature

        """
        return predictor.coef_

class GXN_EN(__General_GXN__):
    """
    Class that infers a GXN from gene expression data, using the ElasticNet algorithm

    Args:
        eps (float): Parameter $\epsilon$ regulating the level of regularization of the algorithm as described in the corresponding article
        params_ENcv_update (dict): Other parameters for the ElasticNetCV method

    """
    def __init__(self,eps,**params_ENcv_update):
        """
        Constructor of the class GXN_EN

        Args:
            eps (float): Parameter $\epsilon$ regulating the level of regularization of the algorithm as described in the corresponding article
            params_ENcv_update (dict): Other parameters for the ElasticNetCV method

        """
        params_ENcv = {"fit_intercept":[False],
                       "l1_ratio":[[0.8,0.9,0.99,1]],
                       "selection":["random"],
                       "tol":[1e-2],
                       "eps":[eps],
                       "n_alphas":[int(1./eps)],
                       "n_jobs":[1],
                       'cv':[KFold(n_splits=5,random_state=666,shuffle=True)]}
        params_ENcv.update(params_ENcv_update)

        __General_GXN__.__init__(self,
                                 ElasticNetCV(),
                                 **params_ENcv)
    def feature_importance_function(self,predictor):
        """
        Compute and return feature importance of inner predictor

        Returns:
            numpy.array: importance scores for each feature

        """
        return predictor.coef_
