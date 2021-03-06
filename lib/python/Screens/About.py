from enigma import *
from Screen import Screen
from Components.Element import cached
from Components.config import config
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Sources.StaticText import StaticText
from Components.Harddisk import Harddisk
from Components.NimManager import nimmanager
from Components.About import about, getVersionString, getChipSetString, getKernelVersionString, getCPUString, getCpuCoresString, getPythonVersionString, getGStreamerVersionString, getDriverInstalledDate
from Components.ScrollLabel import ScrollLabel
from Components.Console import Console
from Components.Converter.Poll import Poll

from ServiceReference import ServiceReference
from enigma import iServiceInformation, eServiceReference, eServiceCenter, iPlayableService, iPlayableServicePtr, eTimer, eConsoleAppContainer, getEnigmaVersionString, eLabel, getBestPlayableServiceReference, eDVBFrontendParametersSatellite, eEPGCache
from boxbranding import getBoxType, getMachineBuild, getMachineBrand, getMachineName, getImageVersion, getImageType, getImageBuild, getDriverDate

from Components.Pixmap import MultiPixmap
from Components.Network import iNetwork

from Components.Label import Label
from Components.ProgressBar import ProgressBar

from os import popen
from Tools.StbHardware import getFPVersion
from Tools.Directories import fileExists, resolveFilename, SCOPE_CURRENT_SKIN, SCOPE_PLUGINS
from Tools.Transponder import ConvertToHumanReadable, getChannelNumber

from os import path
from re import search

from Components.HTMLComponent import HTMLComponent
from Components.GUIComponent import GUIComponent
import skin
import os
import time
import re

boxtype = getBoxType()

def getAboutText():
	AboutText = ""

	AboutText += _("Model:\t %s %s\n") % (getMachineBrand(), getMachineName())

	if path.exists('/proc/stb/info/chipset'):
		AboutText += _("Chipset:\t %s") % str(getChipSetString()) + "\n"

	bogoMIPS = ""
	if path.exists('/proc/cpuinfo'):
		f = open('/proc/cpuinfo', 'r')
		temp = f.readlines()
		f.close()
		try:
			for lines in temp:
				lisp = lines.split(': ')
				if lisp[0].startswith('BogoMIPS'):
					bogoMIPS = "" + str(int(float(lisp[1].replace('\n','')))) + ""
					#bogoMIPS = "" + lisp[1].replace('\n','') + ""
					break
		except:
			pass

	cpuMHz = ""
	if getMachineBuild() in ('vusolo4k'):
		cpuMHz = "   (1,5 GHz)"
	else:
		if path.exists('/proc/cpuinfo'):
			f = open('/proc/cpuinfo', 'r')
			temp = f.readlines()
			f.close()
			try:
				for lines in temp:
					lisp = lines.split(': ')
					if lisp[0].startswith('cpu MHz'):
						#cpuMHz = "   (" +  lisp[1].replace('\n', '') + " MHz)"
						cpuMHz = "   (" +  str(int(float(lisp[1].replace('\n', '')))) + " MHz)"
						break
			except:
				pass

	openLD = "OpenLD "

	AboutText += _("CPU:\t %s") % str(getCPUString()) + cpuMHz + "\n"
	AboutText += _("Cores:\t %s") % str(getCpuCoresString()) + "\n"
	AboutText += _("BogoMIPS:\t %s") % bogoMIPS + "\n"
	AboutText += _("Firmware:\t %s") % openLD + str(getImageVersion()) + "\n"
	#AboutText += _("Build:\t %s") % getImageBuild() + "\n"
	#AboutText += _("Image Type:\t%s\n") % getImageType() + "\n"
	AboutText += _("Kernel:\t %s") % str(getKernelVersionString()) + "\n"
	AboutText += _("DVB drivers:\t %s") % str(getDriverInstalledDate()) + "\n"
	AboutText += _("Last update:\t %s") % str(getEnigmaVersionString()) + "\n"
	AboutText += _("GStreamer:\t%s") % str(getGStreamerVersionString().replace('GStreamer','')) + "\n"
	AboutText += _("Python:\t %s") % getPythonVersionString() + "\n\n"
	#AboutText += _("CPU Load:\t %s") % str(about.getLoadCPUString()) + "\n"

	#AboutText += _("Installed:\t ") + about.getFlashDateString() + "\n"
	#AboutText += _("Restarts:\t %d ") % config.misc.startCounter.value + "\n\n"

	fp_version = getFPVersion()
	if fp_version is None:
		fp_version = ""
	elif fp_version != 0:
		fp_version = _("Frontprocessor version: %s") % fp_version
		AboutText += fp_version + "\n"

	tempinfo = ""
	if path.exists('/proc/stb/sensors/temp0/value'):
		f = open('/proc/stb/sensors/temp0/value', 'r')
		tempinfo = f.read()
		f.close()
	elif path.exists('/proc/stb/fp/temp_sensor'):
		f = open('/proc/stb/fp/temp_sensor', 'r')
		tempinfo = f.read()
		f.close()
	elif path.exists('/proc/stb/sensors/temp/value'):
		f = open('/proc/stb/sensors/temp/value', 'r')
		tempinfo = f.read()
		f.close()
	if tempinfo and int(tempinfo.replace('\n', '')) > 0:
		mark = str('\xc2\xb0')
		AboutText += _("System temperature:\t%s") % tempinfo.replace('\n', '').replace(' ','') + mark + "C\n"

	tempinfo = ""
	if path.exists('/proc/stb/fp/temp_sensor_avs'):
		f = open('/proc/stb/fp/temp_sensor_avs', 'r')
		tempinfo = f.read()
		f.close()
	if tempinfo and int(tempinfo.replace('\n', '')) > 0:
		mark = str('\xc2\xb0')
		AboutText += _("Processor temperature:\t%s") % tempinfo.replace('\n', '').replace(' ','') + mark + "C\n"
	AboutLcdText = AboutText.replace('\t', ' ')

	return AboutText, AboutLcdText

