#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# 
# Copyright (C) 2013  a.atalla <a.atalla@hacari.org>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
import sys
from scapy.all import *

class Scanner:
	def __init__(self):
		pass
	
	def getLiveHosts(self,ip,net):
		try:
			alive,dead=srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip+'/'+net), timeout=2, verbose=0)
			print "MAC - IP"
			for i in range(0,len(alive)):
					print alive[i][1].hwsrc + " - " + alive[i][1].psrc
		except:
			print 'Exception'
			pass

t=Scanner()
t.getLiveHosts('10.100.3.113','24')