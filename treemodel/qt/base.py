#
# Copyright 2017 Luma Pictures
#
# Licensed under the Apache License, Version 2.0 (the "Apache License")
# with the following modification you may not use this file except in
# compliance with the Apache License and the following modification to it:
# Section 6. Trademarks. is deleted and replaced with:
#
# 6. Trademarks. This License does not grant permission to use the trade
#    names, trademarks, service marks, or product names of the Licensor
#    and its affiliates, except as required to comply with Section 4(c) of
#    the License and to reproduce the content of the NOTICE file.
#
# You may obtain a copy of the Apache License at
#
#     http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License with the above modification is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the Apache License for the specific
# language governing permissions and limitations under the Apache License.
#

from __future__ import absolute_import

from treemodel.itemtree import ItemTree, TreeItem

from typing import (Any, Dict, Generic, Iterable, Iterator, List, Optional,
                    Tuple, Union, TYPE_CHECKING)

from pxr.UsdQt._Qt import QtCore, QtGui

NULL_INDEX = QtCore.QModelIndex()


class AbstractTreeModelMixin(object):
    '''
    Mixin class that implements the necessary methods for Qt model to reflect
    the structure of an ``ItemTree`` instance.
    '''

    def __init__(self, itemTree=None, parent=None):
        '''
        Parameters
        ----------
        itemTree : Optional[ItemTree]
        parent
        '''
        super(AbstractTreeModelMixin, self).__init__(parent=parent)

        self.itemTree = None  # type: ItemTree
        self.setItemTree(itemTree or ItemTree())

    # Qt methods ---------------------------------------------------------------
    def hasChildren(self, parentIndex):
        '''
        Parameters
        ----------
        parentIndex : QtCore.QModelIndex

        Returns
        -------
        bool
        '''
        return bool(self.rowCount(parentIndex))

    def index(self, row, column, parentIndex):
        '''
        Parameters
        ----------
        row : int
        column : int
        parentIndex : QtCore.QModelIndex

        Returns
        -------
        QtCore.QModelIndex
        '''
        if parentIndex.isValid():
            parentItem = parentIndex.internalPointer()
        else:
            parentItem = self.itemTree.root
        return self.itemIndex(row, column, parentItem)

    def parent(self, modelIndex):
        '''
        Parameters
        ----------
        modelIndex : QtCore.QModelIndex

        Returns
        -------
        QtCore.QModelIndex
        '''
        if modelIndex.isValid():
            parent = self.itemTree.parent(modelIndex.internalPointer())
            if parent is not self.itemTree.root:
                return self.createIndex(self.itemTree.rowIndex(parent), 0, parent)
        return NULL_INDEX

    def rowCount(self, parentIndex):
        if parentIndex.column() > 0:
            return 0
        if parentIndex.isValid():
            parent = parentIndex.internalPointer()
        else:
            parent = self.itemTree.root
        return self.itemTree.childCount(parent=parent)

    # Custom methods -----------------------------------------------------------
    def setItemTree(self, itemTree):
        '''
        Parameters
        ----------
        itemTree : ItemTree
        '''
        assert isinstance(itemTree, ItemTree)
        self.beginResetModel()
        self.itemTree = itemTree
        self.endResetModel()

    def itemIndex(self, row, column, parentItem):
        '''
        Parameters
        ----------
        row : int
        column : int
        parentItem: TreeItem

        Returns
        -------
        QtCore.QModelIndex
        '''
        try:
            childItem = self.itemTree.childAtRow(parentItem, row)
        except (KeyError, IndexError):
            return NULL_INDEX
        else:
            return self.createIndex(row, column, childItem)

    def getItemIndex(self, item, column=0):
        return self.itemIndex(self.itemTree.rowIndex(item),
                              column,
                              self.itemTree.parent(item))


class Column(object):
    '''Qt specific column used by ItemDataModel'''
    __slots__ = ('_name', 'label', 'width')

    def __init__(self, name, label=None, width=100):
        '''
        Parameters
        ----------
        name : str
        label : Optional[str]
        width: int
        '''
        self._name = name
        if label is None:
            label = name
        self.label = label
        self.width = max(0, width)

    def __repr__(self):
        return '{0.__class__.__name__}({0._name})'.format(self)

    def __str__(self):
        return self._name

    @property
    def name(self):
        # name is read-only
        return self._name
