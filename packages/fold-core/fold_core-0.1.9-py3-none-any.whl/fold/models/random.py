# Copyright (c) 2022 - Present Myalo UG (haftungbeschränkt) (Mark Aron Szulyovszky, Daniel Szemerey) <info@dreamfaster.ai>. All rights reserved. See LICENSE in root folder.


from random import choices
from typing import List, Optional, Union

import numpy as np
import pandas as pd

from ..base import Transformation, fit_noop
from .base import Model


class RandomClassifier(Model):
    """
    A model that predicts random classes and probabilities.

    Parameters
    ----------
    all_classes : List[int]
        All possible classes.
    probability_mean : float
        The mean of the normal distribution used to generate the probabilities.


    Examples
    --------
    ```pycon
    >>> import numpy as np
    >>> from fold.loop import train_backtest
    >>> from fold.splitters import SlidingWindowSplitter
    >>> from fold.models import RandomClassifier
    >>> from fold.utils.tests import generate_sine_wave_data
    >>> X, y  = generate_sine_wave_data()
    >>> splitter = SlidingWindowSplitter(train_window=0.5, step=0.2)
    >>> np.random.seed(42)
    >>> pipeline = RandomClassifier([0,1], [0.5, 0.5])
    >>> preds, trained_pipeline = train_backtest(pipeline, X, y, splitter)

    ```
    """

    properties = Transformation.Properties(requires_X=False)
    name = "RandomClassifier"

    def __init__(
        self, all_classes: List[int], probability_mean: Optional[List[float]] = None
    ) -> None:
        self.all_classes = all_classes
        if probability_mean is not None:
            assert len(probability_mean) == len(all_classes)
        self.probability_mean = (
            [1 / len(all_classes) for _ in range(len(all_classes))]
            if probability_mean is None
            else probability_mean
        )

    fit = fit_noop

    def predict(self, X: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        predictions = pd.Series(
            choices(population=self.all_classes, k=len(X)),
            index=X.index,
            name="predictions_RandomClassifier",
        )
        probabilities = pd.concat(
            [
                pd.Series(
                    np.random.normal(prob_mean, 0.1, len(X)).clip(0, 1),
                    index=X.index,
                    name=f"probabilities_RandomClassifier_{associated_class}",
                )
                for associated_class, prob_mean in zip(
                    self.all_classes, self.probability_mean
                )
            ],
            axis="columns",
        )
        probabilities = probabilities.div(probabilities.sum(axis=1), axis=0)

        return pd.concat([predictions, probabilities], axis="columns")

    predict_in_sample = predict

    update = fit
