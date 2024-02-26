"""
Implements the TopicModeling class, which applies standard topic modeling
"""

import os

import gensim
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import loguniform, randint
from sklearn.feature_extraction.text import TfidfVectorizer

from legislation_analysis.utils.constants import (
    MAX_NUM_TOPICS_CONGRESS,
    MIN_NUM_TOPICS_CONGRESS,
    MODELED_DATA_PATH,
    TOPIC_MODEL_TRAINING_ITERATIONS,
)
from legislation_analysis.utils.functions import load_file_to_df


class TopicModeling:
    """
    Applies standard topic modeling techniques to textual data.

    parameters:
        file_path (str): path to the file to apply topic modeling to.
        save_name (str): name of the file to save the topic modeling data to.
        column (str): column to apply topic modeling to.
        max_df (float): maximum document frequency for the tfidf vectorizer.
        min_df (int): minimum document frequency for the tfidf vectorizer.
        topic_ranges (tuple): range of topics to search for the optimal number
                              of
    """

    def __init__(
        self,
        file_path: str,
        save_name: str,
        column: str = "text_pos_tags_of_interest",
        max_df: float = 0.8,
        min_df: int = 5,
        topic_ranges: tuple = (
            MIN_NUM_TOPICS_CONGRESS,
            MAX_NUM_TOPICS_CONGRESS,
        ),
    ):
        # file loading and saving
        self.df = load_file_to_df(file_path)
        self.save_name = save_name
        self.serial_path = os.path.join(
            MODELED_DATA_PATH, self.save_name.split(".")[0] + "_corpus.mm"
        )
        self.save_path = os.path.join(MODELED_DATA_PATH, self.save_name)

        # corpus generation
        self.tfidf_vectorizer = TfidfVectorizer(
            max_df=max_df, min_df=min_df, stop_words="english"
        )
        self.corpusmm = None
        self.tfidf = None
        self.dictionary = None
        self.corpus = None

        # model building
        self.column = column
        self.lda_model = None
        self.lda_output = None
        self.coherence_scores = None
        self.topic_ranges = topic_ranges

        # model parameters
        self.optimal_alpha = (
            self.optimal_eta
        ) = self.optimal_passes = self.optimal_topics = None

        # model outputs
        self.lda_topics_df = None
        self.topics_by_text_df = None

        # visualizations
        self.heatmap = None
        self.barchart = None

    def get_corpus(self) -> None:
        """
        Generates and serializes the corpus.
        """
        # fit and transform with tfidf_vectorizer if not already done
        self.tfidf = (
            self.tfidf_vectorizer.fit_transform(self.df[self.column])
            if self.tfidf is None
            else self.tfidf
        )

        # check and reduce the column if not already done
        column_reduced = f"{self.column}_reduced"
        if column_reduced not in self.df.columns:
            self.df[column_reduced] = self.df[self.column].apply(
                lambda x: [
                    word
                    for word in (x.split() if isinstance(x, str) else x)
                    if word in self.tfidf_vectorizer.vocabulary_
                ]
            )

        # create the dictionary if not already done
        self.dictionary = (
            gensim.corpora.Dictionary(self.df[column_reduced])
            if not self.dictionary
            else self.dictionary
        )

        # create corpus if not already done and serialize if the file does not
        # exist
        self.corpus = [
            self.dictionary.doc2bow(text) for text in self.df[column_reduced]
        ]
        gensim.corpora.MmCorpus.serialize(self.serial_path, self.corpus)
        self.corpusmm = (
            gensim.corpora.MmCorpus(self.serial_path)
            if not self.corpusmm
            else self.corpusmm
        )

    def coherence(self, model: gensim.models.LdaModel) -> float:
        """
        Computes the coherence of the LDA model.

        parameters:
            model (gensim.models.LdaModel): LDA model to compute coherence for.
        """
        if f"{self.column}_reduced" not in self.df.columns:
            raise ValueError(
                """Column not Found: The column must be reduced before
                computing coherence. Use get_corpus."""
            )
        coherence_model_lda = gensim.models.CoherenceModel(
            model=model,
            texts=self.df[f"{self.column}_reduced"],
            dictionary=self.dictionary,
            coherence="c_v",
        )
        return coherence_model_lda.get_coherence()

    def random_search(
        self, iterations: int = TOPIC_MODEL_TRAINING_ITERATIONS
    ) -> tuple:
        """
        Finds the optimal parameters for the LDA model by using random search.

        parameters:
            iterations (int): Number of iterations to run.

        returns:
            (tuple) Optimal parameters for the LDA model.
        """
        best_score = float("-inf")
        best_params = None
        for _iter in range(iterations):
            # sample hyperparameters
            params = {
                "num_topics": randint(
                    self.topic_ranges[0], self.topic_ranges[1]
                ).rvs(),
                "alpha": loguniform(0.001, 1).rvs(),
                "eta": loguniform(0.001, 1).rvs(),
                "passes": randint(10, 50).rvs(),
            }

            print(
                f"""\t(Iteration {_iter+1} of {iterations})
                Trying parameters: {params}"""
            )

            # train LDA model with sampled hyperparameters
            model = gensim.models.LdaModel(
                corpus=self.corpus, id2word=self.dictionary, **params
            )

            # evaluate model
            coherence_score = self.coherence(model)

            print(f"\t\tCoherence Score: {coherence_score:.2f}")

            # update best model if current model is better
            if coherence_score > best_score:
                best_score = coherence_score
                best_params = params

        print(f"Best Score: {best_score}")
        print(f"Best Params: {best_params}")

        # save best parameters
        self.optimal_topics = best_params["num_topics"]
        self.optimal_alpha = best_params["alpha"]
        self.optimal_eta = best_params["eta"]
        self.optimal_passes = best_params["passes"]

        # build the model
        self.lda_model = gensim.models.LdaModel(
            corpus=self.corpus,
            id2word=self.dictionary,
            num_topics=self.optimal_topics,
            alpha=self.optimal_alpha,
            eta=self.optimal_eta,
            passes=self.optimal_passes,
        )

    def get_topics(self, num_words: int = 10) -> list:
        """
        Returns the topics generated by the LDA model.

        parameters:
            num_words (int): Number of words to return for each topic.

        returns:
            (list) Topics generated by the LDA model.
        """
        return self.lda_model.show_topics(
            num_topics=self.optimal_topics, num_words=num_words, formatted=False
        )

    def get_lda_topics_df(self) -> None:
        """
        Generates a dataframe of topics and their words.
        """
        topics = self.get_topics()
        df_cols = [f"topic_{i}" for i in range(1, self.optimal_topics + 1)]
        df_dict = {col: [] for col in df_cols}
        for i, col in enumerate(df_cols):
            for word, _ in topics[i][1]:
                df_dict[col].append(word)

        self.lda_topics_df = pd.DataFrame(df_dict)

    def get_text_topics_df(self) -> None:
        """
        Generates a dataframe of texts and their topic distributions
        """
        lda_df = pd.DataFrame(
            {
                "title": self.df["title"],
                "topics": [
                    self.lda_model[self.dictionary.doc2bow(red_col)]
                    for red_col in self.df[f"{self.column}_reduced"]
                ],
            }
        )

        # create a column for each topic probability
        topic_prod_dict = {
            i: [0] * len(lda_df) for i in range(self.optimal_topics)
        }

        # add probabilites
        for index, topicTuples in enumerate(lda_df["topics"]):
            for topicNum, prob in topicTuples:
                topic_prod_dict[topicNum][index] = prob

        # Update the DataFrame
        for topicNum in range(self.optimal_topics):
            lda_df["topic_{}".format(topicNum)] = topic_prod_dict[topicNum]

        self.topics_by_text_df = lda_df

    def gen_topic_model(self) -> None:
        """
        Generates the LDA model for the corpus.

        parameters:
            visualize (bool): Whether to visualize the coherence scores.
        """
        # process column
        if isinstance(
            self.df[self.column][0], (list, pd.core.series.Series, np.ndarray)
        ):
            self.df[self.column] = self.df[self.column].apply(
                lambda x: " ".join(list(x))
            )

        print("Getting corpus...")
        self.get_corpus()

        print("Finding optimal parameters...")
        self.random_search()

        print("Getting topic words...")
        self.get_lda_topics_df()

        print("Getting text topics...")
        self.get_text_topics_df()

    def get_random_indices(df_len, num_indices):
        """
        Generate a list of random indices.

        parameters:
          df_len (int): Length of the dataframe.
          num_indices (int): Number of indices to generate.

        returns:
          (list) random indices from the dataframe
        """
        if num_indices > df_len:
            return list(range(df_len))

        random_indices = np.random.choice(df_len, num_indices, replace=False)
        random_indices = list(random_indices)
        random_indices.sort()

        return random_indices

    def get_heat_map(self, title, indices=None):
        """
        Generates a heatmap of the topics.

        parameters:
            indices (list): List of indices to plot.
        """
        if indices is None:
            indices = self.get_random_indices(len(self.topics_by_text_df), 15)
        else:
            indices = indices

        ldaDFVisNames = list(self.topics_by_text_df["title"])
        ldaDFV = self.topics_by_text_df.loc[indices, :][
            ["topic_%d" % x for x in indices]
        ]
        ldaDFVis = ldaDFV.values
        K = self.optimal_topics
        topic_labels = ["Topic #{}".format(k) for k in range(K)]

        plt.pcolor(ldaDFVis, norm=None, cmap="Reds")
        plt.yticks(np.arange(ldaDFVis.shape[0]) + 0.5, ldaDFVisNames)
        plt.xticks(np.arange(ldaDFVis.shape[1]) + 0.5, topic_labels)
        plt.title(title)

        # flip the y-axis so the texts are in the order we anticipate
        plt.gca().invert_yaxis()

        # rotate the ticks on the x-axis
        plt.xticks(rotation=90)

        # add a legend
        plt.colorbar(cmap="Reds")
        plt.tight_layout()  # fixes margins
        self.heat_map = plt

    def get_bar_chart(self, title, indices=None):
        """
        Generates a bar chart of the topics.

        parameters:
            indices (list): List of indices to plot.
        """
        if indices is None:
            indices = self.get_random_indices(len(self.topics_by_text_df), 15)
        else:
            indices = indices

        N = len(indices)

        K = self.optimal_topics
        ind = np.arange(N)
        width = 0.5
        plots = []
        height_cumulative = np.zeros(N)

        ldaDFVisNames = list(self.topics_by_text_df["title"])
        ldaDFV = self.topics_by_text_df.loc[indices, :][
            ["topic_%d" % x for x in indices]
        ]
        ldaDFVis = ldaDFV.values

        for k in range(K):
            color = plt.cm.coolwarm(k / K, 1)
            if k == 0:
                p = plt.bar(ind, ldaDFVis[:, k], width, color=color)
            else:
                p = plt.bar(
                    ind,
                    ldaDFVis[:, k],
                    width,
                    bottom=height_cumulative,
                    color=color,
                )
            height_cumulative += ldaDFVis[:, k]
            plots.append(p)

        plt.ylim(
            (0, 1)
        )  # proportions sum to 1, so the height of the stacked bars is 1
        plt.ylabel("Topics")

        plt.title(title)
        plt.xticks(ind + width / 2, ldaDFVisNames, rotation="vertical")

        plt.yticks(np.arange(0, 1, 10))
        topic_labels = ["Topic #{}".format(k) for k in range(K)]
        plt.legend(
            [p[0] for p in plots],
            topic_labels,
            loc="center left",
            frameon=True,
            bbox_to_anchor=(1, 0.5),
        )

        self.bar_chart = plt

    def visualize(self):
        """
        Generates visualizations for the topic models.
        """
        self.get_heat_map()
        self.get_bar_chart()
