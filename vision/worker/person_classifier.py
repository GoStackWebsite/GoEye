"""Classifies a tracked person as staff vs customer."""
import numpy as np

from shared.schemas import PersonRole


# Decides whether a tracked person is staff or a customer
class PersonClassifier:
    def classify(self, crop: np.ndarray) -> PersonRole:
        # TODO: implement (uniform color, zone behavior, a trained model, ...)
        return PersonRole.UNKNOWN
