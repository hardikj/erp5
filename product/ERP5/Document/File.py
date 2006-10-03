##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo

from Products.CMFCore.WorkflowCore import WorkflowMethod
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Base import Base

from Products.CMFDefault.File import File as CMFFile

from zLOG import LOG

class File(XMLObject, CMFFile):
    """
        A File can contain text that can be formatted using
        *Structured Text* or *HTML*. Text can be automatically translated
        through the use of 'message catalogs'.

        File can only contain role information.

        File inherits from XMLObject and can
        be synchronized accross multiple sites.
    """

    meta_type = 'ERP5 File'
    portal_type = 'File'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Default global values
    content_type = '' # Required for WebDAV support (default value)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Data
                      )

    # Declarative interfaces
    #__implements__ = ( , )

    ### Special edit method
    security.declarePrivate( '_edit' )
    def _edit(self, **kw):
      """\
        This is used to edit files
      """
      if kw.has_key('file'):
        file = kw.get('file')
        precondition = kw.get('precondition')
        if self._isNotEmpty(file):
          CMFFile._edit(self, precondition=precondition, file=file)
        del kw['file']
      Base._edit(self, **kw)

    security.declareProtected( Permissions.ModifyPortalContent, 'edit' )
    edit = WorkflowMethod( _edit )

    # Copy support needs to be implemented by ExtFile
    ################################
    # Special management methods   #
    ################################

    def manage_afterClone(self, item):
      Base.manage_afterClone(self, item)
      CMFFile.manage_afterClone(self, item)

    def manage_afterAdd(self, item, container):
      Base.manage_afterAdd(self, item, container)
      CMFFile.manage_afterAdd(self, item, container)

    def manage_beforeDelete(self, item, container):
      CMFFile.manage_beforeDelete(self, item, container)

    # DAV Support
    index_html = CMFFile.index_html
    PUT = CMFFile.PUT
    security.declareProtected('FTP access', 'manage_FTPget', 'manage_FTPstat', 'manage_FTPlist')
    manage_FTPget = CMFFile.manage_FTPget
    manage_FTPlist = CMFFile.manage_FTPlist
    manage_FTPstat = CMFFile.manage_FTPstat

