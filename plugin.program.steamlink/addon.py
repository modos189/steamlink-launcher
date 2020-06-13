#!/usr/bin/python3

import os
import platform
import requests
import shutil
import stat
import subprocess
import tarfile
import tempfile
##import xmbcaddon
from urllib.request import urlretrieve

##addon_dir = xbmcaddon.Addon().getAddonInfo("path")
addon_dir = "/home/user/Downloads/ADDON"
version_file = os.path.join(os.path.join(addon_dir, "steamlink"), "version.txt")

# Detect operatiing system
def GetOS():
	with open("/etc/os-release") as os_release:
		for line in os_release:
			if line.startswith("NAME="):
				value = line.split("=",)[1]
				os_string = value.split("\"")[1]
				return os_string

	# If "NAME=" wasn't found in /etc/os-release, return "unknown"
	return "unknown"

# Installation on LibreELEC
def LibreELECInstall():
	# Remove installaton directory if already present
	shutil.rmtree(os.path.join(addon_dir, "steamlink"), ignore_errors=True)

	# Copy required libraries
	lib_source = os.path.join(os.path.join(addon_dir, "resources"), "lib") # ADDON/resources/lib
	lib_target = os.path.join(os.path.join(addon_dir, "steamlink"), "lib") # ADDON/steamlink/lib
	print("Symlinking required libraries from " + lib_source + " to " + lib_target + ".")
	os.makedirs(lib_target)
	# libjpeg.so.62.2.0 > libjpeg.so.62
	os.symlink(os.path.join(lib_source, "libjpeg.so.62.2.0"),   os.path.join(lib_target, "libjpeg.so.62"))
	# libpng16.so.16.36.0 -> libpng16.so.16
	os.symlink(os.path.join(lib_source, "libpng16.so.16.36.0"), os.path.join(lib_target, "libpng16.so.16"))
	# libX11-xcb.so.1.0.0
	os.symlink(os.path.join(lib_source, "libX11-xcb.so.1.0.0"), os.path.join(lib_target, "libX11-xcb.so.1.0.0"))
	# libX11.so.6.3.0
	os.symlink(os.path.join(lib_source, "libX11.so.6.3.0"),     os.path.join(lib_target, "libX11.so.6.3.0"))
	# libXext.so.6.4.0
	os.symlink(os.path.join(lib_source, "libXext.so.6.4.0"),    os.path.join(lib_target, "libXext.so.6.4.0"))

	# Make start script executable
	start_sh_name = "start.sh"
	start_sh = os.path.join(os.path.join(addon_dir, "resources"), start_sh_name)
	mode = os.stat(start_sh).st_mode
	os.chmod(start_sh, mode | stat.S_IEXEC)
	
	# Get download link and download path
	link = "http://media.steampowered.com/steamlink/rpi/public_build.txt"
	download_link = requests.get(link).text.split("\n")[0]
	steamlink_version = download_link.split("http://media.steampowered.com/steamlink/rpi/steamlink-rpi3-",1)[1].split(".tar.gz")[0]
	tarball_name = "steamlink-rpi3-" + steamlink_version + ".tar.gz"
	tarball_path = os.path.join(tempfile.mkdtemp(), tarball_name)

	# Download .tar.gz to temporary directory
	print("Downloading Steam Link.")
	urlretrieve(download_link, tarball_path)

	# Extract .tar.gz
	print("Extracting Steam Link archive.")
	tarfile.open(tarball_path).extractall(path=addon_dir)

	# Symlinking systemd service file
	service_file_name = "steamlink.service"
	service_file_source = os.path.join(os.path.join(addon_dir, "resources"), service_file_name) # ADDON/resources/steamlink.sh
	# /usr/lib/systemd/system/ ?
	##service_file_target = "/storage/.config/system.d/" + service_file_name # TODO: Get systemd path from OS?
	service_file_target = addon_dir + os.path.sep + service_file_name
	if not os.path.isfile(service_file_target):
		os.symlink(service_file_source, service_file_target)

	# Enable systemd service
	subprocess.run(["systemctl", "enable", "steamlink.service"])

def LibreELECStart():
	print("Starting Steam Link.")
	subprocess.run(["systemctl", "start", "steamlink.service"])

def LibreELEC():
	# Detect installation
	if not os.path.isfile(version_file):
		print("Installation not found. Installing.")
		LibreELECInstall()
	else:
		print("Installation found. Checking version.")
		# Compare versions and install if online version differs from local one
		link = "http://media.steampowered.com/steamlink/rpi/public_build.txt"
		download_link = requests.get(link).text.split("\n")[0]
		steamlink_version = download_link.split("http://media.steampowered.com/steamlink/rpi/steamlink-rpi3-",1)[1].split(".tar.gz")[0]

		with open(version_file) as vf:
			for line in vf:
				if line.split("\n")[0] != steamlink_version:
					print("Newer version found. Installing.")
					LibreELECInstall()
				else:
					print("Current version already installed. Skipping installation.")
				break # Version file should always be a single line

	LibreELECStart()

# Installation on OSMC
def OSMCInstall():
	print("TODO")

def OSMCStart():
	print("TODO")

def OSMC():
	print("TODO")

# Main
def Main():
	# Check architecture
	if not platform.machine().startswith("arm"):
		print("Architecture not supported. Exiting.")
		##exit(1)

	# "switch"
	name = GetOS()
	if   name == "LibreELEC":
		LibreELEC()
	elif name == "OSMC":
		OSMC()
	elif name == "unknown":
		print("Was not able to detect operating system. Exiting.")
		exit(1)
	else:
		##print("Operating system not supported. Exiting.")
		##exit(1)
		LibreELEC()


Main()
