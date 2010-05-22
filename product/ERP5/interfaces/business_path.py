# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
"""
Products.ERP5.interfaces.business_path
"""

from zope.interface import Interface

class IBusinessPath(Interface):
  """Business Path interface specification

  IBusinessPath provides a method to calculate the completion
  date of existing movements based on business path properties.
  It also provides methods to determine whether all related simulation
  movements related to a given explanation are completed, partially
  completed or frozen. Finally, it provides a method to invoke
  delivery builders for all movements related to a given explanation.
  """

  def getMovementCompletionDate(self, movement):
    """Returns the date of completion of the movemnet 
    based on paremeters of the business path. This complete date can be
    the start date, the stop date, the date of a given workflow transition
    on the explaining delivery, etc.

    movement -- a Simulation Movement
    """
  
  def isCompleted(explanation):
    """returns True if all related simulation movements for this explanation
    document are in a simulation state which is considered as completed
    according to the configuration of the current business path.
    Completed means that it is possible to move to next step
    of Business Process. This method does not check however whether previous
    trade states of a given business process are completed or not.
    Use instead IBusinessPathProcess.isBusinessPathCompleted for this purpose.

    explanation -- the Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree and a union 
                   business process.

    NOTE: simulation movements can be completed (ex. in 'started' state) but
    not yet frozen (ex. in 'delivered' state).
    """

  def isPartiallyCompleted(explanation):
    """returns True if some related simulation movements for this explanation
    document are in a simulation state which is considered as completed
    according to the configuration of the current business path.
    Completed means that it is possible to move to next step
    of Business Process. This method does not check however whether previous
    trade states of a given business process are completed or not.
    Use instead IBusinessPathProcess.isBusinessPathCompleted for this purpose.

    explanation -- the Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree and a union 
                   business process.
    """

  def isFrozen(explanation):
    """returns True if all related simulation movements for this explanation
    document are in a simulation state which is considered as frozen
    according to the configuration of the current business path.
    Frozen means that simulation movement cannot be modified.
    This method does not check however whether previous
    trade states of a given business process are completed or not.
    Use instead IBusinessPathProcess.isBusinessPathCompleted for this purpose.

    explanation -- the Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree and a union 
                   business process.

    NOTE: simulation movements can be frozen (ex. in 'stopped' state) but
    not yet completed (ex. in 'delivered' state).
    """

  def build(explanation):
    """Builds all related movements in the simulation using the builders
    defined on the Business Path

    explanation -- the Order, Order Line, Delivery or Delivery Line which
                   implicitely defines a simulation subtree and a union 
                   business process.
    """