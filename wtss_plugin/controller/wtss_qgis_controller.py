#
# This file is part of Python QGIS Plugin for WTSS.
# Copyright (C) 2024 INPE.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.
#

"""Python QGIS Plugin for WTSS."""

import datetime
import json
from json import loads as json_loads
from pathlib import Path
from types import SimpleNamespace

import requests
from pyproj import CRS, Proj, transform
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QMessageBox
from wtss import *

from .config import Config


class Controls:
    """Sample controls to main class plugin.

    :methods:
        alert
        addItemsTreeView
        formatForQDate
        transformProjection
        getDescription
    """

    def alert(self, type_message, title, text):
        """Show alert message box with a title and info.

        :param title<string>: the message box title.
        :param text<string>: the message box info.
        """
        msg = QMessageBox()
        if type_message == 'error':
            msg.setIcon(QMessageBox.Critical)
        elif type_message == 'warning':
            msg.setIcon(QMessageBox.Warning)
        elif type_message == 'info':
            msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.Ok)
        retval = msg.exec_()

    def dialogBox(self, mainDialog, title, text):
        """Create a dialog box to get user info.

        :param mainDialog<string>: the plugin main dialog.
        :param title<string>: the dialog box title.
        :param text<string>: the dialog box info.
        """
        text, okPressed = QInputDialog.getText(mainDialog, title, text, QLineEdit.Normal, "")
        if okPressed and text != "":
            return text
        else:
            return ""

    def addItemsTreeView(self, parent, elements):
        """Create a data struct based on QGIS Tree View.

        :param parent<QStandardItemModel>: the parent node of data struct.
        :param elements<tuple>: list of items in array of tuples.
        """
        for text, children in elements:
            item = QStandardItem(text)
            parent.appendRow(item)
            if children:
                self.addItemsTreeView(item, children)

    def formatForQDate(self, date_string):
        """Return a QDate format.

        :param date_string<string>: date string with 'yyyy-mm-dd' format.
        """
        return QDate(
            int(date_string[:4]),
            int(date_string[5:-3]),
            int(date_string[8:])
        )

    def transformProjection(self, projection, latitude, longitude):
        """Transform any projection to EPSG:4326.

        :param projection<string>: string format 'EPSG:4326'.
        :param latitude<float>: the point latitude.
        :param longitude<float>: the point longitude.
        """
        lat, lon = transform(
            Proj(init=CRS.from_string(projection)),
            Proj(init=CRS.from_string("EPSG:4326")),
            latitude, longitude
        )
        return {
            "lat": lat,
            "long": lon,
            "crs": "EPSG:4326"
        }

    def getDescription(self, name = "Null", host = "Null", coverage = "Null"):
        """Return a service description format string.

        :param name<string> optional: service name.
        :param host<string> optional: service host.
        :param coverage<string> optional: activate coverage.
        """
        return (
            "Service name: " + name + "\n" +
            "Host: " + host + "\n" +
            "Active coverage: " + coverage + "\n"
        )

    def getCoverageDescription(self, server_controls = None, service = "", coverage = ""):
        """Get description from WTSS Server and format for show.

        :param server_controls<Services>: server controls to set services.
        :param service<string>: the service name save on server controls.
        :param coverage<string>: the coverage name selected.
        """
        description = server_controls.productDescription(service, coverage)
        return "{description}\n\n{spatial}".format(
            description=str(description.get("description")),
            spatial= "*Dimensions*\n\nXmin: {xmin:,.2f}\nXmax: {xmax:,.2f}\nYmin: {ymin:,.2f}\nYmax: {ymax:,.2f}".format(
                xmin=description.get("spatial_extent").get("xmin"),
                xmax=description.get("spatial_extent").get("xmax"),
                ymin=description.get("spatial_extent").get("ymin"),
                ymax=description.get("spatial_extent").get("ymax")
            )
        )

class Service:
    """Service class to map json dumps."""

    def __init__(self, index, name, host):
        """Build the Service Object.

        :param index<str>: service saved id.
        :param name<str>: service saved name.
        :param host<str>: service url.
        """
        self.id = index
        self.name = name
        self.host = host

class ServiceList:
    """Service list class to store like json file."""

    def __init__(self, services):
        """Build the Service List Object.

        :param services<Service[]>: list of Service objects.
        """
        self.services = services

