# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox,
    QDoubleSpinBox, QFormLayout, QFrame, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QMainWindow, QMenuBar, QProgressBar, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QSplitter,
    QStatusBar, QTabWidget, QTableView, QVBoxLayout,
    QWidget)

from pyqtgraph import PlotWidget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1600, 900)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.tabWidget_all = QTabWidget(self.centralwidget)
        self.tabWidget_all.setObjectName(u"tabWidget_all")
        self.tab_settings = QWidget()
        self.tab_settings.setObjectName(u"tab_settings")
        self.verticalLayout_33 = QVBoxLayout(self.tab_settings)
        self.verticalLayout_33.setObjectName(u"verticalLayout_33")
        self.verticalLayout_32 = QVBoxLayout()
        self.verticalLayout_32.setObjectName(u"verticalLayout_32")
        self.frame_8 = QFrame(self.tab_settings)
        self.frame_8.setObjectName(u"frame_8")
        self.frame_8.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_8.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_23 = QVBoxLayout(self.frame_8)
        self.verticalLayout_23.setObjectName(u"verticalLayout_23")
        self.horizontalLayout_17 = QHBoxLayout()
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.horizontalSpacer_10 = QSpacerItem(458, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_17.addItem(self.horizontalSpacer_10)

        self.label_device = QLabel(self.frame_8)
        self.label_device.setObjectName(u"label_device")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_device.sizePolicy().hasHeightForWidth())
        self.label_device.setSizePolicy(sizePolicy)
        self.label_device.setMinimumSize(QSize(51, 0))
        self.label_device.setMaximumSize(QSize(51, 16777215))

        self.horizontalLayout_17.addWidget(self.label_device)

        self.comboBox_devices = QComboBox(self.frame_8)
        self.comboBox_devices.setObjectName(u"comboBox_devices")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.comboBox_devices.sizePolicy().hasHeightForWidth())
        self.comboBox_devices.setSizePolicy(sizePolicy1)
        self.comboBox_devices.setMinimumSize(QSize(200, 0))

        self.horizontalLayout_17.addWidget(self.comboBox_devices)

        self.pushButton_refresh_device = QPushButton(self.frame_8)
        self.pushButton_refresh_device.setObjectName(u"pushButton_refresh_device")

        self.horizontalLayout_17.addWidget(self.pushButton_refresh_device)

        self.horizontalSpacer_11 = QSpacerItem(458, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_17.addItem(self.horizontalSpacer_11)


        self.verticalLayout_23.addLayout(self.horizontalLayout_17)

        self.horizontalLayout_21 = QHBoxLayout()
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.horizontalSpacer_12 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_21.addItem(self.horizontalSpacer_12)

        self.pushButton_defaults_device = QPushButton(self.frame_8)
        self.pushButton_defaults_device.setObjectName(u"pushButton_defaults_device")
        self.pushButton_defaults_device.setMinimumSize(QSize(220, 0))

        self.horizontalLayout_21.addWidget(self.pushButton_defaults_device)

        self.horizontalSpacer_13 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_21.addItem(self.horizontalSpacer_13)


        self.verticalLayout_23.addLayout(self.horizontalLayout_21)


        self.verticalLayout_32.addWidget(self.frame_8)

        self.frame_9 = QFrame(self.tab_settings)
        self.frame_9.setObjectName(u"frame_9")
        self.frame_9.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_9.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_31 = QVBoxLayout(self.frame_9)
        self.verticalLayout_31.setObjectName(u"verticalLayout_31")
        self.horizontalLayout_23 = QHBoxLayout()
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.verticalLayout_29 = QVBoxLayout()
        self.verticalLayout_29.setObjectName(u"verticalLayout_29")
        self.groupBox_corrections_calibrations = QGroupBox(self.frame_9)
        self.groupBox_corrections_calibrations.setObjectName(u"groupBox_corrections_calibrations")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.groupBox_corrections_calibrations.sizePolicy().hasHeightForWidth())
        self.groupBox_corrections_calibrations.setSizePolicy(sizePolicy2)
        self.groupBox_corrections_calibrations.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.verticalLayout_21 = QVBoxLayout(self.groupBox_corrections_calibrations)
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.checkBox_electric_dark = QCheckBox(self.groupBox_corrections_calibrations)
        self.checkBox_electric_dark.setObjectName(u"checkBox_electric_dark")
        self.checkBox_electric_dark.setMinimumSize(QSize(151, 0))

        self.verticalLayout_21.addWidget(self.checkBox_electric_dark)

        self.checkBox_optical_dark = QCheckBox(self.groupBox_corrections_calibrations)
        self.checkBox_optical_dark.setObjectName(u"checkBox_optical_dark")
        self.checkBox_optical_dark.setMinimumSize(QSize(151, 0))

        self.verticalLayout_21.addWidget(self.checkBox_optical_dark)

        self.checkBox_stray_light_correction = QCheckBox(self.groupBox_corrections_calibrations)
        self.checkBox_stray_light_correction.setObjectName(u"checkBox_stray_light_correction")
        self.checkBox_stray_light_correction.setMinimumSize(QSize(151, 0))

        self.verticalLayout_21.addWidget(self.checkBox_stray_light_correction)

        self.checkBox_non_linearity = QCheckBox(self.groupBox_corrections_calibrations)
        self.checkBox_non_linearity.setObjectName(u"checkBox_non_linearity")
        self.checkBox_non_linearity.setMinimumSize(QSize(151, 0))

        self.verticalLayout_21.addWidget(self.checkBox_non_linearity)

        self.checkBox_irradiance = QCheckBox(self.groupBox_corrections_calibrations)
        self.checkBox_irradiance.setObjectName(u"checkBox_irradiance")
        self.checkBox_irradiance.setMinimumSize(QSize(151, 0))

        self.verticalLayout_21.addWidget(self.checkBox_irradiance)

        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.checkBox_pixel_binning = QCheckBox(self.groupBox_corrections_calibrations)
        self.checkBox_pixel_binning.setObjectName(u"checkBox_pixel_binning")
        self.checkBox_pixel_binning.setMinimumSize(QSize(101, 0))

        self.horizontalLayout_18.addWidget(self.checkBox_pixel_binning)

        self.comboBox_pixel_binning = QComboBox(self.groupBox_corrections_calibrations)
        self.comboBox_pixel_binning.setObjectName(u"comboBox_pixel_binning")
        self.comboBox_pixel_binning.setMinimumSize(QSize(62, 0))

        self.horizontalLayout_18.addWidget(self.comboBox_pixel_binning)


        self.verticalLayout_21.addLayout(self.horizontalLayout_18)

        self.horizontalLayout_19 = QHBoxLayout()
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.checkBox_boxcar_smooth = QCheckBox(self.groupBox_corrections_calibrations)
        self.checkBox_boxcar_smooth.setObjectName(u"checkBox_boxcar_smooth")
        self.checkBox_boxcar_smooth.setMinimumSize(QSize(111, 0))

        self.horizontalLayout_19.addWidget(self.checkBox_boxcar_smooth)

        self.spinBox_boxcar_smooth = QSpinBox(self.groupBox_corrections_calibrations)
        self.spinBox_boxcar_smooth.setObjectName(u"spinBox_boxcar_smooth")
        self.spinBox_boxcar_smooth.setMinimumSize(QSize(61, 0))

        self.horizontalLayout_19.addWidget(self.spinBox_boxcar_smooth)


        self.verticalLayout_21.addLayout(self.horizontalLayout_19)


        self.verticalLayout_29.addWidget(self.groupBox_corrections_calibrations)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_29.addItem(self.verticalSpacer_2)


        self.horizontalLayout_23.addLayout(self.verticalLayout_29)

        self.verticalLayout_30 = QVBoxLayout()
        self.verticalLayout_30.setObjectName(u"verticalLayout_30")
        self.groupBox_sensor_control = QGroupBox(self.frame_9)
        self.groupBox_sensor_control.setObjectName(u"groupBox_sensor_control")
        sizePolicy2.setHeightForWidth(self.groupBox_sensor_control.sizePolicy().hasHeightForWidth())
        self.groupBox_sensor_control.setSizePolicy(sizePolicy2)
        self.groupBox_sensor_control.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.verticalLayout_22 = QVBoxLayout(self.groupBox_sensor_control)
        self.verticalLayout_22.setObjectName(u"verticalLayout_22")
        self.checkBox_thermoelectric_enable = QCheckBox(self.groupBox_sensor_control)
        self.checkBox_thermoelectric_enable.setObjectName(u"checkBox_thermoelectric_enable")
        self.checkBox_thermoelectric_enable.setMinimumSize(QSize(181, 0))

        self.verticalLayout_22.addWidget(self.checkBox_thermoelectric_enable)

        self.horizontalLayout_24 = QHBoxLayout()
        self.horizontalLayout_24.setObjectName(u"horizontalLayout_24")
        self.label_current_temperature = QLabel(self.groupBox_sensor_control)
        self.label_current_temperature.setObjectName(u"label_current_temperature")

        self.horizontalLayout_24.addWidget(self.label_current_temperature)

        self.label_current_temperature_value = QLabel(self.groupBox_sensor_control)
        self.label_current_temperature_value.setObjectName(u"label_current_temperature_value")

        self.horizontalLayout_24.addWidget(self.label_current_temperature_value)


        self.verticalLayout_22.addLayout(self.horizontalLayout_24)

        self.horizontalLayout_20 = QHBoxLayout()
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.label_temp_setpoint = QLabel(self.groupBox_sensor_control)
        self.label_temp_setpoint.setObjectName(u"label_temp_setpoint")

        self.horizontalLayout_20.addWidget(self.label_temp_setpoint)

        self.spinBox_tec_temp_setpoint = QSpinBox(self.groupBox_sensor_control)
        self.spinBox_tec_temp_setpoint.setObjectName(u"spinBox_tec_temp_setpoint")
        self.spinBox_tec_temp_setpoint.setMinimumSize(QSize(51, 0))

        self.horizontalLayout_20.addWidget(self.spinBox_tec_temp_setpoint)


        self.verticalLayout_22.addLayout(self.horizontalLayout_20)


        self.verticalLayout_30.addWidget(self.groupBox_sensor_control)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_30.addItem(self.verticalSpacer)


        self.horizontalLayout_23.addLayout(self.verticalLayout_30)

        self.groupBox_4 = QGroupBox(self.frame_9)
        self.groupBox_4.setObjectName(u"groupBox_4")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.groupBox_4.sizePolicy().hasHeightForWidth())
        self.groupBox_4.setSizePolicy(sizePolicy3)
        self.groupBox_4.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.groupBox_4.setFlat(True)
        self.groupBox_4.setCheckable(True)
        self.groupBox_4.setChecked(False)
        self.verticalLayout_24 = QVBoxLayout(self.groupBox_4)
        self.verticalLayout_24.setObjectName(u"verticalLayout_24")
        self.widget_temperatureplot = PlotWidget(self.groupBox_4)
        self.widget_temperatureplot.setObjectName(u"widget_temperatureplot")
        sizePolicy3.setHeightForWidth(self.widget_temperatureplot.sizePolicy().hasHeightForWidth())
        self.widget_temperatureplot.setSizePolicy(sizePolicy3)

        self.verticalLayout_24.addWidget(self.widget_temperatureplot)


        self.horizontalLayout_23.addWidget(self.groupBox_4)


        self.verticalLayout_31.addLayout(self.horizontalLayout_23)


        self.verticalLayout_32.addWidget(self.frame_9)

        self.horizontalLayout_22 = QHBoxLayout()
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.verticalLayout_28 = QVBoxLayout()
        self.verticalLayout_28.setObjectName(u"verticalLayout_28")
        self.groupBox_device_information = QGroupBox(self.tab_settings)
        self.groupBox_device_information.setObjectName(u"groupBox_device_information")
        self.verticalLayout_25 = QVBoxLayout(self.groupBox_device_information)
        self.verticalLayout_25.setObjectName(u"verticalLayout_25")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.label_modelserial = QLabel(self.groupBox_device_information)
        self.label_modelserial.setObjectName(u"label_modelserial")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_modelserial)

        self.label_modelserial_changeable = QLabel(self.groupBox_device_information)
        self.label_modelserial_changeable.setObjectName(u"label_modelserial_changeable")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.label_modelserial_changeable)

        self.label_firmwarerev = QLabel(self.groupBox_device_information)
        self.label_firmwarerev.setObjectName(u"label_firmwarerev")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_firmwarerev)

        self.label_firmwarerev_changeable = QLabel(self.groupBox_device_information)
        self.label_firmwarerev_changeable.setObjectName(u"label_firmwarerev_changeable")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.label_firmwarerev_changeable)

        self.label_hardwarerev = QLabel(self.groupBox_device_information)
        self.label_hardwarerev.setObjectName(u"label_hardwarerev")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_hardwarerev)

        self.label_hardwarerev_changeable = QLabel(self.groupBox_device_information)
        self.label_hardwarerev_changeable.setObjectName(u"label_hardwarerev_changeable")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.label_hardwarerev_changeable)

        self.label_pixelcount = QLabel(self.groupBox_device_information)
        self.label_pixelcount.setObjectName(u"label_pixelcount")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_pixelcount)

        self.label_pixelcount_changeable = QLabel(self.groupBox_device_information)
        self.label_pixelcount_changeable.setObjectName(u"label_pixelcount_changeable")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.label_pixelcount_changeable)

        self.label_wavelengthrangefactory = QLabel(self.groupBox_device_information)
        self.label_wavelengthrangefactory.setObjectName(u"label_wavelengthrangefactory")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_wavelengthrangefactory)

        self.label_wavelengthrangefactory_changeable = QLabel(self.groupBox_device_information)
        self.label_wavelengthrangefactory_changeable.setObjectName(u"label_wavelengthrangefactory_changeable")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.label_wavelengthrangefactory_changeable)

        self.label_integrationlimits = QLabel(self.groupBox_device_information)
        self.label_integrationlimits.setObjectName(u"label_integrationlimits")

        self.formLayout.setWidget(5, QFormLayout.ItemRole.LabelRole, self.label_integrationlimits)

        self.label_integrationlimits_changeable = QLabel(self.groupBox_device_information)
        self.label_integrationlimits_changeable.setObjectName(u"label_integrationlimits_changeable")

        self.formLayout.setWidget(5, QFormLayout.ItemRole.FieldRole, self.label_integrationlimits_changeable)

        self.label_saturationlimits = QLabel(self.groupBox_device_information)
        self.label_saturationlimits.setObjectName(u"label_saturationlimits")

        self.formLayout.setWidget(6, QFormLayout.ItemRole.LabelRole, self.label_saturationlimits)

        self.label_saturationlimits_changeable = QLabel(self.groupBox_device_information)
        self.label_saturationlimits_changeable.setObjectName(u"label_saturationlimits_changeable")

        self.formLayout.setWidget(6, QFormLayout.ItemRole.FieldRole, self.label_saturationlimits_changeable)

        self.label_thermistorpresent = QLabel(self.groupBox_device_information)
        self.label_thermistorpresent.setObjectName(u"label_thermistorpresent")

        self.formLayout.setWidget(7, QFormLayout.ItemRole.LabelRole, self.label_thermistorpresent)

        self.label_thermistorpresent_changeable = QLabel(self.groupBox_device_information)
        self.label_thermistorpresent_changeable.setObjectName(u"label_thermistorpresent_changeable")

        self.formLayout.setWidget(7, QFormLayout.ItemRole.FieldRole, self.label_thermistorpresent_changeable)

        self.label_irradiancecoefficients = QLabel(self.groupBox_device_information)
        self.label_irradiancecoefficients.setObjectName(u"label_irradiancecoefficients")

        self.formLayout.setWidget(8, QFormLayout.ItemRole.LabelRole, self.label_irradiancecoefficients)

        self.label_irradiancecoefficients_changeable = QLabel(self.groupBox_device_information)
        self.label_irradiancecoefficients_changeable.setObjectName(u"label_irradiancecoefficients_changeable")

        self.formLayout.setWidget(8, QFormLayout.ItemRole.FieldRole, self.label_irradiancecoefficients_changeable)

        self.label_shutterpresent = QLabel(self.groupBox_device_information)
        self.label_shutterpresent.setObjectName(u"label_shutterpresent")

        self.formLayout.setWidget(9, QFormLayout.ItemRole.LabelRole, self.label_shutterpresent)

        self.label_shutterpresent_changeable = QLabel(self.groupBox_device_information)
        self.label_shutterpresent_changeable.setObjectName(u"label_shutterpresent_changeable")

        self.formLayout.setWidget(9, QFormLayout.ItemRole.FieldRole, self.label_shutterpresent_changeable)


        self.verticalLayout_25.addLayout(self.formLayout)


        self.verticalLayout_28.addWidget(self.groupBox_device_information)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_28.addItem(self.verticalSpacer_3)


        self.horizontalLayout_22.addLayout(self.verticalLayout_28)

        self.verticalLayout_27 = QVBoxLayout()
        self.verticalLayout_27.setObjectName(u"verticalLayout_27")
        self.groupBox_eeprominfo = QGroupBox(self.tab_settings)
        self.groupBox_eeprominfo.setObjectName(u"groupBox_eeprominfo")
        self.groupBox_eeprominfo.setFlat(True)
        self.groupBox_eeprominfo.setCheckable(True)
        self.groupBox_eeprominfo.setChecked(False)
        self.verticalLayout_26 = QVBoxLayout(self.groupBox_eeprominfo)
        self.verticalLayout_26.setObjectName(u"verticalLayout_26")
        self.tableView_eeprom = QTableView(self.groupBox_eeprominfo)
        self.tableView_eeprom.setObjectName(u"tableView_eeprom")

        self.verticalLayout_26.addWidget(self.tableView_eeprom)


        self.verticalLayout_27.addWidget(self.groupBox_eeprominfo)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_27.addItem(self.verticalSpacer_4)


        self.horizontalLayout_22.addLayout(self.verticalLayout_27)

        self.horizontalSpacer_14 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_22.addItem(self.horizontalSpacer_14)


        self.verticalLayout_32.addLayout(self.horizontalLayout_22)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_32.addItem(self.verticalSpacer_5)


        self.verticalLayout_33.addLayout(self.verticalLayout_32)

        self.tabWidget_all.addTab(self.tab_settings, "")
        self.tab_main = QWidget()
        self.tab_main.setObjectName(u"tab_main")
        self.verticalLayout_19 = QVBoxLayout(self.tab_main)
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.splitter = QSplitter(self.tab_main)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.frame = QFrame(self.splitter)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.NoFrame)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_18 = QVBoxLayout(self.frame)
        self.verticalLayout_18.setSpacing(0)
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.verticalLayout_18.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_17 = QVBoxLayout()
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.frame_5 = QFrame(self.frame)
        self.frame_5.setObjectName(u"frame_5")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.frame_5.sizePolicy().hasHeightForWidth())
        self.frame_5.setSizePolicy(sizePolicy4)
        self.frame_5.setMinimumSize(QSize(0, 46))
        self.frame_5.setMaximumSize(QSize(16777215, 46))
        self.frame_5.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_5.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_16 = QVBoxLayout(self.frame_5)
        self.verticalLayout_16.setSpacing(0)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.verticalLayout_16.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.pushButton_full_range = QPushButton(self.frame_5)
        self.pushButton_full_range.setObjectName(u"pushButton_full_range")
        sizePolicy2.setHeightForWidth(self.pushButton_full_range.sizePolicy().hasHeightForWidth())
        self.pushButton_full_range.setSizePolicy(sizePolicy2)
        self.pushButton_full_range.setMinimumSize(QSize(75, 0))
        self.pushButton_full_range.setMaximumSize(QSize(75, 16777215))

        self.horizontalLayout_13.addWidget(self.pushButton_full_range)

        self.pushButton_zoom = QPushButton(self.frame_5)
        self.pushButton_zoom.setObjectName(u"pushButton_zoom")
        sizePolicy2.setHeightForWidth(self.pushButton_zoom.sizePolicy().hasHeightForWidth())
        self.pushButton_zoom.setSizePolicy(sizePolicy2)
        self.pushButton_zoom.setMinimumSize(QSize(75, 0))
        self.pushButton_zoom.setMaximumSize(QSize(75, 16777215))
        self.pushButton_zoom.setCheckable(True)

        self.horizontalLayout_13.addWidget(self.pushButton_zoom)

        self.pushButton_scale_intensity = QPushButton(self.frame_5)
        self.pushButton_scale_intensity.setObjectName(u"pushButton_scale_intensity")
        sizePolicy2.setHeightForWidth(self.pushButton_scale_intensity.sizePolicy().hasHeightForWidth())
        self.pushButton_scale_intensity.setSizePolicy(sizePolicy2)
        self.pushButton_scale_intensity.setMinimumSize(QSize(91, 0))
        self.pushButton_scale_intensity.setMaximumSize(QSize(91, 16777215))

        self.horizontalLayout_13.addWidget(self.pushButton_scale_intensity)

        self.checkBox_auto_intensity_scale = QCheckBox(self.frame_5)
        self.checkBox_auto_intensity_scale.setObjectName(u"checkBox_auto_intensity_scale")
        sizePolicy2.setHeightForWidth(self.checkBox_auto_intensity_scale.sizePolicy().hasHeightForWidth())
        self.checkBox_auto_intensity_scale.setSizePolicy(sizePolicy2)
        self.checkBox_auto_intensity_scale.setMinimumSize(QSize(140, 0))
        self.checkBox_auto_intensity_scale.setMaximumSize(QSize(140, 16777215))
        font = QFont()
        font.setKerning(True)
        self.checkBox_auto_intensity_scale.setFont(font)
        self.checkBox_auto_intensity_scale.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.horizontalLayout_13.addWidget(self.checkBox_auto_intensity_scale)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_13.addItem(self.horizontalSpacer_5)


        self.verticalLayout_16.addLayout(self.horizontalLayout_13)


        self.verticalLayout_17.addWidget(self.frame_5)

        self.widget = PlotWidget(self.frame)
        self.widget.setObjectName(u"widget")
        self.widget.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        self.widget.setMouseTracking(True)

        self.verticalLayout_17.addWidget(self.widget)

        self.frame_6 = QFrame(self.frame)
        self.frame_6.setObjectName(u"frame_6")
        sizePolicy4.setHeightForWidth(self.frame_6.sizePolicy().hasHeightForWidth())
        self.frame_6.setSizePolicy(sizePolicy4)
        self.frame_6.setMinimumSize(QSize(0, 46))
        self.frame_6.setMaximumSize(QSize(16777215, 46))
        self.frame_6.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_6.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_15 = QHBoxLayout(self.frame_6)
        self.horizontalLayout_15.setSpacing(0)
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.horizontalLayout_15.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.pushButton_manual_fit = QPushButton(self.frame_6)
        self.pushButton_manual_fit.setObjectName(u"pushButton_manual_fit")
        self.pushButton_manual_fit.setCheckable(True)

        self.horizontalLayout_14.addWidget(self.pushButton_manual_fit)

        self.pushButton_manual_voigt_fit = QPushButton(self.frame_6)
        self.pushButton_manual_voigt_fit.setObjectName(u"pushButton_manual_voigt_fit")
        self.pushButton_manual_voigt_fit.setCheckable(True)

        self.horizontalLayout_14.addWidget(self.pushButton_manual_voigt_fit)

        self.pushButton_clear_all_fits = QPushButton(self.frame_6)
        self.pushButton_clear_all_fits.setObjectName(u"pushButton_clear_all_fits")

        self.horizontalLayout_14.addWidget(self.pushButton_clear_all_fits)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_14.addItem(self.horizontalSpacer_6)

        self.checkBox_autofit = QCheckBox(self.frame_6)
        self.checkBox_autofit.setObjectName(u"checkBox_autofit")
        sizePolicy2.setHeightForWidth(self.checkBox_autofit.sizePolicy().hasHeightForWidth())
        self.checkBox_autofit.setSizePolicy(sizePolicy2)
        self.checkBox_autofit.setMinimumSize(QSize(75, 0))
        self.checkBox_autofit.setMaximumSize(QSize(75, 16777215))

        self.horizontalLayout_14.addWidget(self.checkBox_autofit)

        self.label_autofit_range = QLabel(self.frame_6)
        self.label_autofit_range.setObjectName(u"label_autofit_range")
        sizePolicy.setHeightForWidth(self.label_autofit_range.sizePolicy().hasHeightForWidth())
        self.label_autofit_range.setSizePolicy(sizePolicy)
        self.label_autofit_range.setMinimumSize(QSize(171, 0))
        self.label_autofit_range.setMaximumSize(QSize(171, 16777215))

        self.horizontalLayout_14.addWidget(self.label_autofit_range)

        self.doubleSpinBox_min_fitting_range_nm = QDoubleSpinBox(self.frame_6)
        self.doubleSpinBox_min_fitting_range_nm.setObjectName(u"doubleSpinBox_min_fitting_range_nm")
        sizePolicy2.setHeightForWidth(self.doubleSpinBox_min_fitting_range_nm.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_min_fitting_range_nm.setSizePolicy(sizePolicy2)
        self.doubleSpinBox_min_fitting_range_nm.setMinimumSize(QSize(81, 0))
        self.doubleSpinBox_min_fitting_range_nm.setMaximumSize(QSize(81, 16777215))

        self.horizontalLayout_14.addWidget(self.doubleSpinBox_min_fitting_range_nm)

        self.label_to = QLabel(self.frame_6)
        self.label_to.setObjectName(u"label_to")
        sizePolicy.setHeightForWidth(self.label_to.sizePolicy().hasHeightForWidth())
        self.label_to.setSizePolicy(sizePolicy)
        self.label_to.setMinimumSize(QSize(18, 0))
        self.label_to.setMaximumSize(QSize(18, 16777215))

        self.horizontalLayout_14.addWidget(self.label_to)

        self.doubleSpinBox_max_fitting_range_nm = QDoubleSpinBox(self.frame_6)
        self.doubleSpinBox_max_fitting_range_nm.setObjectName(u"doubleSpinBox_max_fitting_range_nm")
        sizePolicy2.setHeightForWidth(self.doubleSpinBox_max_fitting_range_nm.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_max_fitting_range_nm.setSizePolicy(sizePolicy2)
        self.doubleSpinBox_max_fitting_range_nm.setMinimumSize(QSize(81, 0))
        self.doubleSpinBox_max_fitting_range_nm.setMaximumSize(QSize(81, 16777215))

        self.horizontalLayout_14.addWidget(self.doubleSpinBox_max_fitting_range_nm)

        self.pushButton_fromview = QPushButton(self.frame_6)
        self.pushButton_fromview.setObjectName(u"pushButton_fromview")

        self.horizontalLayout_14.addWidget(self.pushButton_fromview)

        self.pushButton_zoom_to_range = QPushButton(self.frame_6)
        self.pushButton_zoom_to_range.setObjectName(u"pushButton_zoom_to_range")

        self.horizontalLayout_14.addWidget(self.pushButton_zoom_to_range)


        self.horizontalLayout_15.addLayout(self.horizontalLayout_14)


        self.verticalLayout_17.addWidget(self.frame_6)

        self.frame_7 = QFrame(self.frame)
        self.frame_7.setObjectName(u"frame_7")
        sizePolicy4.setHeightForWidth(self.frame_7.sizePolicy().hasHeightForWidth())
        self.frame_7.setSizePolicy(sizePolicy4)
        self.frame_7.setMinimumSize(QSize(0, 46))
        self.frame_7.setMaximumSize(QSize(16777215, 46))
        self.frame_7.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_7.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_20 = QVBoxLayout(self.frame_7)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.label_integration_progress = QLabel(self.frame_7)
        self.label_integration_progress.setObjectName(u"label_integration_progress")
        sizePolicy.setHeightForWidth(self.label_integration_progress.sizePolicy().hasHeightForWidth())
        self.label_integration_progress.setSizePolicy(sizePolicy)
        self.label_integration_progress.setMinimumSize(QSize(65, 0))
        self.label_integration_progress.setMaximumSize(QSize(65, 16777215))

        self.horizontalLayout_16.addWidget(self.label_integration_progress)

        self.progressBar = QProgressBar(self.frame_7)
        self.progressBar.setObjectName(u"progressBar")
        sizePolicy2.setHeightForWidth(self.progressBar.sizePolicy().hasHeightForWidth())
        self.progressBar.setSizePolicy(sizePolicy2)
        self.progressBar.setMinimumSize(QSize(181, 0))
        self.progressBar.setMaximumSize(QSize(181, 16777215))
        self.progressBar.setValue(0)

        self.horizontalLayout_16.addWidget(self.progressBar)

        self.label_scans_priogrss = QLabel(self.frame_7)
        self.label_scans_priogrss.setObjectName(u"label_scans_priogrss")
        sizePolicy.setHeightForWidth(self.label_scans_priogrss.sizePolicy().hasHeightForWidth())
        self.label_scans_priogrss.setSizePolicy(sizePolicy)
        self.label_scans_priogrss.setMinimumSize(QSize(45, 0))
        self.label_scans_priogrss.setMaximumSize(QSize(45, 16777215))

        self.horizontalLayout_16.addWidget(self.label_scans_priogrss)

        self.progressBar_scans_progress = QProgressBar(self.frame_7)
        self.progressBar_scans_progress.setObjectName(u"progressBar_scans_progress")
        sizePolicy2.setHeightForWidth(self.progressBar_scans_progress.sizePolicy().hasHeightForWidth())
        self.progressBar_scans_progress.setSizePolicy(sizePolicy2)
        self.progressBar_scans_progress.setMinimumSize(QSize(181, 0))
        self.progressBar_scans_progress.setMaximumSize(QSize(181, 16777215))
        self.progressBar_scans_progress.setValue(0)

        self.horizontalLayout_16.addWidget(self.progressBar_scans_progress)

        self.label_time_left = QLabel(self.frame_7)
        self.label_time_left.setObjectName(u"label_time_left")
        sizePolicy.setHeightForWidth(self.label_time_left.sizePolicy().hasHeightForWidth())
        self.label_time_left.setSizePolicy(sizePolicy)
        self.label_time_left.setMinimumSize(QSize(100, 0))
        self.label_time_left.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout_16.addWidget(self.label_time_left)

        self.label_time_left_seconds = QLabel(self.frame_7)
        self.label_time_left_seconds.setObjectName(u"label_time_left_seconds")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.label_time_left_seconds.sizePolicy().hasHeightForWidth())
        self.label_time_left_seconds.setSizePolicy(sizePolicy5)
        self.label_time_left_seconds.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_16.addWidget(self.label_time_left_seconds)

        self.label_seconds_unit = QLabel(self.frame_7)
        self.label_seconds_unit.setObjectName(u"label_seconds_unit")
        sizePolicy.setHeightForWidth(self.label_seconds_unit.sizePolicy().hasHeightForWidth())
        self.label_seconds_unit.setSizePolicy(sizePolicy)
        self.label_seconds_unit.setMinimumSize(QSize(50, 0))
        self.label_seconds_unit.setMaximumSize(QSize(50, 16777215))
        self.label_seconds_unit.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_16.addWidget(self.label_seconds_unit)

        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_16.addItem(self.horizontalSpacer_7)

        self.label_xy = QLabel(self.frame_7)
        self.label_xy.setObjectName(u"label_xy")
        sizePolicy.setHeightForWidth(self.label_xy.sizePolicy().hasHeightForWidth())
        self.label_xy.setSizePolicy(sizePolicy)
        self.label_xy.setMinimumSize(QSize(25, 0))
        self.label_xy.setMaximumSize(QSize(25, 16777215))

        self.horizontalLayout_16.addWidget(self.label_xy)

        self.label_xy_position = QLabel(self.frame_7)
        self.label_xy_position.setObjectName(u"label_xy_position")
        sizePolicy5.setHeightForWidth(self.label_xy_position.sizePolicy().hasHeightForWidth())
        self.label_xy_position.setSizePolicy(sizePolicy5)

        self.horizontalLayout_16.addWidget(self.label_xy_position)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_16.addItem(self.horizontalSpacer_8)

        self.label_P = QLabel(self.frame_7)
        self.label_P.setObjectName(u"label_P")
        sizePolicy.setHeightForWidth(self.label_P.sizePolicy().hasHeightForWidth())
        self.label_P.setSizePolicy(sizePolicy)
        self.label_P.setMinimumSize(QSize(50, 0))
        self.label_P.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout_16.addWidget(self.label_P)

        self.label_current_pressure = QLabel(self.frame_7)
        self.label_current_pressure.setObjectName(u"label_current_pressure")
        sizePolicy5.setHeightForWidth(self.label_current_pressure.sizePolicy().hasHeightForWidth())
        self.label_current_pressure.setSizePolicy(sizePolicy5)

        self.horizontalLayout_16.addWidget(self.label_current_pressure)

        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_16.addItem(self.horizontalSpacer_9)


        self.verticalLayout_20.addLayout(self.horizontalLayout_16)


        self.verticalLayout_17.addWidget(self.frame_7)


        self.verticalLayout_18.addLayout(self.verticalLayout_17)

        self.splitter.addWidget(self.frame)
        self.frame_2 = QFrame(self.splitter)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setMinimumSize(QSize(301, 0))
        self.frame_2.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_15 = QVBoxLayout(self.frame_2)
        self.verticalLayout_15.setSpacing(0)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.verticalLayout_15.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_14 = QVBoxLayout()
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.groupBox_calibrations = QGroupBox(self.frame_2)
        self.groupBox_calibrations.setObjectName(u"groupBox_calibrations")
        self.verticalLayout_6 = QVBoxLayout(self.groupBox_calibrations)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.frame_3 = QFrame(self.groupBox_calibrations)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame_3)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.label_pressurecalibrations = QLabel(self.frame_3)
        self.label_pressurecalibrations.setObjectName(u"label_pressurecalibrations")

        self.horizontalLayout_3.addWidget(self.label_pressurecalibrations)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.comboBox_pressurecalibrations = QComboBox(self.frame_3)
        self.comboBox_pressurecalibrations.setObjectName(u"comboBox_pressurecalibrations")
        sizePolicy1.setHeightForWidth(self.comboBox_pressurecalibrations.sizePolicy().hasHeightForWidth())
        self.comboBox_pressurecalibrations.setSizePolicy(sizePolicy1)

        self.horizontalLayout_2.addWidget(self.comboBox_pressurecalibrations)

        self.pushButton_pressurecalib_source = QPushButton(self.frame_3)
        self.pushButton_pressurecalib_source.setObjectName(u"pushButton_pressurecalib_source")
        sizePolicy2.setHeightForWidth(self.pushButton_pressurecalib_source.sizePolicy().hasHeightForWidth())
        self.pushButton_pressurecalib_source.setSizePolicy(sizePolicy2)
        self.pushButton_pressurecalib_source.setMinimumSize(QSize(20, 0))
        self.pushButton_pressurecalib_source.setMaximumSize(QSize(20, 16777215))

        self.horizontalLayout_2.addWidget(self.pushButton_pressurecalib_source)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)


        self.verticalLayout_4.addLayout(self.verticalLayout_3)


        self.horizontalLayout_5.addWidget(self.frame_3)

        self.frame_4 = QFrame(self.groupBox_calibrations)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_4.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.frame_4)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)

        self.label_temperaturecalibrations = QLabel(self.frame_4)
        self.label_temperaturecalibrations.setObjectName(u"label_temperaturecalibrations")

        self.horizontalLayout_4.addWidget(self.label_temperaturecalibrations)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_4)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.comboBox_temperaturecalibrations = QComboBox(self.frame_4)
        self.comboBox_temperaturecalibrations.setObjectName(u"comboBox_temperaturecalibrations")
        sizePolicy1.setHeightForWidth(self.comboBox_temperaturecalibrations.sizePolicy().hasHeightForWidth())
        self.comboBox_temperaturecalibrations.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.comboBox_temperaturecalibrations)

        self.pushButton_temperaturecalib_source = QPushButton(self.frame_4)
        self.pushButton_temperaturecalib_source.setObjectName(u"pushButton_temperaturecalib_source")
        sizePolicy2.setHeightForWidth(self.pushButton_temperaturecalib_source.sizePolicy().hasHeightForWidth())
        self.pushButton_temperaturecalib_source.setSizePolicy(sizePolicy2)
        self.pushButton_temperaturecalib_source.setMinimumSize(QSize(20, 0))
        self.pushButton_temperaturecalib_source.setMaximumSize(QSize(20, 16777215))

        self.horizontalLayout.addWidget(self.pushButton_temperaturecalib_source)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.verticalLayout_5.addLayout(self.verticalLayout_2)


        self.horizontalLayout_5.addWidget(self.frame_4)


        self.verticalLayout_6.addLayout(self.horizontalLayout_5)


        self.verticalLayout_14.addWidget(self.groupBox_calibrations)

        self.groupBox_reference = QGroupBox(self.frame_2)
        self.groupBox_reference.setObjectName(u"groupBox_reference")
        self.groupBox_reference.setCheckable(True)
        self.groupBox_reference.setChecked(False)
        self.verticalLayout_7 = QVBoxLayout(self.groupBox_reference)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_reference_wavelength = QLabel(self.groupBox_reference)
        self.label_reference_wavelength.setObjectName(u"label_reference_wavelength")
        sizePolicy.setHeightForWidth(self.label_reference_wavelength.sizePolicy().hasHeightForWidth())
        self.label_reference_wavelength.setSizePolicy(sizePolicy)
        self.label_reference_wavelength.setMinimumSize(QSize(111, 0))
        self.label_reference_wavelength.setMaximumSize(QSize(111, 16777215))

        self.horizontalLayout_6.addWidget(self.label_reference_wavelength)

        self.lineEdit_reference_wavelength_nm = QLineEdit(self.groupBox_reference)
        self.lineEdit_reference_wavelength_nm.setObjectName(u"lineEdit_reference_wavelength_nm")

        self.horizontalLayout_6.addWidget(self.lineEdit_reference_wavelength_nm)

        self.label_reference_temperature = QLabel(self.groupBox_reference)
        self.label_reference_temperature.setObjectName(u"label_reference_temperature")
        sizePolicy.setHeightForWidth(self.label_reference_temperature.sizePolicy().hasHeightForWidth())
        self.label_reference_temperature.setSizePolicy(sizePolicy)
        self.label_reference_temperature.setMinimumSize(QSize(95, 0))
        self.label_reference_temperature.setMaximumSize(QSize(91, 16777215))

        self.horizontalLayout_6.addWidget(self.label_reference_temperature)

        self.lineEdit_reference_temperature_c = QLineEdit(self.groupBox_reference)
        self.lineEdit_reference_temperature_c.setObjectName(u"lineEdit_reference_temperature_c")

        self.horizontalLayout_6.addWidget(self.lineEdit_reference_temperature_c)


        self.verticalLayout_7.addLayout(self.horizontalLayout_6)


        self.verticalLayout_14.addWidget(self.groupBox_reference)

        self.groupBox = QGroupBox(self.frame_2)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_9 = QVBoxLayout(self.groupBox)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_measured_wavelength = QLabel(self.groupBox)
        self.label_measured_wavelength.setObjectName(u"label_measured_wavelength")
        sizePolicy.setHeightForWidth(self.label_measured_wavelength.sizePolicy().hasHeightForWidth())
        self.label_measured_wavelength.setSizePolicy(sizePolicy)
        self.label_measured_wavelength.setMinimumSize(QSize(111, 0))
        self.label_measured_wavelength.setMaximumSize(QSize(111, 16777215))

        self.horizontalLayout_8.addWidget(self.label_measured_wavelength)

        self.lineEdit_measured_wavelength_nm = QLineEdit(self.groupBox)
        self.lineEdit_measured_wavelength_nm.setObjectName(u"lineEdit_measured_wavelength_nm")

        self.horizontalLayout_8.addWidget(self.lineEdit_measured_wavelength_nm)

        self.label_measured_temperature = QLabel(self.groupBox)
        self.label_measured_temperature.setObjectName(u"label_measured_temperature")
        sizePolicy.setHeightForWidth(self.label_measured_temperature.sizePolicy().hasHeightForWidth())
        self.label_measured_temperature.setSizePolicy(sizePolicy)
        self.label_measured_temperature.setMinimumSize(QSize(95, 0))
        self.label_measured_temperature.setMaximumSize(QSize(91, 16777215))

        self.horizontalLayout_8.addWidget(self.label_measured_temperature)

        self.lineEdit_measured_temperature_c = QLineEdit(self.groupBox)
        self.lineEdit_measured_temperature_c.setObjectName(u"lineEdit_measured_temperature_c")

        self.horizontalLayout_8.addWidget(self.lineEdit_measured_temperature_c)


        self.verticalLayout_8.addLayout(self.horizontalLayout_8)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_pressure = QLabel(self.groupBox)
        self.label_pressure.setObjectName(u"label_pressure")
        sizePolicy.setHeightForWidth(self.label_pressure.sizePolicy().hasHeightForWidth())
        self.label_pressure.setSizePolicy(sizePolicy)
        self.label_pressure.setMinimumSize(QSize(131, 0))
        font1 = QFont()
        font1.setPointSize(14)
        self.label_pressure.setFont(font1)

        self.horizontalLayout_7.addWidget(self.label_pressure)

        self.label_result_pressure_gpa = QLabel(self.groupBox)
        self.label_result_pressure_gpa.setObjectName(u"label_result_pressure_gpa")
        palette = QPalette()
        brush = QBrush(QColor(170, 0, 0, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush)
        brush1 = QBrush(QColor(255, 0, 0, 255))
        brush1.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Light, brush1)
        brush2 = QBrush(QColor(212, 0, 0, 255))
        brush2.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Midlight, brush2)
        brush3 = QBrush(QColor(85, 0, 0, 255))
        brush3.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Dark, brush3)
        brush4 = QBrush(QColor(113, 0, 0, 255))
        brush4.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Mid, brush4)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, brush)
        brush5 = QBrush(QColor(255, 255, 255, 255))
        brush5.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.BrightText, brush5)
        brush6 = QBrush(QColor(0, 0, 0, 255))
        brush6.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush6)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush5)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Shadow, brush6)
        brush7 = QBrush(QColor(212, 127, 127, 255))
        brush7.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.AlternateBase, brush7)
        brush8 = QBrush(QColor(255, 255, 220, 255))
        brush8.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipBase, brush8)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipText, brush6)
        brush9 = QBrush(QColor(0, 0, 0, 127))
        brush9.setStyle(Qt.BrushStyle.SolidPattern)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, brush9)
