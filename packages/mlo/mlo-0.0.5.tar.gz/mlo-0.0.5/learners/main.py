#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 11:48:58 2017

@author: Amine Laghaout

TODO code:

- [x] Remove ``default_lesson_dir`` and keep ``lesson_dir`` only.
- [ ] Add a feature engineering function in the wrangler and call the explorer twice the __call__.
- [ ] Add a consolidate() to Wrangler that does the feature selection.
- [ ] Create subfunctions for the numerical and categorical transformers.
- [x] Place everything under ``hyperparams`` and ``data_params``.
- [ ] Hyperparameter optimization
- [ ] Thorough comments
- [ ] Use JSON files for inputs (as a last step).
- [ ] Capture the stdout into a file under the lesson_dir which is timestamped and concatenated.
- [ ] Include a Makefile for Docker

TODO documentation:

- [ ] Create a table with technology and level of detail (taxonomy) as dimensions.
- [ ] Detailed UML and diagram
- [ ] Explain how the metrics are synonymous with results and they may also include results (e.g., predictions, timing metrics)
- [ ] Explain how the generic is separate from the detailed. I'll maintain the generic
- [ ] File structure
- [ ] TensorBoard
- [ ] Demos
- [ ] Go over the metrics
- [ ] Warning about Scikit-learn: Not scalable
- [ ] Provide some feedback.

TODO requirements specification:

- [ ] Data with td.data.Dataset
- [ ] tf.keras
- [ ] Exploration: Pearson correlation heatmap
- [ ] Visualization with Seaborn: https://www.tensorflow.org/tutorials/keras/regression

"""

try:
    USER = ''
    from . import learner as lea
except BaseException:
    import getpass
    USER = getpass.getuser()
    import learner as lea


def main(learner='learner',
         explore=True, select=True, train=True, test=True, serve=True):
    """
    This function is used to invoke a pre-defined learner object from the
    command line.

    Parameters
    ----------
    learner: Learner, str
        Learner to be invoked or instantiated.
    explore: bool
        Explore the data?
    select: bool
        Select the model?
    train: bool
        Train the model?
    test: bool
        Test the model?
    serve: bool
        Serve the model?

    Return
    ------
    learner: learner.Learner
        Learner object.
    """

    # Instantiate the default learner.
    learner = lea.Learner(some_argument='my_argument')
    learner(explore, select, train, test, serve)

    return learner


if __name__ == '__main__':
    learner = main()
