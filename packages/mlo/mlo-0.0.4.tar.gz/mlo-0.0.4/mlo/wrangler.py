#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 11:48:58 2017

@author: Amine Laghaout

This module contains the most common high-level data wranglers.
"""

import os
import time

try:
    from . import utilities as util
except BaseException:
    import utilities as util


class Wrangler:

    def __init__(self, data_source=None, verbose=True, **kwargs):
        """
        Generic data/environment wrangler class.

        Parameters
        ----------
        data_source: str, None
            Specification of the data source (e.g., pathname to a CSV file,
            log-in credentials to a database, etc).
        """

        # This lists serves to store the dataset at the successive stages of
        # the wrangling. The first stage is typically the raw data straight
        # from the source, whereas the very last is the machine-readable
        # dataset, i.e., after operations such as one-hot encoding,
        # normalization, etc.
        self.dataset = None
        self.datasets = dict(raw=self.dataset)

        # Convert all the arguments to attributes.
        util.args_to_attributes(
            self, data_source=data_source, verbose=verbose, **kwargs)

        # Load (or generate) the raw data. Note that the wrangling per se,
        # i.e., the conversion into the machine-readable data, is not done in
        # ``__init__()``. It should be run separately after the creation of the
        # wrangler object. The reason is that the user may want to first
        # inspect the raw data before performing the transformation into
        # machine-readable data. The option of storing both the raw, human-
        # readable data and the machine-readable data (as well as any inter-
        # mediate transformation) may only be feasible if the data is evaluated
        # lazily. In such cases, the sequence of data transformations may be
        # stored in a list ``self.datasets`` where the first element is the raw
        # data and the last---equivalent to ``self.dataset``---is typically
        # the most refined, machine-readable data.
        self.acquire()

        # Validate the raw data.
        assert self.validate()

        self.shuffle()

    def acquire(self):
        """
        Data acquisition. This is where the raw, human-readable data is
        assembled.
        """

        if self.verbose:
            print('===== Acquiring the data…')

        # Continue in child class. This is where `self.dataset` is defined.
        pass

    def validate(self):
        """ Validate the data. """

        if self.verbose:
            print('===== Validating the data…')

        # Assume the validation is passed by default.
        return True

        pass  # Continue in child class.

    def shuffle(self):
        """ Shuffle the datasets. """

        if self.verbose:
            print('===== Shuffling the data…')

    def __call__(self):
        """
        Data wrangling. This transforms the raw, human-readable data to the
        (typically numerical) machine-readable data that can be ingested by
        machine learning algorithms. This can be thought of as the most basic
        (and often only) layer of feature engineering.
        """

        if self.verbose:
            print('===== Wrangling the data…')

        pass  # Continue in child class with the following:

        # Pre-split wrangling.

        # Split into train, validate, and test sets.
        # self.data.split()

        # Post-split wrangling.

        # Normalize the data based on the training set.
        # self.data.normalize()

        return dict(stats=None)

    def explore(self):
        """
        Explore the data, either visually or statistically.

        Note: This is the data exploration on the final version of the data.
        This is to avoid having to have an alternating sequence of exploration
        and wrangling.
        """

        if self.verbose:
            print('===== Exploring the data…')

        return dict(data_specs=None)

    def view(self):
        """ View one or several batches of data. """

        pass  # Continue in child class.

    def split(self, split_sizes=None):
        """
        Split the data sets into the sections specified by ``split_sizes``. As
        a result ``self.dataset`` as well as each element in ``self.datasets``
        is split accordingly.
        Parameter
        ---------
        split_sizes: dict, None
            Dictionary which specifies the sizes of the various sections to
            split thhe data into. The values in the dictionary can refer to
            numbers of examples, numbers of batches, or percentages thereof.
            (The exact choice is implementation-dependent.)
        """

        if self.verbose:
            print('===== Splitting the data…')

        pass  # Continue in child class.

    def normalize(self):
        """ Normalize the datasets. """

        if self.verbose:
            print('===== Normalizing the data…')

        pass  # Continue in child class.

    def consolidate(self):

        if self.verbose:
            print('===== Consolidating the data…')

        pass  # Continue in child class.

    def save(self, wrangler_dir='./lesson/', timestamp=True):
        """ Save the data object. """

        if self.verbose:
            print('===== Saving the wrangler object…')

        if isinstance(timestamp, bool) and timestamp is True:
            timestamp = round(time.time())
        elif timestamp is None:
            timestamp = ''

        try:
            util.rw_data(
                os.path.join(
                    wrangler_dir, f'wrangler{timestamp}.pkl'), self)
            if self.verbose:
                print('✓ Saved the wrangler.')

        # If saving the whole object fails, save the datasets only.
        except BaseException:
            util.rw_data(
                os.path.join(
                    wrangler_dir, f'datasets{timestamp}.pkl'),
                self.datasets)
            if self.verbose:
                print('✓ Saved the datasets.')
