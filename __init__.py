# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CalculatePicketing
                                 A QGIS plugin
 This plugin calculate pickets
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2023-01-27
        copyright            : (C) 2023 by GPN_GEO
        email                : nastyashevchenkomail@mail.ru
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load CalculatePicketing class from file CalculatePicketing.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .calculate_picketing import CalculatePicketing
    return CalculatePicketing(iface)
