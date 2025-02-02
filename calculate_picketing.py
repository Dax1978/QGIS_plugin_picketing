# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CalculatePicketing
                                 A QGIS plugin
 This plugin calculate pickets
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-01-27
        git sha              : $Format:%H$
        copyright            : (C) 2023 by GPN_GEO
        email                : nastyashevchenkomail@mail.ru
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from qgis.core import QgsVectorLayer, QgsPoint, QgsVectorDataProvider
from qgis.core import QgsFeature
from .calculate_picketing_dialog import CalculatePicketingDialog
from qgis.core import (
    QgsGeometry,
    QgsGeometryCollection,
    QgsPoint,
    QgsPointXY,
    QgsWkbTypes,
    QgsProject,
    QgsFeatureRequest,
    QgsVectorLayer,
    QgsDistanceArea,
    QgsUnitTypes,
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem
)

import os.path
import math


class CalculatePicketing:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.pickY = []
        self.pickX = []
        self.tan_rumb_list = []
        self.dist_list = []
        self.delta_y_list = []
        self.delta_x_list = []
        self.pointsY = []
        self.pointsX = []
        self.parts_list = []
        self.dir_list = []
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'CalculatePicketing_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Picketing')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('CalculatePicketing', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/calculate_picketing/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Calculate picketing'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Picketing'),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = CalculatePicketingDialog()
            # self.dlg.lineLengthButton.clicked.connect(self.lineLengthCalc)
            self.dlg.LineLengthButton.clicked.connect(self.LineLengthCalc)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def LineLengthCalc(self):
        """Основной метод: получаем координаты и рассчитываем расстояния и углы"""
        # get the current active layer
        layer = self.iface.activeLayer()
        layer.selectAll()
        # Находим координаты узловых точек линии
        for feat in layer.getFeatures():
            # Проверяем, что объект - полилиния (индекс 1 соответствует полилиниям)
            if feat.geometry().type() == 1:
                for part in feat.geometry().asMultiPolyline():
                    for pnt in part:
                        x = pnt.x()
                        y = pnt.y()
                        # Сохраняем координаты узловых точек в списки
                        self.pointsX.append(x)
                        self.pointsY.append(y)
            else:
                print("Incorrect type of geometry. Must be - polyline")

        # Находим расстояния и дирекционные углы
        for i in range(0, len(self.pointsX) - 1):
            dist = self.distance(self.pointsX[i], self.pointsY[i], self.pointsX[i + 1], self.pointsY[i + 1])
            direc = self.dir_angle(self.pointsX[i], self.pointsY[i], self.pointsX[i + 1], self.pointsY[i + 1])
            self.dist_list.append(dist)
            self.dir_list.append(direc)
            parts = math.floor(dist / 100)
            self.parts_list.append(parts)

        self.delta_coord()
        print(self.calc_pick())
        self.add_points()

    def distance(self, x1, y1, x2, y2):
        """Метод определения расстояний через ОГЗ"""
        dist = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        return dist

    def dir_angle(self, x1, y1, x2, y2):
        """Метод определения дирекционных углов в радианах через ОГЗ"""
        delta_x = x2 - x1
        delta_y = y2 - y1
        tan_rumb = delta_x / delta_y
        self.tan_rumb_list.append(tan_rumb)
        rumb = math.atan(tan_rumb)
        if delta_x > 0 and delta_y > 0:
            dir = rumb
        elif delta_x > 0 and delta_y < 0:
            dir = 2 * math.pi - rumb
        elif delta_x < 0 and delta_y < 0:
            dir = math.pi + rumb
        elif delta_x < 0 and delta_y > 0:
            dir = math.pi - rumb
        return dir

    def rest_dist(self) -> list[float]:
        """Метод для расчета остатка расстояния пикета при переходе от одной линии к другой"""
        rest = []
        rest_dist = 100 - (self.dist_list[0] - self.parts_list[0] * 100)
        rest.append(rest_dist)
        for i in range(1, len(self.pointsX) - 2):
            r = (self.dist_list[i] - rest[-1]) % 100
            rest.append(100 - r)
        return rest

    def delta_x(self, angle, length):
        delta_x = length * math.sin(angle)
        return delta_x

    def delta_y(self, angle, length):
        delta_y = length * math.cos(angle)
        return delta_y

    def delta_coord(self, length=100):
        """Рассчитывает приращение координат по прямой линии для каждого участка для 100 м"""
        self.delta_x_list = []
        self.delta_y_list = []
        for i in self.dir_list:
            delta_x = length * math.sin(i)
            delta_y = length * math.cos(i)
            self.delta_x_list.append(delta_x)
            self.delta_y_list.append(delta_y)
        return self.delta_x_list, self.delta_y_list

    # ОСНОВНАЯ ЛОГИКА

    def calc_pick(self):
        """Метод, реализующий получение координат пикетов в виде списков"""
        # sum_dist = sum(self.dist_list)
        # pickets = int(sum_dist // 100)
        self.delta_coord()
        x_0 = self.pointsX[0]
        y_0 = self.pointsY[0]
        self.pickX.append(x_0)
        self.pickY.append(y_0)
        i = 0
        while i < (len(self.pointsX) - 2):
            pk_x = x_0 + self.delta_x_list[i]
            pk_y = y_0 + self.delta_y_list[i]
            x_0 = pk_x
            y_0 = pk_y
            d = self.distance(self.pointsX[i + 1], self.pointsY[i + 1], pk_x, pk_y)
            if d > 100:
                self.pickX.append(pk_x)
                self.pickY.append(pk_y)
            else:
                r_1 = round((pk_x - self.pointsX[i + 1]) / (pk_y - self.pointsY[i + 1]), 9)
                r_2 = round((pk_x - self.pointsX[i]) / (pk_y - self.pointsY[i]), 9)
                # Условие, при котором пикеты не будут выходить за пределы дороги
                # Подумать насчет pk_x < X, так как дорога может быть в другую сторону
                if r_1 == round(self.tan_rumb_list[i+1], 9) or r_2 == round(self.tan_rumb_list[i], 9) and pk_x < self.pointsX[i+1]:
                    self.pickX.append(pk_x)
                    self.pickY.append(pk_y)
                pk_x = self.pointsX[i + 1] + self.delta_x(self.dir_list[i + 1], self.rest_dist()[i])
                pk_y = self.pointsY[i + 1] + self.delta_y(self.dir_list[i + 1], self.rest_dist()[i])
                x_0 = pk_x
                y_0 = pk_y
                self.pickX.append(pk_x)
                self.pickY.append(pk_y)
                i += 1

        last_dist = int((self.dist_list[-1] - self.rest_dist()[-1]) // 100)
        if last_dist != 0:
            for n in range(last_dist):
                pk_x = x_0 + self.delta_x_list[-1]
                pk_y = y_0 + self.delta_y_list[-1]
                x_0 = pk_x
                y_0 = pk_y
                self.pickX.append(pk_x)
                self.pickY.append(pk_y)

        return self.pickX, self.pickY

    def add_points(self):
        """Метод добавления пикетов на точечный слой в QGIS"""
        layers = QgsProject.instance().mapLayersByName('Пикеты')
        layer = QgsVectorLayer(layers[0].dataProvider().dataSourceUri(), '', 'ogr')
        caps = layer.dataProvider().capabilities()
        if caps & QgsVectorDataProvider.AddFeatures:
            feat = QgsFeature(layer.fields())
            feat.setAttributes([0, 'added programatically'])
            for i in range(len(self.pickX)):
                x = self.pickX[i]
                y = self.pickY[i]
                feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))
                res, outFeats = layer.dataProvider().addFeatures([feat])
