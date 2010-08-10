# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Julien Muchembled <jm@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Products.ERP5Type import Permissions
from Products.ERP5Type.Cache import transactional_cached
from Products.ERP5Type.Utils import sortValueList
from Products.ERP5.Document.Predicate import Predicate
from Products.ERP5.Document.BusinessProcess import BusinessProcess
from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery


@transactional_cached()
def _getEffectiveModel(self, start_date=None, stop_date=None):
  """Return the most appropriate model using effective_date, expiration_date
  and version number.
  An effective model is a model which start and stop_date are equal (or
  excluded) to the range of the given start and stop_date and with the
  higher version number (if there is more than one)

  XXX Should we moved this function to a class ? Which one ?
      What about reusing IVersionable ?
  """
  reference = self.getProperty('reference')
  if not reference:
    return self

  query_list = [Query(reference=reference),
                Query(portal_type=self.getPortalType()),
                Query(validation_state=('deleted', 'invalidated'),
                      operator='NOT')]
  if start_date is not None:
    query_list.append(ComplexQuery(Query(effective_date=None),
                                   Query(effective_date=start_date,
                                         range='ngt'),
                                   logical_operator='OR'))
  if stop_date is not None:
    query_list.append(ComplexQuery(Query(expiration_date=None),
                                   Query(expiration_date=stop_date,
                                         range='min'),
                                   logical_operator='OR'))

  # XXX What to do the catalog returns nothing (either because 'self' was just
  #     created and not yet indexed, or because it was invalidated) ?
  #     For the moment, we raise.
  model_list = self.getPortalObject().portal_catalog.unrestrictedSearchResults(
      query=ComplexQuery(logical_operator='AND', *query_list),
      sort_on=(('version', 'descending'),))
  if not model_list:
    raise KeyError('No %s found with the reference %s between %s and %s' % \
            (self.getPortalType(), reference, start_date, stop_date))
  return model_list[0].getObject()


# We do have clever caching here, since container_list does not contain objects
# with no subobject.
# After evaluation of asComposedDocument() on a SO and all its SOL,
# _findPredicateList's cache has at most 1 entry per specialise value found
# on SO/SOL.
@transactional_cached()
def _findPredicateList(container_list, portal_type=None):
  predicate_list = []
  reference_dict = {}
  for container in container_list:
    for ob in container.contentValues(portal_type=portal_type):
      if isinstance(ob, Predicate):
        # reference is used to hide lines on farther containers
        reference = ob.getProperty('reference')
        if reference:
          reference_set = reference_dict.setdefault(ob.getPortalType(), set())
          if reference in reference_set:
            continue
          reference_set.add(reference)
        predicate_list.append(ob)
  return predicate_list


class asComposedDocument(object):
  """Return a temporary object which is the composition of all effective models

  The returned value is a temporary copy of the given object. The list of all
  effective models (specialise values) is stored in a private attribute.
  Collecting predicates (from effective models) is done lazily. Predicates can
  be accessed through contentValues/objectValues.

  This class should be seen as a function, and it is named accordingly.
  It is out of CompositionMixin class to avoid excessive indentation.
  """

  def __new__(cls, orig_self, portal_type_list=None):
    self = orig_self.asContext(_portal_type_list=portal_type_list) # XXX-JPS orig_self -> original_self - please follow conventions
    base_class = self.__class__
    self.__class__ = type(base_class.__name__, (cls, base_class, BusinessProcess), {})
              # here we could inherit many "useful" classes dynamically - héhé
              # that would be a "real" abstract composition system
    self._effective_model_list = \
      orig_self._findEffectiveSpecialiseValueList(specialise_type_list=portal_type_list)
    return self

  def __init__(self, orig_self, portal_type_list=None):
    # __new__ does not call __init__ because returned object
    # is wrapped in an acquisition context.
    assert False

  def asComposedDocument(self, portal_type_list=None):
    assert False, "not useful yet"
    # If required, this must be implemented by calling 'asComposedDocument' on
    # the original object (because the parameters may differ).

  @property
  def _folder_handler(self):
    assert False

  def __getattr__(self, name):
    raise AttributeError(name)

  def objectValues(self, spec=None, meta_type=None, portal_type=None,
                   sort_on=None, sort_order=None, checked_permission=None,
                   **kw):
    assert spec is meta_type is checked_permission is None, "not useful yet"
    object_list = getattr(aq_base(self), '_predicate_list', None)
    if object_list is None:
      container_list = tuple(filter(len, self._effective_model_list))
      object_list = _findPredicateList(container_list, self._portal_type_list)
      self._predicate_list = object_list
    if portal_type is not None:
      if isinstance(portal_type, str):
        portal_type = (portal_type,)
      object_list = filter(lambda x: x.getPortalType() in portal_type,
                           object_list)
    return sortValueList(object_list, sort_on, sort_order, **kw)


class CompositionMixin:
  """
  """

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'asComposedDocument')
  asComposedDocument = transactional_cached()(asComposedDocument)

  # XXX add accessors to get properties from '_effective_model_list' ?
  #     (cf PaySheetModel)

  def _findEffectiveSpecialiseValueList(self, specialise_type_list=None):
    """Return a list of effective specialised objects that is the
    inheritance tree.
    An effective object is an object which have start_date and stop_date
    included to the range of the given parameters start_date and stop_date.

    This algorithm uses Breadth First Search.
    """
    start_date = self.getStartDate()
    stop_date = self.getStopDate()
    def getEffectiveModel(model):
      return _getEffectiveModel(model, start_date, stop_date)
    model_list = [self]
    model_set = set(model_list)
    model_index = 0
    while model_index < len(model_list):
      model = model_list[model_index]
      model_index += 1
      # we don't use getSpecialiseValueList to avoid acquisition on the parent
      for model in map(getEffectiveModel, model.getValueList('specialise',
                                      portal_type=specialise_type_list or ())):
        if model not in model_set:
          model_set.add(model)
          if 1: #model.test(self): # XXX
            model_list.append(model)
    del model_list[0]
    parent = self.getParentValue()
    if hasattr(aq_base(parent), 'asComposedDocument'):
      model_list += [model for model in parent.asComposedDocument(
                             specialise_type_list)._effective_model_list
                           if model not in model_set]
    return model_list

del asComposedDocument # to be unhidden (and renamed ?) if needed
