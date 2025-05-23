# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'IDS Vendor Bill References',
    'summary': '',
    'version': '14.0.0.1.0',
    'author': 'IDS',
    'maintainer': '',
    'contributors':['Ali Mahmoud'],
    'website': '',
    'depends': ['account'],
    'data': [
        'views/account_move_view.xml',
        'security/ir.model.access.csv',
    ],
    'application': False,
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'images': ['static/description/poster_image.png'],
}
