"""
Geometry helper
SPDX - License - Identifier: LGPL - 3.0 - or -later
Copyright © 2022 Concordia CERC group
Project Coder Guille Gutierrez guillermo.gutierrezmorote@concordia.ca
Code contributors: Pilar Monsalvete Alvarez de Uribarri pilar.monsalvete@concordia.ca
"""


class MapPoint:
  def __init__(self, x, y):
    self._x = int(x)
    self._y = int(y)

  @property
  def x(self):
    return self._x

  @property
  def y(self):
    return self._y

  def __str__(self):
    return f'({self.x}, {self.y})'

  def __len__(self):
    return 1

  def __getitem__(self, index):
    if index == 0:
      return self._x
    elif index == 1:
      return self._y
    else:
      raise IndexError('Index error')