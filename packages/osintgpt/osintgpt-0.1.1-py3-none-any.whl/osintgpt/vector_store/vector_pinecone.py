# -*- coding: utf-8 -*-

# =================================================================
# osintgpt
#
# Author: @estebanpdl
#
# File: pinecone_client.py
# Description: Pinecone API. This file contains the Pinecone class
#   method for managing the Pinecone API connection.
# =================================================================

# import modules <Pinecone>
import os
import uuid
import time
import pinecone

# type hints
from typing import List, Optional

# import submodules
from dotenv import load_dotenv

# import exceptions
from osintgpt.exceptions.errors import MissingEnvironmentVariableError

# import base class
from .base import BaseVectorEngine

# Pinecone class
class Pinecone(BaseVectorEngine):
    '''
    Pinecone class

    This class provides methods for managing connections to a Pinecone server,
    allowing users to store, retrieve, and manipulate high-dimensional vector
    embeddings and associated documents within a Pinecone index. It offers
    functionality for creating, updating, and deleting indexes, as well as
    adding and updating vector embeddings.
    '''
    # constructor
    def __init__(self, env_file_path: str):
        '''
        Constructor
        '''
        # load environment variables
        load_dotenv(dotenv_path=env_file_path)

        # set environment variables
        self.api_key = os.getenv('PINECONE_API_KEY')
        if not self.api_key:
            raise MissingEnvironmentVariableError('PINECONE_API_KEY')
        
        self.environment = os.getenv('PINECONE_ENVIRONMENT')
        if not self.environment:
            raise MissingEnvironmentVariableError('PINECONE_ENVIRONMENT')

        pinecone.init(api_key=self.api_key, environment=self.environment)
        self.pinecone = pinecone
    
    # get client
    def get_client(self):
        '''
        Get client

        returns:
            client: pinecone client
        '''
        # return client
        return self.pinecone
    
    # create index
    def create_index(self, index_name: str, dimension: int, metric: str = 'cosine',
        metadata_config: Optional[dict] = None):
        '''
        Create index

        args:
            index_name: index name
            dimension: dimension
            metric: metric
        '''
        # create index
        self.pinecone.create_index(
            name=index_name,
            dimension=dimension,
            metric=metric
        )
    
    # describe index stats
    def describe_index_stats(self, index_name: str):
        '''
        Describe index stats

        args:
            index_name: index name
        
        returns:
            index_stats: index stats
        '''
        # describe index stats
        index = self.pinecone.Index(index_name=index_name)
        return index.describe_index_stats()

    # build ids list
    def _build_ids_list(self, vectors: List):
        '''
        Build ids list

        args:
            vectors: vectors
        
        returns:
            ids_list: ids list
        '''
        # build ids list
        ids_list = []
        while len(ids_list) < len(vectors):
            # create unique id
            unique_id = str(uuid.uuid4()).replace('-', '')

            # check if unique id is already stored
            if unique_id not in ids_list:
                ids_list.append(unique_id)
        
        return ids_list

    # add vectors
    def add_vectors(self, index_name: str, vectors: List, vector_name: str = 'main',
        metadata: Optional[List[dict]] = None, batch_size: int = 5):
        '''
        Add vectors

        IMPORTANT NOTE:
        When using Pinecone to add vectors, a 'MaxRetryError' can occasionally be
        thrown. This issue is beyond the scope of this tool, as it is a problem
        directly related to the Pinecone library itself. If you encounter this
        error, try adjusting the 'batch_size' parameter to upsert vectors in
        smaller quantities.

        args:
            index_name: index name
                type: str
            vectors: embeddings
                type: List
            metadata: metadata
                type: List[dict]
            vector_name: vector name <namespace>: default = 'main'
                type: str
            batch_size: batch size: default = 5
                batch size for upserting vectors into Pinecone index
                type: int
        '''
        #  build ids
        ids = self._build_ids_list(vectors)

        # get pinecone index
        index = self.pinecone.Index(index_name=index_name)

        '''
        Verify index status
        '''
        item = self.pinecone.describe_index(index_name)
        status = item.status['state']
        while status != 'Ready':
            item = self.pinecone.describe_index(index_name)
            status = item.status['state']

            # sleep
            time.sleep(2)
        
        # index is ready
        time.sleep(2)

        # to upsert
        to_upsert = list(zip(ids, vectors, metadata))

        # batch size
        for i in range(0, len(to_upsert), batch_size):
            # get batch
            batch = to_upsert[i:i+batch_size]

            # upsert
            index.upsert(
                vectors=batch,
                namespace=vector_name
            )
    
    def search_query(self, embedded_query: List[float], top_k: int = 10, **kwargs):
        pass