class About(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Image Information"))
		self.skinName = "AboutOE"
		self.populate()

		self["key_green"] = Button(_("Translations"))
		self["actions"] = ActionMap(["SetupActions", "ColorActions", "TimerEditActions"],
			{
				"cancel": self.close,
				"ok": self.close,
				"log": self.showAboutReleaseNotes,
				"up": self["AboutScrollLabel"].pageUp,
				"down": self["AboutScrollLabel"].pageDown,
				#"green": self.showTranslationInfo,
			})

	def populate(self):
		self["lab1"] = StaticText(_("Developer:\t Javilonas (Javier Sayago)"))
		self["lab2"] = StaticText(_("Support:\t www.lonasdigital.com"))
		model = None

		AboutText = getAboutText()[0]

		self["AboutScrollLabel"] = ScrollLabel(AboutText)

	def showTranslationInfo(self):
		self.session.open(TranslationInfo)

	def showAboutReleaseNotes(self):
		self.session.open(ViewGitLog)

	def createSummary(self):
		return AboutSummary

class Devices(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Device Information"))
		self["TunerHeader"] = StaticText(_("Detected NIMs:"))
		self["HDDHeader"] = StaticText(_("Detected Devices:"))
		self["MountsHeader"] = StaticText(_("Network Servers:"))
		self["nims"] = StaticText()
		for count in (0, 1, 2, 3):
			self["Tuner" + str(count)] = StaticText("")
		self["hdd"] = StaticText()
		self["mounts"] = StaticText()
		self.list = []
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.populate2)
		self["actions"] = ActionMap(["SetupActions", "ColorActions", "TimerEditActions"],
			{
				"cancel": self.close,
				"ok": self.close,
			})
		self.onLayoutFinish.append(self.populate)

	def populate(self):
		self.mountinfo = ''
		self["actions"].setEnabled(False)
		scanning = _("Wait please while scanning for devices...")
		self["nims"].setText(scanning)
		for count in (0, 1, 2, 3):
			self["Tuner" + str(count)].setText(scanning)
		self["hdd"].setText(scanning)
		self['mounts'].setText(scanning)
		self.activityTimer.start(1)

	def populate2(self):
		self.activityTimer.stop()
		self.Console = Console()
		niminfo = ""
		nims = nimmanager.nimList()
		for count in range(len(nims)):
			if niminfo:
				niminfo += "\n"
			niminfo += nims[count]
		self["nims"].setText(niminfo)

		nims = nimmanager.nimList()
		if len(nims) <= 4 :
			for count in (0, 1, 2, 3):
				if count < len(nims):
					self["Tuner" + str(count)].setText(nims[count])
				else:
					self["Tuner" + str(count)].setText("")
		else:
			desc_list = []
			count = 0
			cur_idx = -1
			while count < len(nims):
				data = nims[count].split(":")
				idx = data[0].strip('Tuner').strip()
				desc = data[1].strip()
				if desc_list and desc_list[cur_idx]['desc'] == desc:
					desc_list[cur_idx]['end'] = idx
				else:
					desc_list.append({'desc' : desc, 'start' : idx, 'end' : idx})
					cur_idx += 1
				count += 1

			for count in (0, 1, 2, 3):
				if count < len(desc_list):
					if desc_list[count]['start'] == desc_list[count]['end']:
						text = "Tuner %s: %s" % (desc_list[count]['start'], desc_list[count]['desc'])
					else:
						text = "Tuner %s-%s: %s" % (desc_list[count]['start'], desc_list[count]['end'], desc_list[count]['desc'])
				else:
					text = ""

				self["Tuner" + str(count)].setText(text)

		self.list = []
		list2 = []
		f = open('/proc/partitions', 'r')
		for line in f.readlines():
			parts = line.strip().split()
			if not parts:
				continue
			device = parts[3]
			if not search('[a-z][1-9]', device):
				continue
			if device in list2:
				continue

			mount = '/dev/' + device
			f = open('/proc/mounts', 'r')
			for line in f.readlines():
				if device in line:
					parts = line.strip().split()
					mount = str(parts[1])
					break
			f.close()

			if not mount.startswith('/dev/'):
				size = Harddisk(device).diskSize()
				free = Harddisk(device).free()

				if ((float(size) / 1024) / 1024) >= 1:
					sizeline = _("Size: ") + str(round(((float(size) / 1024) / 1024), 2)) + _("TB")
				elif (size / 1024) >= 1:
					sizeline = _("Size: ") + str(round((float(size) / 1024), 2)) + _("GB")
				elif size >= 1:
					sizeline = _("Size: ") + str(size) + _("MB")
				else:
					sizeline = _("Size: ") + _("unavailable")

				if ((float(free) / 1024) / 1024) >= 1:
					freeline = _("Free: ") + str(round(((float(free) / 1024) / 1024), 2)) + _("TB")
				elif (free / 1024) >= 1:
					freeline = _("Free: ") + str(round((float(free) / 1024), 2)) + _("GB")
				elif free >= 1:
					freeline = _("Free: ") + str(free) + _("MB")
				else:
					freeline = _("Free: ") + _("full")
				self.list.append(mount + '\t' + sizeline + ' \t' + freeline)
#			else:
#				self.list.append(mount + '\t' + _('Not mounted'))
# A hdd/usb/mmc is not displayed until it is mapped.

			list2.append(device)
		self.list = '\n'.join(self.list)
		self["hdd"].setText(self.list)

		self.Console.ePopen("df -mh | grep -v '^Filesystem'", self.Stage1Complete)

	def Stage1Complete(self, result, retval, extra_args=None):
		result = result.replace('\n                        ', ' ').split('\n')
		self.mountinfo = ""
		for line in result:
			self.parts = line.split()
			if line and self.parts[0] and (self.parts[0].startswith('192') or self.parts[0].startswith('//192')):
				line = line.split()
				try:
					ipaddress = line[0]
				except:
					ipaddress = ""
				try:
					mounttotal = line[1]
				except:
					mounttotal = ""
				try:
					mountfree = line[3]
				except:
					mountfree = ""
				if self.mountinfo:
					self.mountinfo += "\n"
				self.mountinfo += "%s (%sB, %sB %s)" % (ipaddress, mounttotal, mountfree, _("free"))

		if self.mountinfo:
			self["mounts"].setText(self.mountinfo)
		else:
			self["mounts"].setText(_('none'))
		self["actions"].setEnabled(True)

	def createSummary(self):
		return AboutSummary

class SystemMemoryInfo(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Memory Information"))
		self.skinName = ["SystemMemoryInfo", "About"]
		self["lab1"] = StaticText(_("INFO RAM / FLASH"))
		self["AboutScrollLabel"] = ScrollLabel()

		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.close,
				"ok": self.close,
			})

		out_lines = file("/proc/meminfo").readlines()
		self.AboutText = _("RAM") + '\n'
		RamTotal = "-"
		RamFree = "-"
		for lidx in range(len(out_lines) - 1):
			tstLine = out_lines[lidx].split()
			if "MemTotal:" in tstLine:
				MemTotal = out_lines[lidx].split()
				self.AboutText += _("Total Memory:") + "\t" + MemTotal[1] + "\n"
			if "MemFree:" in tstLine:
				MemFree = out_lines[lidx].split()
				self.AboutText += _("Free Memory:") + "\t" + MemFree[1] + "\n"
				if config.osd.language.value == 'es_ES':
					self.AboutText += _("Memoria Usada:\t%s") % str(about.getRAMusageString()) + "\n"
				else:
					self.AboutText += _("Memory Usage:\t%s") % str(about.getRAMusageString()) + "\n"
			if "Buffers:" in tstLine:
				Buffers = out_lines[lidx].split()
				self.AboutText += _("Buffers:") + "\t" + Buffers[1] + "\n"
			if "Cached:" in tstLine:
				Cached = out_lines[lidx].split()
				self.AboutText += _("Cached:") + "\t" + Cached[1] + "\n"
			if "SwapTotal:" in tstLine:
				SwapTotal = out_lines[lidx].split()
				self.AboutText += _("Total Swap:") + "\t" + SwapTotal[1] + "\n"
			if "SwapFree:" in tstLine:
				SwapFree = out_lines[lidx].split()
				self.AboutText += _("Free Swap:") + "\t" + SwapFree[1] + "\n\n"

		self["actions"].setEnabled(False)
		self.Console = Console()
		self.Console.ePopen("df -mh / | grep -v '^Filesystem'", self.Stage1Complete)

	def Stage1Complete(self, result, retval, extra_args=None):
		flash = str(result).replace('\n', '')
		flash = flash.split()
		FlashTotal = flash[1]
		FlashFree = flash[3]
		FlashUsed = flash[2]
		FlashUse = flash[4]

		self.AboutText += _("FLASH") + '\n'
		self.AboutText += _("Total:") + "\t" + FlashTotal + "\n"
		self.AboutText += _("Free:") + "\t" + FlashFree + "\n"
		self.AboutText += _("Used:") + "\t" + FlashUsed + ' (' + FlashUse + ')'"\n\n"

		self["AboutScrollLabel"].setText(self.AboutText)
		self["actions"].setEnabled(True)

	def createSummary(self):
		return AboutSummary

