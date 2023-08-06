from __future__ import annotations

import functools

from river import base, utils
from river.neighbors import NearestNeighbors
from river.neighbors.base import DistanceFunc, FunctionWrapper


class KNNClassifier(base.Classifier):
    """K-Nearest Neighbors (KNN) for classification.

    This works by storing a buffer with the `window_size` most recent observations.
    A brute-force search is used to find the `n_neighbors` nearest observations
    in the buffer to make a prediction. See the NearestNeighbors parent class for more
    details.

    Parameters
    ----------
    n_neighbors
        The number of nearest neighbors to search for.
    window_size
        The maximum size of the window storing the last observed samples.
    min_distance_keep
        The minimum distance (similarity) to consider adding a point to the window.
        E.g., a value of 0.0 will add even exact duplicates. Default is 0.05 to add
        similar but not exactly the same points.
    weighted
        Weight the contribution of each neighbor by it's inverse distance.
    cleanup_every
        This determines at which rate old classes are cleaned up. Classes that
        have been seen in the past but that are not present in the current
        window are dropped. Classes are never dropped when this is set to 0.
    distance_func
        An optional distance function that should accept an a=, b=, and any
        custom set of kwargs. If not defined, the Minkowski distance is used with
        p=2 (Euclidean distance). See the example section for more details.
    softmax
        Whether or not to use softmax normalization to normalize the neighbors contributions.
        Votes are divided by the total number of votes if this is `False`.

    Notes
    -----
    Note that since the window is moving and we keep track of all classes that
    are added at some point, a class might be returned in a result (with a
    value of 0) if it is no longer in the window. You can call
    model.clean_up_classes(), or set `cleanup_every` to a non-zero value.

    Examples
    --------
    >>> from river import datasets
    >>> from river import evaluate
    >>> from river import metrics
    >>> from river import neighbors
    >>> from river import preprocessing

    >>> dataset = datasets.Phishing()

    >>> model = (
    ...     preprocessing.StandardScaler() |
    ...     neighbors.KNNClassifier(window_size=50)
    ... )

    >>> evaluate.progressive_val_score(dataset, model, metrics.Accuracy())
    Accuracy: 84.55%

    When defining a custom distance function you can rely on `functools.partial` to set default
    parameter values. For instance, let's use the Manhattan function instead of the default Euclidean distance:

    >>> import functools
    >>> from river import utils
    >>> model = (
    ...     preprocessing.StandardScaler() |
    ...     neighbors.KNNClassifier(
    ...         window_size=50,
    ...         distance_func=functools.partial(utils.math.minkowski_distance, p=1)
    ...     )
    ... )
    >>> evaluate.progressive_val_score(dataset, model, metrics.Accuracy())
    Accuracy: 86.87%

    """

    def __init__(
        self,
        n_neighbors: int = 5,
        window_size: int = 1000,
        min_distance_keep: float = 0.0,
        weighted: bool = True,
        cleanup_every: int = 0,
        distance_func: DistanceFunc | None = None,
        softmax: bool = False,
    ):
        self.n_neighbors = n_neighbors
        self.window_size = window_size
        self.min_distance_keep = min_distance_keep
        self.distance_func = (
            distance_func
            if distance_func is not None
            else functools.partial(utils.math.minkowski_distance, p=2)
        )

        self.weighted = weighted
        self.cleanup_every = cleanup_every
        self.classes: set[base.typing.ClfTarget] = set()
        self.softmax = softmax
        self._cleanup_counter = cleanup_every

        self._nn = NearestNeighbors(
            window_size=self.window_size,
            min_distance_keep=min_distance_keep,
            distance_func=FunctionWrapper(self.distance_func),
        )

    @property
    def _multiclass(self):
        return True

    @classmethod
    def _unit_test_params(cls):
        yield {"n_neighbors": 3, "window_size": 30}

    def clean_up_classes(self):
        """Clean up classes added to the window.

        Classes that are added (and removed) from the window may no longer be valid.
        This method cleans up the window and and ensures only known classes
        are added, and we do not consider "None" a class. It is called every
        `cleanup_every` step, or can be called manually.

        """
        self.classes = {x for x in self.window if x[0][1] is not None}

    def learn_one(self, x, y):
        # Only add the class y to known classes if we actually add the point!
        if self._nn.update((x, y), n_neighbors=self.n_neighbors):
            self.classes.add(y)

        # Ensure classes known to instance reflect window
        self._run_class_cleanup()
        return self

    def _run_class_cleanup(self):
        """Helper function to run class cleanup, accounting for _cleanup_counter."""
        # clean up classes every cleanup_every steps
        if self.cleanup_every:
            self._cleanup_counter -= 1
            if self._cleanup_counter == 0:
                self.clean_up_classes()
                self._cleanup_counter = self.cleanup_every

        return self

    def predict_proba_one(self, x):
        nearest = self._nn.find_nearest((x, None), n_neighbors=self.n_neighbors)

        # Default prediction for every class we know is 0.
        # If class_cleanup is false this can include classes not in window
        y_pred = {c: 0.0 for c in self.classes}

        # No nearest points? Return the default (normalized)
        # Note that normalization otherwise happens at the end
        if not nearest:
            default_pred = 1 / len(self.classes) if self.classes else 0.0
            return {c: default_pred for c in self.classes}

        # If the closest is an exact match AND has a class, return it
        if nearest[0][-1] == 0 and nearest[0][0][1] is not None:
            # Update the class in our prediction from 0 to 1, 100% certain!
            y_pred[nearest[0][0][1]] = 1.0
            return y_pred

        for neighbor in nearest:
            (x, y), distance = neighbor

            # Weighted votes by inverse distance
            if self.weighted:
                y_pred[y] += 1.0 / distance

            # Uniform votes
            else:
                y_pred[y] += 1.0

        # Normalize votes into real [0, 1] probabilities
        if self.softmax:
            return utils.math.softmax(y_pred)

        # Otherwise normalize by the total sum
        total = sum(y_pred.values())
        for y in y_pred:
            y_pred[y] /= total
        return y_pred
