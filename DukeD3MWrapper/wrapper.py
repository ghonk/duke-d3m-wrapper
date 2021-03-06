import os.path
import numpy as np
import pandas
import pickle
import requests
import ast
import typing
from json import JSONDecoder
from typing import List

from Duke.agg_functions import *
from Duke.dataset_descriptor import DatasetDescriptor
from Duke.utils import mean_of_rows

from d3m.primitive_interfaces.base import PrimitiveBase, CallResult

from d3m import container, utils
from d3m.metadata import hyperparams, base as metadata_base, params

__author__ = 'Distil'
__version__ = '1.1.1'

Inputs = container.pandas.DataFrame
Outputs = container.pandas.DataFrame

class Params(params.Params):
    pass


class Hyperparams(hyperparams.Hyperparams):
    pass

class duke(PrimitiveBase[Inputs, Outputs, Params, Hyperparams]):
    metadata = metadata_base.PrimitiveMetadata({
        # Simply an UUID generated once and fixed forever. Generated using "uuid.uuid4()".
        'id': "46612a42-6120-3559-9db9-3aa9a76eb94f",
        'version': __version__,
        'name': "duke",
        # Keywords do not have a controlled vocabulary. Authors can put here whatever they find suitable.
        'keywords': ['Dataset Descriptor'],
        'source': {
            'name': __author__,
            'uris': [
                # Unstructured URIs.
                "https://github.com/NewKnowledge/duke-d3m-wrapper",
            ],
        },
        # A list of dependencies in order. These can be Python packages, system packages, or Docker images.
        # Of course Python packages can also have their own dependencies, but sometimes it is necessary to
        # install a Python package first to be even able to run setup.py of another package. Or you have
        # a dependency which is not on PyPi.
         'installation': [{
            'type': metadata_base.PrimitiveInstallationType.PIP,
            'package_uri': 'git+https://github.com/NewKnowledge/duke-d3m-wrapper.git@{git_commit}#egg=DukeD3MWrapper'.format(
                git_commit=utils.current_git_commit(os.path.dirname(__file__)),
            ),
         },
            {
            "type": "FILE",
            "key": "en.model",
            "file_uri": "http://public.datadrivendiscovery.org/en_1000_no_stem/en.model",
            "file_digest":"e974c8783b8ce9aa3e598c555a8ffa9cb5bdfe970955fed00702850b855e3257"
        },
        {
            "type": "FILE",
            "key": "en.model.syn0.npy",
            "file_uri": "http://public.datadrivendiscovery.org/en_1000_no_stem/en.model.syn0.npy",
            "file_digest":"1b30f64c99a90c16a133cf06eb4349d012de83ae915e2467b710b7b6417a9d56"
        },
        {
            "type": "FILE",
            "key": "en.model.syn1.npy",
            "file_uri": "http://public.datadrivendiscovery.org/en_1000_no_stem/en.model.syn1.npy",
            "file_digest":"aa88b503ca1472d6efd7babe42b452e21178a74df80e01a7eb253c5eff96cd50"
        },
        ],
        # The same path the primitive is registered with entry points in setup.py.
        'python_path': 'd3m.primitives.distil.duke',
        # Choose these from a controlled vocabulary in the schema. If anything is missing which would
        # best describe the primitive, make a merge request.
        'algorithm_types': [
            metadata_base.PrimitiveAlgorithmType.RECURRENT_NEURAL_NETWORK,
        ],
        'primitive_family': metadata_base.PrimitiveFamily.DATA_CLEANING,
    })
    
    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0, volumes: typing.Dict[str,str]=None)-> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed, volumes=volumes)
                
        self._decoder = JSONDecoder()
        self._params = {}
        self._volumes = volumes

    def fit(self) -> None:
        pass
    
    def get_params(self) -> Params:
        return self._params

    def set_params(self, *, params: Params) -> None:
        self.params = params

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        pass
        
    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> CallResult[Outputs]:
        """
        Produce a summary for the tabular dataset input
        
        Parameters
        ----------
        inputs : Input pandas frame
        Returns
        -------
        Outputs
            The output is a string summary
        """
        
        """ Accept a pandas data frame, returns a string summary
        frame: a pandas data frame containing the data to be processed
        -> a string summary
        """
        
        frame = inputs

        try:
            tree_path='../ontologies/class-tree_dbpedia_2016-10.json'
            embedding_path = self._volumes['en.model']
            row_agg_func=mean_of_rows
            tree_agg_func=parent_children_funcs(np.mean, max)
            source_agg_func=mean_of_rows
            max_num_samples = 1e6
            verbose=True

            duke = DatasetDescriptor(
                dataset=frame,
                tree=tree_path,
                embedding=embedding_path,
                row_agg_func=row_agg_func,
                tree_agg_func=tree_agg_func,
                source_agg_func=source_agg_func,
                max_num_samples=max_num_samples,
                verbose=verbose,
                )

            print('initialized duke dataset descriptor \n')

            N = 5
            out_tuple = duke.get_top_n_words(N)
            out_frame = pd.DataFrame.from_records(list([out_tuple[0],out_tuple[1]]),columns=['subject tags','confidences'])

            return out_frame

        except:
            return "Failed summarizing data frame"


if __name__ == '__main__':
    client = duke(hyperparams={})
    # frame = pandas.read_csv("https://query.data.world/s/10k6mmjmeeu0xlw5vt6ajry05",dtype='str')
    frame = pandas.read_csv("https://s3.amazonaws.com/d3m-data/merged_o_data/o_4550_merged.csv",dtype='str')
    result = client.produce(inputs = frame)
    print(result)
