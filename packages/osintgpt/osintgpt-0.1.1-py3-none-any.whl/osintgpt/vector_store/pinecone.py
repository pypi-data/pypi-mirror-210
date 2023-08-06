# -*- coding: utf-8 -*-

# ===============================================================
# osintgpt
#
#
# File: qdrant.py
# Description: Qdrant API. This file contains the Qdrant class
#   method for managing the Qdrant API connection.
# ===============================================================

# import modules <Pinecone>
import pinecone

# type hints
from typing import List, Optional

# Pinecone class
class Pinecone(object):
    '''
    Pinecone class

    This class provides methods for managing connections to a Pinecone server,
    allowing users to store, retrieve, and manipulate high-dimensional vector
    embeddings and associated documents within a Pinecone index.
    '''
    # constructor
    def __init__(self, **kwargs):
        '''
        Constructor

        args:
            **kwargs: keyword arguments for Pinecone
                api_key: API key
                environment: environment > find next to API key in console
        '''
        pinecone.init(**kwargs)
        self.pinecone = pinecone