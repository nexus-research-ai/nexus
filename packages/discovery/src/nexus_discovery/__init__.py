"""Nexus discovery, campus graph, and serendipity matching."""
from .campus_graph import LivingCampusGraph, GraphNode, GraphEdge
from .matcher import CollaboratorMatcher, MatchProfile, MatchResult
from .vector_index import InMemoryVectorIndex, cosine_similarity, VectorRecord