class SystemNetworkInfo(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Network Information"))
		self.skinName = ["SystemNetworkInfo", "WlanStatus"]
		self["LabelBSSID"] = StaticText()
		self["LabelESSID"] = StaticText()
		self["LabelQuality"] = StaticText()
		self["LabelSignal"] = StaticText()
		self["LabelBitrate"] = StaticText()
		self["LabelEnc"] = StaticText()
		self["BSSID"] = StaticText()
		self["ESSID"] = StaticText()
		self["quality"] = StaticText()
		self["signal"] = StaticText()
		self["bitrate"] = StaticText()
		self["enc"] = StaticText()

		self["IFtext"] = StaticText()
		self["IF"] = StaticText()
		self["Statustext"] = StaticText()
		self["statuspic"] = MultiPixmap()
		self["statuspic"].setPixmapNum(1)
		self["statuspic"].show()

		self.iface = None
		self.createscreen()
		self.iStatus = None

		if iNetwork.isWirelessInterface(self.iface):
			try:
				from Plugins.SystemPlugins.WirelessLan.Wlan import iStatus
				self.iStatus = iStatus
			except:
				pass
			self.resetList()
			self.onClose.append(self.cleanup)
		self.updateStatusbar()

		self["key_red"] = StaticText(_("Close"))

		self["actions"] = ActionMap(["SetupActions", "ColorActions", "DirectionActions"],
			{
				"cancel": self.close,
				"ok": self.close,
				"up": self["AboutScrollLabel"].pageUp,
				"down": self["AboutScrollLabel"].pageDown
			})

	def createscreen(self):
		self.AboutText = ""
		self.iface = "eth0"
		eth0 = about.getIfConfig('eth0')
		if eth0.has_key('addr'):
			if eth0.has_key('ifname'):
				self.AboutText += _('Interface:\t/dev/' + eth0['ifname'] + "\n")
			self.AboutText += _("IP:") + "\t" + eth0['addr'] + "\n"
			if eth0.has_key('netmask'):
				self.AboutText += _("Netmask:") + "\t" + eth0['netmask'] + "\n"
			if eth0.has_key('brdaddr'):
				self.AboutText += _('Broadcast:\t' + eth0['brdaddr'] + "\n")
			if eth0.has_key('hwaddr'):
				self.AboutText += _("MAC:") + "\t" + eth0['hwaddr'] + "\n"
			self.iface = 'eth0'

		eth1 = about.getIfConfig('eth1')
		if eth1.has_key('addr'):
			if eth1.has_key('ifname'):
				self.AboutText += _('Interface:\t/dev/' + eth1['ifname'] + "\n")
			self.AboutText += _("IP:") + "\t" + eth1['addr'] + "\n"
			if eth1.has_key('netmask'):
				self.AboutText += _("Netmask:") + "\t" + eth1['netmask'] + "\n"
			if eth1.has_key('brdaddr'):
				self.AboutText += _('Broadcast:\t' + eth1['brdaddr'] + "\n")
			if eth1.has_key('hwaddr'):
				self.AboutText += _("MAC:") + "\t" + eth1['hwaddr'] + "\n"
			self.iface = 'eth1'

		ra0 = about.getIfConfig('ra0')
		if ra0.has_key('addr'):
			if ra0.has_key('ifname'):
				self.AboutText += _('Interface:\t/dev/' + ra0['ifname'] + "\n")
			self.AboutText += _("IP:") + "\t" + ra0['addr'] + "\n"
			if ra0.has_key('netmask'):
				self.AboutText += _("Netmask:") + "\t" + ra0['netmask'] + "\n"
			if ra0.has_key('brdaddr'):
				self.AboutText += _('Broadcast:\t' + ra0['brdaddr'] + "\n")
			if ra0.has_key('hwaddr'):
				self.AboutText += _("MAC:") + "\t" + ra0['hwaddr'] + "\n"
			self.iface = 'ra0'

		wlan0 = about.getIfConfig('wlan0')
		if wlan0.has_key('addr'):
			if wlan0.has_key('ifname'):
				self.AboutText += _('Interface:\t/dev/' + wlan0['ifname'] + "\n")
			self.AboutText += _("IP:") + "\t" + wlan0['addr'] + "\n"
			if wlan0.has_key('netmask'):
				self.AboutText += _("Netmask:") + "\t" + wlan0['netmask'] + "\n"
			if wlan0.has_key('brdaddr'):
				self.AboutText += _('Broadcast:\t' + wlan0['brdaddr'] + "\n")
			if wlan0.has_key('hwaddr'):
				self.AboutText += _("MAC:") + "\t" + wlan0['hwaddr'] + "\n"
			self.iface = 'wlan0'

		rx_bytes, tx_bytes = about.getIfTransferredData(self.iface)
		self.AboutText += "\n" + _("Bytes received:") + "\t" + rx_bytes + '  (~'  + str(int(rx_bytes)/1024/1024)  + ' MB)'  + "\n"
		self.AboutText += _("Bytes sent:") + "\t" + tx_bytes + '  (~'  + str(int(tx_bytes)/1024/1024)+ ' MB)'  + "\n"

		hostname = file('/proc/sys/kernel/hostname').read()
		self.AboutText += "\n" + _("Hostname:") + "\t" + hostname + "\n"
		self["AboutScrollLabel"] = ScrollLabel(self.AboutText)

	def cleanup(self):
		if self.iStatus:
			self.iStatus.stopWlanConsole()

	def resetList(self):
		if self.iStatus:
			self.iStatus.getDataForInterface(self.iface, self.getInfoCB)

	def getInfoCB(self, data, status):
		self.LinkState = None
		if data is not None:
			if data is True:
				if status is not None:
					if self.iface == 'wlan0' or self.iface == 'ra0':
						if status[self.iface]["essid"] == "off":
							essid = _("No Connection")
						else:
							essid = str(status[self.iface]["essid"])
						if status[self.iface]["accesspoint"] == "Not-Associated":
							accesspoint = _("Not-Associated")
							essid = _("No Connection")
						else:
							accesspoint = str(status[self.iface]["accesspoint"])
						if self.has_key("BSSID"):
							self.AboutText += _('Accesspoint:') + '\t' + accesspoint + '\n'
						if self.has_key("ESSID"):
							self.AboutText += _('SSID:') + '\t' + essid + '\n'

						quality = str(status[self.iface]["quality"])
						if self.has_key("quality"):
							self.AboutText += _('Link Quality:') + '\t' + quality + '\n'

						if status[self.iface]["bitrate"] == '0':
							bitrate = _("Unsupported")
						else:
							bitrate = str(status[self.iface]["bitrate"]) + " Mb/s"
						if self.has_key("bitrate"):
							self.AboutText += _('Bitrate:') + '\t' + bitrate + '\n'

						signal = str(status[self.iface]["signal"])
						if self.has_key("signal"):
							self.AboutText += _('Signal Strength:') + '\t' + signal + '\n'

						if status[self.iface]["encryption"] == "off":
							if accesspoint == "Not-Associated":
								encryption = _("Disabled")
							else:
								encryption = _("Unsupported")
						else:
							encryption = _("Enabled")
						if self.has_key("enc"):
							self.AboutText += _('Encryption:') + '\t' + encryption + '\n'

						if status[self.iface]["essid"] == "off" or status[self.iface]["accesspoint"] == "Not-Associated" or status[self.iface]["accesspoint"] is False:
							self.LinkState = False
							self["statuspic"].setPixmapNum(1)
							self["statuspic"].show()
						else:
							self.LinkState = True
							iNetwork.checkNetworkState(self.checkNetworkCB)
						self["AboutScrollLabel"].setText(self.AboutText)

	def exit(self):
		self.close(True)

	def updateStatusbar(self):
		self["IFtext"].setText(_("Network:"))
		self["IF"].setText(iNetwork.getFriendlyAdapterName(self.iface))
		self["Statustext"].setText(_("Link:"))
		if iNetwork.isWirelessInterface(self.iface):
			try:
				self.iStatus.getDataForInterface(self.iface, self.getInfoCB)
			except:
				self["statuspic"].setPixmapNum(1)
				self["statuspic"].show()
		else:
			iNetwork.getLinkState(self.iface, self.dataAvail)

	def dataAvail(self, data):
		self.LinkState = None
		for line in data.splitlines():
			line = line.strip()
			if 'Link detected:' in line:
				if "yes" in line:
					self.LinkState = True
				else:
					self.LinkState = False
		if self.LinkState:
			iNetwork.checkNetworkState(self.checkNetworkCB)
		else:
			self["statuspic"].setPixmapNum(1)
			self["statuspic"].show()

	def checkNetworkCB(self, data):
		try:
			if iNetwork.getAdapterAttribute(self.iface, "up") is True:
				if self.LinkState is True:
					if data <= 2:
						self["statuspic"].setPixmapNum(0)
					else:
						self["statuspic"].setPixmapNum(1)
					self["statuspic"].show()
				else:
					self["statuspic"].setPixmapNum(1)
					self["statuspic"].show()
			else:
				self["statuspic"].setPixmapNum(1)
				self["statuspic"].show()
		except:
			pass

	def createSummary(self):
		return AboutSummary

class AboutSummary(Screen):
	def __init__(self, session, parent):
		Screen.__init__(self, session, parent=parent)
		self["selected"] = StaticText("openLD:" + getImageVersion())

		AboutText = getAboutText()[1]

		self["AboutText"] = StaticText(AboutText)

class ViewGitLog(Screen):
	def __init__(self, session, args=None):
		Screen.__init__(self, session)
		self.skinName = "SoftwareUpdateChanges"
		self.setTitle(_("OE Changes"))
		self.logtype = 'oe'
		self["text"] = ScrollLabel()
		self['title_summary'] = StaticText()
		self['text_summary'] = StaticText()
		self["key_red"] = Button(_("Close"))
		self["key_green"] = Button(_("OK"))
		self["key_yellow"] = Button(_("Show E2 Log"))
		self["myactions"] = ActionMap(['ColorActions', 'OkCancelActions', 'DirectionActions'],
		{
			'cancel': self.closeRecursive,
			'green': self.closeRecursive,
			"red": self.closeRecursive,
			"yellow": self.changelogtype,
			"left": self.pageUp,
			"right": self.pageDown,
			"down": self.pageDown,
			"up": self.pageUp
		},-1)
		self.onLayoutFinish.append(self.getlog)

	def changelogtype(self):
		if self.logtype == 'e2':
			self["key_yellow"].setText(_("Show E2 Log"))
			self.setTitle(_("OE Changes"))
			self.logtype = 'oe'
		else:
			self["key_yellow"].setText(_("Show OE Log"))
			self.setTitle(_("Enigma2 Changes"))
			self.logtype = 'e2'
		self.getlog()

	def pageUp(self):
		self["text"].pageUp()

	def pageDown(self):
		self["text"].pageDown()

	def getlog(self):
		fd = open('/etc/' + self.logtype + '-git.log', 'r')
		releasenotes = fd.read()
		fd.close()
		releasenotes = releasenotes.replace('\nopenld: build', "\n\nopenld: build")
		self["text"].setText(releasenotes)
		summarytext = releasenotes
		try:
			if self.logtype == 'e2':
				self['title_summary'].setText(_("E2 Log"))
				self['text_summary'].setText(_("Enigma2 Changes"))
			else:
				self['title_summary'].setText(_("OE Log"))
				self['text_summary'].setText(_("OE Changes"))
		except:
			self['title_summary'].setText("")
			self['text_summary'].setText("")

	def unattendedupdate(self):
		self.close((_("Unattended upgrade without GUI and reboot system"), "cold"))

	def closeRecursive(self):
		self.close((_("Cancel"), ""))

class TranslationInfo(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Translation Information"))
		# don't remove the string out of the _(), or it can't be "translated" anymore.

		# TRANSLATORS: Add here whatever should be shown in the "translator" about screen, up to 6 lines (use \n for newline)
		info = _("TRANSLATOR_INFO")

		if info == "TRANSLATOR_INFO":
			info = ""

		infolines = _("").split("\n")
		infomap = {}
		for x in infolines:
			l = x.split(': ')
			if len(l) != 2:
				continue
			(type, value) = l
			infomap[type] = value
		print infomap

		self["TranslationInfo"] = StaticText(info)

		translator_name = infomap.get("Language-Team", "none")
		if translator_name == "none":
			translator_name = infomap.get("Last-Translator", "")

		self["TranslatorName"] = StaticText(translator_name)

		self["actions"] = ActionMap(["SetupActions"],
			{
				"cancel": self.close,
				"ok": self.close,
			})
