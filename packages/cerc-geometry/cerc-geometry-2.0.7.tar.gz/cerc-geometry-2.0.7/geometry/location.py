"""
Location module
SPDX - License - Identifier: LGPL - 3.0 - or -later
Copyright © 2022 Concordia CERC group
Project Coder Guille Gutierrez guillermo.gutierrezmorote@concordia.ca
Code contributors: Pilar Monsalvete Alvarez de Uribarri pilar.monsalvete@concordia.ca
"""


class Location:
  """
  Location
  """
  def __init__(self, country, city):
    self._country = country
    self._city = city

  @property
  def city(self):
    """
    City name
    """
    return self._city

  @property
  def country(self):
    """
    Country code
    """
    return self._country