#endif
#if QT_VERSION >= QT_VERSION_CHECK(6, 6, 0)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Accent, brush5)
#endif
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Light, brush1)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Midlight, brush2)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Dark, brush3)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Mid, brush4)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.BrightText, brush5)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, brush6)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush5)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Shadow, brush6)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.AlternateBase, brush7)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipBase, brush8)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipText, brush6)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, brush9)
#endif
#if QT_VERSION >= QT_VERSION_CHECK(6, 6, 0)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Accent, brush5)
#endif
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush3)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Light, brush1)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Midlight, brush2)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Dark, brush3)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Mid, brush4)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, brush3)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.BrightText, brush5)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, brush3)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Shadow, brush6)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.AlternateBase, brush)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipBase, brush8)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipText, brush6)
        brush10 = QBrush(QColor(85, 0, 0, 127))
        brush10.setStyle(Qt.BrushStyle.SolidPattern)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, brush10)
#endif
        brush11 = QBrush(QColor(221, 0, 0, 255))
        brush11.setStyle(Qt.BrushStyle.SolidPattern)
#if QT_VERSION >= QT_VERSION_CHECK(6, 6, 0)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Accent, brush11)
#endif
        self.label_result_pressure_gpa.setPalette(palette)
        font2 = QFont()
        font2.setPointSize(16)
        font2.setBold(True)
        self.label_result_pressure_gpa.setFont(font2)

        self.horizontalLayout_7.addWidget(self.label_result_pressure_gpa)


        self.verticalLayout_8.addLayout(self.horizontalLayout_7)


        self.verticalLayout_9.addLayout(self.verticalLayout_8)


        self.verticalLayout_14.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(self.frame_2)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_11 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_10 = QVBoxLayout()
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_integrationtime = QLabel(self.groupBox_2)
        self.label_integrationtime.setObjectName(u"label_integrationtime")
        sizePolicy.setHeightForWidth(self.label_integrationtime.sizePolicy().hasHeightForWidth())
        self.label_integrationtime.setSizePolicy(sizePolicy)
        self.label_integrationtime.setMinimumSize(QSize(121, 0))
        self.label_integrationtime.setMaximumSize(QSize(121, 16777215))

        self.horizontalLayout_9.addWidget(self.label_integrationtime)

        self.doubleSpinBox_integration_time_ms = QDoubleSpinBox(self.groupBox_2)
        self.doubleSpinBox_integration_time_ms.setObjectName(u"doubleSpinBox_integration_time_ms")

        self.horizontalLayout_9.addWidget(self.doubleSpinBox_integration_time_ms)

        self.label_scansaverage = QLabel(self.groupBox_2)
        self.label_scansaverage.setObjectName(u"label_scansaverage")
        sizePolicy.setHeightForWidth(self.label_scansaverage.sizePolicy().hasHeightForWidth())
        self.label_scansaverage.setSizePolicy(sizePolicy)
        self.label_scansaverage.setMinimumSize(QSize(91, 0))
        self.label_scansaverage.setMaximumSize(QSize(91, 16777215))

        self.horizontalLayout_9.addWidget(self.label_scansaverage)

        self.spinBox_scansaverage = QSpinBox(self.groupBox_2)
        self.spinBox_scansaverage.setObjectName(u"spinBox_scansaverage")

        self.horizontalLayout_9.addWidget(self.spinBox_scansaverage)


        self.verticalLayout_10.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.pushButton_continuous = QPushButton(self.groupBox_2)
        self.pushButton_continuous.setObjectName(u"pushButton_continuous")
        self.pushButton_continuous.setCheckable(True)

        self.horizontalLayout_10.addWidget(self.pushButton_continuous)

        self.pushButton_single = QPushButton(self.groupBox_2)
        self.pushButton_single.setObjectName(u"pushButton_single")
        self.pushButton_single.setCheckable(True)

        self.horizontalLayout_10.addWidget(self.pushButton_single)

        self.pushButton_optimize = QPushButton(self.groupBox_2)
        self.pushButton_optimize.setObjectName(u"pushButton_optimize")
        self.pushButton_optimize.setCheckable(False)

        self.horizontalLayout_10.addWidget(self.pushButton_optimize)

        self.pushButton_background = QPushButton(self.groupBox_2)
        self.pushButton_background.setObjectName(u"pushButton_background")
        self.pushButton_background.setEnabled(True)
        self.pushButton_background.setCheckable(True)

        self.horizontalLayout_10.addWidget(self.pushButton_background)


        self.verticalLayout_10.addLayout(self.horizontalLayout_10)


        self.verticalLayout_11.addLayout(self.verticalLayout_10)


        self.verticalLayout_14.addWidget(self.groupBox_2)

        self.groupBox_3 = QGroupBox(self.frame_2)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.verticalLayout_13 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_12 = QVBoxLayout()
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.lineEdit_measurement_name = QLineEdit(self.groupBox_3)
        self.lineEdit_measurement_name.setObjectName(u"lineEdit_measurement_name")

        self.horizontalLayout_11.addWidget(self.lineEdit_measurement_name)

        self.pushButton_add_measurement = QPushButton(self.groupBox_3)
        self.pushButton_add_measurement.setObjectName(u"pushButton_add_measurement")
        sizePolicy2.setHeightForWidth(self.pushButton_add_measurement.sizePolicy().hasHeightForWidth())
        self.pushButton_add_measurement.setSizePolicy(sizePolicy2)
        self.pushButton_add_measurement.setMinimumSize(QSize(50, 0))
        self.pushButton_add_measurement.setMaximumSize(QSize(75, 16777215))

        self.horizontalLayout_11.addWidget(self.pushButton_add_measurement)

        self.pushButton_remove_measurement = QPushButton(self.groupBox_3)
        self.pushButton_remove_measurement.setObjectName(u"pushButton_remove_measurement")
        sizePolicy2.setHeightForWidth(self.pushButton_remove_measurement.sizePolicy().hasHeightForWidth())
        self.pushButton_remove_measurement.setSizePolicy(sizePolicy2)
        self.pushButton_remove_measurement.setMinimumSize(QSize(50, 0))
        self.pushButton_remove_measurement.setMaximumSize(QSize(75, 16777215))

        self.horizontalLayout_11.addWidget(self.pushButton_remove_measurement)

        self.pushButton_removeall_measurements = QPushButton(self.groupBox_3)
        self.pushButton_removeall_measurements.setObjectName(u"pushButton_removeall_measurements")
        sizePolicy2.setHeightForWidth(self.pushButton_removeall_measurements.sizePolicy().hasHeightForWidth())
        self.pushButton_removeall_measurements.setSizePolicy(sizePolicy2)
        self.pushButton_removeall_measurements.setMinimumSize(QSize(75, 0))
        self.pushButton_removeall_measurements.setMaximumSize(QSize(75, 16777215))

        self.horizontalLayout_11.addWidget(self.pushButton_removeall_measurements)


        self.verticalLayout_12.addLayout(self.horizontalLayout_11)

        self.tableView_saved_measurements = QTableView(self.groupBox_3)
        self.tableView_saved_measurements.setObjectName(u"tableView_saved_measurements")
        self.tableView_saved_measurements.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)

        self.verticalLayout_12.addWidget(self.tableView_saved_measurements)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.pushButton_save_selected = QPushButton(self.groupBox_3)
        self.pushButton_save_selected.setObjectName(u"pushButton_save_selected")

        self.horizontalLayout_12.addWidget(self.pushButton_save_selected)

        self.pushButton_save_all = QPushButton(self.groupBox_3)
        self.pushButton_save_all.setObjectName(u"pushButton_save_all")

        self.horizontalLayout_12.addWidget(self.pushButton_save_all)

        self.pushButton_load = QPushButton(self.groupBox_3)
        self.pushButton_load.setObjectName(u"pushButton_load")

        self.horizontalLayout_12.addWidget(self.pushButton_load)

        self.checkBox_auto_save_measurements = QCheckBox(self.groupBox_3)
        self.checkBox_auto_save_measurements.setObjectName(u"checkBox_auto_save_measurements")

        self.horizontalLayout_12.addWidget(self.checkBox_auto_save_measurements)


        self.verticalLayout_12.addLayout(self.horizontalLayout_12)


        self.verticalLayout_13.addLayout(self.verticalLayout_12)


        self.verticalLayout_14.addWidget(self.groupBox_3)


        self.verticalLayout_15.addLayout(self.verticalLayout_14)

        self.splitter.addWidget(self.frame_2)

        self.verticalLayout_19.addWidget(self.splitter)

        self.tabWidget_all.addTab(self.tab_main, "")

        self.verticalLayout.addWidget(self.tabWidget_all)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1600, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabWidget_all.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Me so Raman", None))
        self.label_device.setText(QCoreApplication.translate("MainWindow", u"Device:", None))
        self.pushButton_refresh_device.setText(QCoreApplication.translate("MainWindow", u"Refresh \u27f3", None))
        self.pushButton_defaults_device.setText(QCoreApplication.translate("MainWindow", u"Apply settings as default for this device", None))
        self.groupBox_corrections_calibrations.setTitle(QCoreApplication.translate("MainWindow", u"Corrections and Calibrations", None))
        self.checkBox_electric_dark.setText(QCoreApplication.translate("MainWindow", u"Electric-dark correction", None))
        self.checkBox_optical_dark.setText(QCoreApplication.translate("MainWindow", u"Optical-dark correction", None))
        self.checkBox_stray_light_correction.setText(QCoreApplication.translate("MainWindow", u"Stray-light correction", None))
        self.checkBox_non_linearity.setText(QCoreApplication.translate("MainWindow", u"Non-linearity correction", None))
        self.checkBox_irradiance.setText(QCoreApplication.translate("MainWindow", u"Irradiance calibration", None))
        self.checkBox_pixel_binning.setText(QCoreApplication.translate("MainWindow", u"Pixel-binning", None))
        self.checkBox_boxcar_smooth.setText(QCoreApplication.translate("MainWindow", u"Boxcar smooth:", None))
        self.groupBox_sensor_control.setTitle(QCoreApplication.translate("MainWindow", u"Sensor Control", None))
        self.checkBox_thermoelectric_enable.setText(QCoreApplication.translate("MainWindow", u"Thermoelectric (TEC) enable", None))
        self.label_current_temperature.setText(QCoreApplication.translate("MainWindow", u"Current temperature: (\u00b0C):", None))
        self.label_current_temperature_value.setText(QCoreApplication.translate("MainWindow", u"\u2014", None))
        self.label_temp_setpoint.setText(QCoreApplication.translate("MainWindow", u"Temperature set-point (\u00b0C):", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", u"Detector Temperature", None))
        self.groupBox_device_information.setTitle(QCoreApplication.translate("MainWindow", u"Device information (read-only)", None))
        self.label_modelserial.setText(QCoreApplication.translate("MainWindow", u"Model / serial", None))
        self.label_modelserial_changeable.setText(QCoreApplication.translate("MainWindow", u"\u2014", None))
        self.label_firmwarerev.setText(QCoreApplication.translate("MainWindow", u"Firmware rev", None))
        self.label_firmwarerev_changeable.setText(QCoreApplication.translate("MainWindow", u"\u2014", None))
        self.label_hardwarerev.setText(QCoreApplication.translate("MainWindow", u"Hardware rev", None))
        self.label_hardwarerev_changeable.setText(QCoreApplication.translate("MainWindow", u"\u2014", None))
        self.label_pixelcount.setText(QCoreApplication.translate("MainWindow", u"Pixel count", None))
        self.label_pixelcount_changeable.setText(QCoreApplication.translate("MainWindow", u"\u2014", None))
        self.label_wavelengthrangefactory.setText(QCoreApplication.translate("MainWindow", u"\u03bb range (factory)", None))
        self.label_wavelengthrangefactory_changeable.setText(QCoreApplication.translate("MainWindow", u"\u2014", None))
        self.label_integrationlimits.setText(QCoreApplication.translate("MainWindow", u"Integration limits", None))
        self.label_integrationlimits_changeable.setText(QCoreApplication.translate("MainWindow", u"\u2014", None))
        self.label_saturationlimits.setText(QCoreApplication.translate("MainWindow", u"Saturation limits", None))
        self.label_saturationlimits_changeable.setText(QCoreApplication.translate("MainWindow", u"\u2014", None))
        self.label_thermistorpresent.setText(QCoreApplication.translate("MainWindow", u"Thermistor present", None))
        self.label_thermistorpresent_changeable.setText(QCoreApplication.translate("MainWindow", u"\u2014", None))
        self.label_irradiancecoefficients.setText(QCoreApplication.translate("MainWindow", u"Irradiance coefficients", None))
        self.label_irradiancecoefficients_changeable.setText(QCoreApplication.translate("MainWindow", u"\u2014", None))
        self.label_shutterpresent.setText(QCoreApplication.translate("MainWindow", u"Shutter present", None))
        self.label_shutterpresent_changeable.setText(QCoreApplication.translate("MainWindow", u"\u2014", None))
        self.groupBox_eeprominfo.setTitle(QCoreApplication.translate("MainWindow", u"Show EEPROM values", None))
        self.tabWidget_all.setTabText(self.tabWidget_all.indexOf(self.tab_settings), QCoreApplication.translate("MainWindow", u"Settings", None))
        self.pushButton_full_range.setText(QCoreApplication.translate("MainWindow", u"Full range", None))
        self.pushButton_zoom.setText(QCoreApplication.translate("MainWindow", u"Zoom", None))
        self.pushButton_scale_intensity.setText(QCoreApplication.translate("MainWindow", u"Scale intensity", None))
        self.checkBox_auto_intensity_scale.setText(QCoreApplication.translate("MainWindow", u"Auto scale intensity:", None))
        self.pushButton_manual_fit.setText(QCoreApplication.translate("MainWindow", u"Manual fit", None))
        self.pushButton_manual_voigt_fit.setText(QCoreApplication.translate("MainWindow", u"Manual Voigt fit", None))
        self.pushButton_clear_all_fits.setText(QCoreApplication.translate("MainWindow", u"Clear all", None))
        self.checkBox_autofit.setText(QCoreApplication.translate("MainWindow", u"Auto fit", None))
        self.label_autofit_range.setText(QCoreApplication.translate("MainWindow", u"Wavelength fitting range (nm):", None))
        self.label_to.setText(QCoreApplication.translate("MainWindow", u"to", None))
        self.pushButton_fromview.setText(QCoreApplication.translate("MainWindow", u"From view", None))
        self.pushButton_zoom_to_range.setText(QCoreApplication.translate("MainWindow", u"Zoom to view", None))
        self.label_integration_progress.setText(QCoreApplication.translate("MainWindow", u"Integration:", None))
        self.label_scans_priogrss.setText(QCoreApplication.translate("MainWindow", u"Scans:", None))
        self.label_time_left.setText(QCoreApplication.translate("MainWindow", u"Remaining time:", None))
        self.label_time_left_seconds.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_seconds_unit.setText(QCoreApplication.translate("MainWindow", u"seconds", None))
        self.label_xy.setText(QCoreApplication.translate("MainWindow", u"x, y:", None))
        self.label_xy_position.setText(QCoreApplication.translate("MainWindow", u"0, 0", None))
        self.label_P.setText(QCoreApplication.translate("MainWindow", u"P (GPa):", None))
        self.label_current_pressure.setText(QCoreApplication.translate("MainWindow", u"0.00", None))
        self.groupBox_calibrations.setTitle(QCoreApplication.translate("MainWindow", u"Calibrations", None))
        self.label_pressurecalibrations.setText(QCoreApplication.translate("MainWindow", u"Pressure calibrations", None))
        self.pushButton_pressurecalib_source.setText(QCoreApplication.translate("MainWindow", u"?", None))
        self.label_temperaturecalibrations.setText(QCoreApplication.translate("MainWindow", u"Temperature calibrations", None))
        self.pushButton_temperaturecalib_source.setText(QCoreApplication.translate("MainWindow", u"?", None))
        self.groupBox_reference.setTitle(QCoreApplication.translate("MainWindow", u"Reference", None))
        self.label_reference_wavelength.setText(QCoreApplication.translate("MainWindow", u"Wavelength R1 (nm):", None))
        self.lineEdit_reference_wavelength_nm.setText(QCoreApplication.translate("MainWindow", u"694.22", None))
        self.label_reference_temperature.setText(QCoreApplication.translate("MainWindow", u"Temperature (\u00b0C):", None))
        self.lineEdit_reference_temperature_c.setText(QCoreApplication.translate("MainWindow", u"25", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Measured", None))
        self.label_measured_wavelength.setText(QCoreApplication.translate("MainWindow", u"Wavelength R1 (nm):", None))
        self.label_measured_temperature.setText(QCoreApplication.translate("MainWindow", u"Temperature (\u00b0C):", None))
        self.lineEdit_measured_temperature_c.setText(QCoreApplication.translate("MainWindow", u"25", None))
        self.label_pressure.setText(QCoreApplication.translate("MainWindow", u"Pressure (GPa):", None))
        self.label_result_pressure_gpa.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Spectrometer", None))
        self.label_integrationtime.setText(QCoreApplication.translate("MainWindow", u"Integration time (ms):", None))
        self.label_scansaverage.setText(QCoreApplication.translate("MainWindow", u"Scans to average:", None))
        self.pushButton_continuous.setText(QCoreApplication.translate("MainWindow", u"Continuous", None))
        self.pushButton_single.setText(QCoreApplication.translate("MainWindow", u"Single", None))
        self.pushButton_optimize.setText(QCoreApplication.translate("MainWindow", u"Optimize", None))
        self.pushButton_background.setText(QCoreApplication.translate("MainWindow", u"Background", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"Measurements", None))
        self.pushButton_add_measurement.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.pushButton_remove_measurement.setText(QCoreApplication.translate("MainWindow", u"Remove", None))
        self.pushButton_removeall_measurements.setText(QCoreApplication.translate("MainWindow", u"Remove all", None))
        self.pushButton_save_selected.setText(QCoreApplication.translate("MainWindow", u"Save selected", None))
        self.pushButton_save_all.setText(QCoreApplication.translate("MainWindow", u"Save all", None))
        self.pushButton_load.setText(QCoreApplication.translate("MainWindow", u"Load", None))
        self.checkBox_auto_save_measurements.setText(QCoreApplication.translate("MainWindow", u"Auto save", None))
        self.tabWidget_all.setTabText(self.tabWidget_all.indexOf(self.tab_main), QCoreApplication.translate("MainWindow", u"Main", None))
    # retranslateUi