class Services:
    """Class for the service storage rule.

    :Methods:
        getPath
        testServiceConnection
        resetAvailableServices
        getServices
        getServiceNames
        loadServices
        findServiceByName
        listProducts
        productDescription
        productTimeSeries
        addService
        deleteService
        editService
    """

    def __init__(self, user):
        """Build controls for WTSS Servers.

        :param user<string>: users control to storage services in a JSON file.
        """
        self.user = user
        try:
            self.services = self.getServices()
        except FileNotFoundError:
            self.resetAvailableServices()

    def getPath(self):
        """Return the location of JSON with registered services."""
        return (
            Path(Config.BASE_DIR)
                / 'json-schemas'
                    / ('services_storage_user_' + self.user + '.json')
        )

    def testServiceConnection(self, host):
        """Check if sevice is available testing connection.

        :param host<string>: the service host string
        """
        try:
            client_wtss = WTSS(host)
            client_wtss.coverages
            return True
        except:
            return False

    def resetAvailableServices(self):
        """Restart the list of services with default sevices available."""
        self.addService("Brazil Data Cube", Config.WTSS_HOST)
        if not self.getServiceNames():
            to_save = json_loads(json.dumps(ServiceList([]).__dict__))
            with open(str(self.getPath()), 'w') as outfile:
                    json.dump(to_save, outfile)

    def getServices(self):
        """Return a dictionary with registered services."""
        with self.getPath().open() as f:
            return json.loads(
                f.read(),
                object_hook = lambda d: SimpleNamespace(**d)
            )

    def getServiceNames(self):
        """Return a list of registered service names."""
        try:
            service_names = []
            for server in self.getServices().services:
                if self.testServiceConnection(server.host):
                    service_names.append(server.name)
            return service_names
        except (FileNotFoundError, FileExistsError):
            return []

    def getServicesDict(self):
        """Return the services object like dict."""
        try:
            serviceList = self.getServices()
            for i in range(len(serviceList.services)):
                serviceList.services[i] = json_loads(
                    json.dumps(serviceList.services[i].__dict__)
                )
            serviceList = json_loads(json.dumps(serviceList.__dict__))
            return serviceList
        except (FileNotFoundError, FileExistsError):
            return {}

    def loadServices(self):
        """Return the services in a data struct based on QGIS Tree View."""
        try:
            servers = []
            for server in self.getServices().services:
                if self.testServiceConnection(server.host):
                    client_wtss = WTSS(server.host)
                    coverage_tree = []
                    for coverage in client_wtss.coverages:
                        coverage_tree.append((coverage, []))
                    servers.append((server.name, coverage_tree))
                else:
                    self.deleteService(server.name)
            return [('Services', servers)]
        except (FileNotFoundError, FileExistsError):
            return [('Services', servers)]

    def findServiceByName(self, service_name):
        """Return the service in a dictionary finding by name.

        :param service_name<string>: the service registered name.
        """
        try:
            service = None
            for server in self.getServices().services:
                if str(server.name) == str(service_name):
                    service = server
            return service
        except (FileNotFoundError, FileExistsError):
            return None

    def listProducts(self, service_name):
        """Return a dictionary with the list of available products.

        :param service_name<string>: the service registered name.
        """
        host = self.findServiceByName(service_name).host
        if self.testServiceConnection(host):
            client_wtss = WTSS(host)
            return client_wtss.coverages
        else:
            return []

    def productDescription(self, service_name, product):
        """Return a dictionary with product description.

        :param service_name<string>: the service registered name.
        :param product<string>: the product name.
        """
        host = self.findServiceByName(service_name).host
        if self.testServiceConnection(host):
            client_wtss = WTSS(host)
            return client_wtss[product]
        else:
            return {}

    def productTimeSeries(self, service_name, product, bands, lon, lat, start_date, end_date):
        """Return a dictionary with product time series data.

        :param service_name<string>: the service registered name.
        :param product<string>: the product name.
        :param bands<tuple>: the selected bands available on product.
        :param lon<float>: the point longitude.
        :param lat<float>: the point latitude.
        :param start_date<string>: start date string with 'yyyy-mm-dd' format.
        :param end_date<string>: end date string with 'yyyy-mm-dd' format.
        """
        host = self.findServiceByName(service_name).host
        if self.testServiceConnection(host):
            try:
                client_wtss = WTSS(host)
                time_series = client_wtss[product].ts(
                    attributes=bands,
                    longitude=lon,
                    latitude=lat,
                    start_date=start_date,
                    end_date=end_date
                )
                return time_series
            except:
                return None
        else:
            response = requests.get(
                ("{}/wtss/time_series").format(
                    self.findServiceByName(service_name).host
                ),
                {
                    "coverage": product,
                    "attributes": ",".join(list(bands)),
                    "longitude": lon,
                    "latitude": lat,
                    "start_date": start_date,
                    "end_date": end_date
                },
                timeout=100
            )
            if response.status_code == 200:
                response = response.json()
                tl = response["result"]["timeline"]
                tl = [datetime.strptime(t, "%Y-%m-%d").date() for t in tl]
                response["result"]["timeline"] = tl
                return response
            else:
                return None

    def addService(self, name, host):
        """Register an active service.

        :param name<string>: the service name to save.
        :param host<string>: the URL service to save.
        """
        try:
            server_to_save = self.findServiceByName(name)
            if self.testServiceConnection(host) and server_to_save == None:
                try:
                    to_save = self.getServices()
                    index = to_save.services[len(to_save.services) - 1].id + 1
                except (IndexError, FileNotFoundError, FileExistsError):
                    to_save = ServiceList([])
                    index = 0
                server_to_save = Service(index, str(name), str(host))
                to_save.services.append(server_to_save)
                for i in range(len(to_save.services)):
                    to_save.services[i] = json_loads(
                        json.dumps(to_save.services[i].__dict__)
                    )
                to_save = json_loads(json.dumps(to_save.__dict__))
                with open(str(self.getPath()), 'w') as outfile:
                    json.dump(to_save, outfile)
            return server_to_save
        except (FileNotFoundError, FileExistsError):
            return None

    def deleteService(self, server_name):
        """Delete a service finding by name.

        :param server_name<string>: the service name to delete.
        """
        try:
            server_to_delete = self.findServiceByName(server_name)
            if server_to_delete != None:
                to_delete = self.getServices()
                to_delete.services.pop(
                    to_delete.services.index(server_to_delete)
                )
                for i in range(len(to_delete.services)):
                    to_delete.services[i] = json_loads(json.dumps(to_delete.services[i].__dict__))
                to_delete = json_loads(json.dumps(to_delete.__dict__))
                with open(str(self.getPath()), 'w') as outfile:
                    json.dump(to_delete, outfile)
            return server_to_delete
        except (FileNotFoundError, FileExistsError):
            return None

    def editService(self, server_name, server_host):
        """Edit the service data finding by name.

        :param server_name<string>: the service name to find.
        :param server_host<string>: the URL service to edit.
        """
        server_to_edit = self.findServiceByName(server_name)
        if server_to_edit != None:
            self.deleteService(server_name)
        return self.addService(
            server_name,
            server_host
        )
