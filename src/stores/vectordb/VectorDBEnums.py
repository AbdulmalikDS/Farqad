from enum import Enum

class VectorDBEnums(Enum):
    QDRANT = "qdrant"
    CHROMA = "chroma"

class DistanceMethodEnums(Enum):
    COSINE = "cosine"
    DOT = "dot"

    