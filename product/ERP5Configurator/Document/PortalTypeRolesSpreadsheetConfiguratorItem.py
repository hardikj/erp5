##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#                    Jerome Perrin <jerome@nexedi.com>
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

import zope.interface
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Configurator.mixin.configurator_item import ConfiguratorItemMixin


class PortalTypeRolesSpreadsheetConfiguratorItem(ConfiguratorItemMixin, XMLObject):
  """Import a portal type roles spreadsheet.
  """

  meta_type = 'ERP5 Portal Type Roles Spreadsheet Configurator Item'
  portal_type = 'Portal Type Roles Spreadsheet Configurator Item'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  zope.interface.implements(interfaces.IConfiguratorItem)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.ConfiguratorItem
                    )

  def _build(self, business_configuration):
    portal = self.getPortalObject()
    self._readSpreadSheet()
    for type_name, role_list in self._spreadsheet_cache.items():
      portal_type = portal.portal_types.getTypeInfo(type_name)
      for role in role_list:
        # rebuild a category from Group / Site & Function
        category_list = []
        for bc in ('Group', 'Site', 'Function'):
          if role.get(bc):
            category_list.append(role[bc])
        #category = '\n'.join(category_list)
        role_dict = {
                     'title': role.get('Name', 'Default'),
                     'description': role.get('Description', 'Configured by ERP5 Configurator'),
                     'role_name_list': [x.strip() for x in role.get('Role', '').split(';')],
                     'role_category_list': category_list,
                     'role_base_category_list': role.get('Base_Category', ''),
                     'role_base_category_script_id': role.get('Base_Category_Script',
                                           role.get('Script', ''))}
        portal_type.newContent(portal_type='Role Information', \
                               **role_dict)

    ## Update BT5
    bt5_obj = business_configuration.getSpecialiseValue()
    bt5_obj.edit(template_portal_type_roles_list=self._spreadsheet_cache.keys())

  def checkSpreadSheetConsistency(self):
    """Check that the spread sheet is consistent with categories spreadsheet.

     - all roles have a name ('Name' or 'Role')
     - all roles have a portal type ('Name' or 'Role')
     - all roles uses valid group & function categories

    XXX do we want to use constraint framework here ?
    """

  def _readSpreadSheet(self):
    """Read the spreadsheet and prepare internal category cache.
    """
    aq_self = aq_base(self)
    if getattr(aq_self, '_spreadsheet_cache', None) is None:
      role_dict = dict()
      info_dict = self.ConfigurationTemplate_readOOCalcFile(
                      "portal_roles_spreadsheet.ods",
                      data=self.getDefaultConfigurationSpreadsheetData())
      for sheet_name, table in info_dict.items():
        for line in table:
          if 'Portal_Type' in line:
            ptype_role_list = role_dict.setdefault(line['Portal_Type'], [])
            ptype_role_list.append(line)

      aq_self._spreadsheet_cache = role_dict

  security.declareProtected(Permissions.ModifyPortalContent,
                           'setDefaultConfigurationSpreadsheetFile')
  def setDefaultConfigurationSpreadsheetFile(self, *args, **kw):
    """Reset the spreadsheet cache."""
    self._setDefaultConfigurationSpreadsheetFile(*args, **kw)
    self._spreadsheet_cache = None
    self.reindexObject()

  security.declareProtected(Permissions.ModifyPortalContent,
                           'setConfigurationSpreadsheetFile')
  setConfigurationSpreadsheetFile = setDefaultConfigurationSpreadsheetFile

