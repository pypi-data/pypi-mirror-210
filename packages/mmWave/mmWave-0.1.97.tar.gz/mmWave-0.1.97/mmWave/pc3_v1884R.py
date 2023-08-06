# 3D People Counting-ISK V1884R
# ver:0.0.1
# 2023/01/03
# firware: V1884R
# parsing People Counting 3D fusion  
# hardware:(Batman-201)ISK IWR6843
# 
# company: Joybien Technologies: www.joybien.com
# author: Zach Chen
#===========================================
# output: v1010,v1011,v1012,v1020,v1021 Raw data
# v0.0.1 : 2023/01/05 release
#          (1)Output list data
# v0.0.2 : 2023/04/07 add try...except
#

import serial
import time
import struct
import numpy as np
import pandas as pd


class header:
	version = 0
	totalPackLen = 0
	platform = 0
	frameNumber = 0
	timeCpuCycles = 0
	numDetectedObj = 0
	numTLVs = 0
	subframeNumber = 0

class unitS:
	elevationUnit:float = 0.0
	azimuthUnit : float = 0.0
	dopplerUnit : float = 0.0
	rangeUnit :   float = 0.0
	snrUnit :     float = 0.0

class pc3_v1884R:
	gdata = b''
	playback = False
	#magicWord =  [b'\x02',b'\x01',b'\x04',b'\x03',b'\x06',b'\x05',b'\x08',b'\x07',b'\0x99']
	magicWord =  [b'\x01',b'\x02',b'\x03',b'\x04',b'\x05',b'\x06',b'\x07',b'\x08',b'\0x99']
	port = ""
	hdr = header
	u = unitS
	frameNumber = 0
	# provide csv file dataframe
	# real-time 
	v1020_names_rt = ['fN','sx','sy','sz','ran','elv','azi','dop','snr','fn']
	v1010_col_names_rt = ['fN','type','posX','posY','posZ','velX','velY','velZ','accX','accY','accZ','ec0','ec1','ec2','ec3','ec4','ec5','ec6','ec7','ec8','ec9','ec10','ec11','ec12','ec13','ec14','ec15','g','confi','tid']                    
	 
	# read from file for trace point clouds
	fileName = ''
	v1020_col_names = ['time','fN','type','sx','sy','sz','ran','elv','azi', 'dop', 'snr','fn']
	
	
	v1010_col_names = ['time','fN','type','tid','posX','posY','posZ','velX','velY','velZ','accX','accY','accZ','ec0','ec1','ec2','ec3','ec4','ec5','ec6','ec7','ec8','ec9','ec10','ec11','ec12','ec13','ec14','ec15','g','confi']
	 
	v1020simo = []
	
	sim_startFN = 0
	sim_stopFN  = 0 
	JB_t0 = 0
	version_keep = '3050004'
	
	# add for interal use
	tlvLength = 0
	numOfPoints = 0
	# for debug use 
	dbg = False #Packet unpacket Check: True show message 
	sm  = False #Observed StateMachine: True Show message
	plen = 16 
	
	def __init__(self,port, azi_degree = None, bufSize = None):
		
		port.reset_input_buffer()
		port.ReadBufferSize = bufSize
		self.degree = azi_degree
		self.port = port
		self.azi_offset = 0.0 if azi_degree == None else azi_degree * np.pi/180.0
		print("(jb)People Counting 3D initial")
		print("(jb)version:v0.1.0")
		print("(jb)For Hardware:Batman-201(ISK)/AOP(501/601)")
		print("(jb)Firmware: PC3")
		print("(jb)UART Baud Rate:921600")
		print("Output: (dck,v1010,v1011,v1012,v1020,v1021) (RAW data)\n##########################################\n\n\n")
		
	def useDebug(self,ft):
		self.dbg = ft
		
	def stateMachine(self,ft):
		self.sm = ft
		
	def getHeader(self):
		return self.hdr
		
	def headerShow(self):
		print("***header***********") 
		print("Version:     \t%x "%(self.hdr.version))
		print("TotalPackLen:\t%d "%(self.hdr.totalPackLen))
		print("Platform:    \t%X "%(self.hdr.platform))
		print("PID(frame#): \t%d "%(self.hdr.frameNumber))
		print("CPU cycles Time:\t{:d} us".format(self.hdr.timeCpuCycles))
		print("Number of Detected Object: \t%d "%(self.hdr.numDetectedObj))
		print("numTLVs:     \t%d "%(self.hdr.numTLVs))
		print("subframe#  : \t%d "%(self.hdr.subframeNumber))
		print("***End Of Header***") 
		
#################################################################
	JB_syncFlag = 0
	def jb_getUartBuf(self,disp = None):
		idx = 0
		buf = b""
		self.gdata = b''
		while True:
			if self.JB_syncFlag == 0:
				ch = self.port.read() # here ch type is byte
				if ch == self.magicWord[idx]: # 0..7
					buf += ch
					idx += 1 # 1..8
					if idx == 8:
						idx = 8
						self.JB_syncFlag = 1
						self.JB_t0 = time.time()
			else:
				self.JB_syncFlag = 0 # magic word ch mismatch loop back again
				idx = 0 # init
				buf = b""
				self.gdata = b''
			

			if self.JB_syncFlag == 1:
				# read next 16 bytes for v, l, p, f
				for i in range(32):
					ch = self.port.read()
					buf += ch
					self.gdata = buf

				if len(buf) == (32+8): # magic+header
					try:
						(self.hdr.version,self.hdr.totalPackLen,self.hdr.platform,self.hdr.frameNumber,
						self.hdr.timeCpuCycles,self.hdr.numDetectedObj,self.hdr.numTLVs,self.hdr.subFrameNumber) = struct.unpack('8I',buf[8:40]) 
						self.frameNumber = self.hdr.frameNumber
						verString = "{:X}".format(self.hdr.version)
						totalLen = self.hdr.totalPackLen
					except:
						if self.dbg == True:
							print("unpack except:")
						return False
						
					if disp:
						self.headerShow()
					
					if self.playback == True:
						return False
					
					if verString != self.version_keep or self.hdr.totalPackLen > 100000:
						print("ver: {:}   version_keep:{:}".format(verString,self.version_keep ))
						return False

				else:
					self.JB_syncFlag = 0 # len mismatch loop back again
					idx = 0
					buf = b''
					self.gdata = b''

			if self.JB_syncFlag == 1:
				r = self.port.read(totalLen - 40) # read rest of bytes
				#xx = self.port.inWaiting()
				#print("is Wating= {:}  :len:{:}".format(0,len(r)))
				#buf += r
				self.gdata += r
				dt = time.time()- self.JB_t0
				#self.port.flushInput()
				self.port.reset_input_buffer()
				 
				#print(f"==== gdata_len: {len(self.gdata)}" )
				if totalLen  == len(self.gdata):
					#print(f"====eq gdata_len: {len(self.gdata)}" )
					return True
				else:
					self.JB_syncFlag = 0 # len mismatch loop back again
					idx = 0
					buf = b""
					self.gdata = b''
					
#################################################################
#
# TLV: Type-Length-Value
# read TLV data
# input:
#     disp: True:print message
#			False: hide printing message
#     df: 
# output:(return parameter)
#  (dck,v1010,v1011,v1012,v1020,v1021) = radar.tlvRead(False)
#  dck: True: Data available    False: Data not available
#
#	v1010 =([]) #target
#	v1011 =([]) #target index
#	v1012 =([]) #target height
#	v1020 =([]) #point  cloud
#	v1021 =([]) #Prescence Indication
#
#================================================================
	 
	def tlvRead(self,disp):
		global JB_tOld 
		 
		#print("---tlvRead---")
		#ds = dos
		typeList = ['1010','1011','1012','1020','1021']
		idx = 0
		lstate = 'idle'
		sbuf = b''
		lenCount = 0
		 
		dataBytes = 0
		numOfPoints = 0
		tlvCount = 0
		 
		v1010 =([]) #target
		v1011 =([]) #target index
		v1012 =([]) #target height
		v1020 =([]) #point cloud
		v1021 =([]) #Prescence Indication
		
		ch = b'\x00' # init
		idxTo = 0
		uartBuf = b''
		 
		while True:
			###############################
			# on {idle} getUartBuf() else parsing from uartBuf[]
			if lstate == 'idle':
				chk = self.jb_getUartBuf(disp=disp)
				if chk == True:
					uartBuf = self.gdata
					tlvCount = self.hdr.numTLVs
				else:
					#print("===========================tlvRead=========================buf empty" )
					return (False,v1010,v1011,v1012,v1020,v1021)
					
				lstate = 'TL'
				sbuf = b"" # init
				idxFrom = 0
				idxTo = 40  #header 32 + 8(magic word) = 40
				
				if self.sm:
					print("===============================")
					print(f"JB> (idle)->(TL):    numTLVs(tlvCount):{tlvCount}")
				
				
			elif lstate == 'TL': #TLV Header type/length
				idxFrom = idxTo 
				idxTo += 8
				try:
					ttype, self.tlvLength = struct.unpack('2I', uartBuf[idxFrom : idxTo])
				except:
					if self.dbg == True:
						print("Header unpack except")
					return (False,v1010,v1011,v1012,v1020,v1021)
						
				if self.sm:
					print(f"JB> (TL)->({ttype}) indexFrom:idxTo= {idxFrom}:{idxTo}  type:{ttype} tlvLength:{self.tlvLength}")
				lstate = str(ttype)
			
			elif lstate == '1020': # count = Total Lentgh - 8   # eadrs: 8 bytes
				
				(points,dataBytes) = self.points_cal(dataBytes = 8, offset = 20) 
				datalen = self.tlvLength - 20 # tlv(8 bytes) units(4x5=20 bytes)
				 
				
				#print("JB> (1020) points: {:}    datalen:{:}  idxTo:{:}".format(points,datalen,idxTo))
				#(0) unit unpack
				idxFrom = idxTo
				idxTo += 20
				try:
					self.u.elevationUnit,self.u.azimuthUnit,self.u.dopplerUnit,self.u.rangeUnit,self.u.snrUnit = struct.unpack('5f', uartBuf[idxFrom : idxTo])
				except:
					if self.dbg == True:
						print("Header unpack except")
					return (False,v1010,v1011,v1012,v1020,v1021)
				#print("JB> (1020-unit)  ==> elv:{:.4f} azimuth:{:.4f} doppler:{:.4f} range:{:.4f} snr:{:.4f}".format(self.u.elevationUnit,self.u.azimuthUnit,self.u.dopplerUnit,self.u.rangeUnit,self.u.snrUnit))
				
				#(1) reads unpack
				idxFrom = idxTo
				idxTo += datalen
				
				#sbuf = uartBuf[idxFrom : idxTo]
				for i in range(points):
					try: 
						(e,a,d,r,s) = struct.unpack('2bh2H', uartBuf[idxFrom + i*dataBytes : idxFrom + (i + 1)*dataBytes]) #8bytes
						elv = e * self.u.elevationUnit
						azi = a * self.u.azimuthUnit  + self.azi_offset
						dop = d * self.u.dopplerUnit
						ran = r * self.u.rangeUnit
						snr = s * self.u.snrUnit
						sz  = ran * np.sin(elv)
						sx  = ran * np.cos(elv) * np.sin(azi)
						sy  = ran * np.cos(elv) * np.cos(azi) 
						
						#print("({:}:{:4d})(idx:({:4d}) elv:{:.4f} azimuth:{:.4f} doppler:{:.4f} range:{:.4f} snr:{:.4f}".format(points,lenCount,i,elv,azi,dop,ran,snr))
						v1020.append((sx,sy,sz,ran,elv,azi,dop,snr,self.hdr.frameNumber)) #xyzreadsf
						
					except:
						if self.dbg == True:
							print("(1020)Improper Type 1020 Value structure found: ")
						return (False,v1010,v1011,v1012,v1020,v1021)
				 
				(chk,lstate,tlvCount) = self.idle_tl_check(tlvCount = tlvCount,state= lstate)
				if chk:
					return (True,v1010,v1011,v1012,v1020,v1021)
				
						
			elif lstate == '1010': # Target list
				(points,dataBytes) = self.points_cal(dataBytes=112,offset=0) #112 = 4 + 9 * 4 + 18 *4 
				idxFrom = idxTo
				idxTo += self.tlvLength #    datalen
				#print("JB> (1010) points: {:}    datalen:{:}  idxTo:{:}".format(points,self.tlvLength,idxTo))
				#print("JB> (1010) idxFrom: {:}  idxTo:{:}".format(idxFrom,idxTo))
				
				for i in range(points):
					try:
						 
						(tid,posX,posY,posZ,velX,velY,velZ,accX,accY,accZ,ec0,ec1,ec2,
						ec3,ec4,ec5,ec6,ec7,ec8,ec9,ec10,ec11,ec12,ec13,ec14,ec15,g,confi) = struct.unpack('I27f', uartBuf[idxFrom + i*dataBytes : idxFrom + (i + 1)*dataBytes])
						
						#posX, posY = rotate_matrix(pX, pY, self.azi_offset  , x_shift=0, y_shift=0, units="RADIAN")  
						#print(f'JB>(1010) point({i}) tid:{tid} posX:{posX} posY:{posY} posZ:{posZ} ')
						v1010.append((tid,posX,posY,posZ,velX,velY,velZ,accX,accY,accZ,ec0,ec1,ec2,ec3,ec4,ec5,ec6,ec7,ec8,ec9,ec10,ec11,ec12,ec13,ec14,ec15,g,confi))
							
					except:
						if self.dbg == True:
							print("(7)Improper Type 1010 Value structure found: ")
						return (False,v1010,v1011,v1012,v1020,v1021)
				
				(chk,lstate,tlvCount) = self.idle_tl_check(tlvCount = tlvCount,state= lstate)
				if chk:
					return (True,v1010,v1011,v1012,v1020,v1021)
				
			
			elif lstate == '1011': #Target Index
				(points,dataBytes) = self.points_cal(dataBytes=1,offset=0)
				idxFrom = idxTo
				idxTo += self.tlvLength
				#print(f'(v1011) type:{ttype} length:{self.tlvLength} ')
				try:
					for i in range(points):
						tidx = struct.unpack('B', uartBuf[idxFrom + i*dataBytes : idxFrom + (i + 1)*dataBytes])
						#print(f'JB>(1011) point({i}) tidx:{tidx}')
						v1011.append(tidx)
				except:
					if self.dbg == True:
						print("(8)Improper Type 1011 Value structure found: ")
					return (False,v1010,v1011,v1012,v1020,v1021)
				 
				(chk,lstate,tlvCount) = self.idle_tl_check(tlvCount = tlvCount,state= lstate)
				if chk:
					return (True,v1010,v1011,v1012,v1020,v1021)
				
			
			elif lstate == '1012': #Target Height
				(points,dataBytes) = self.points_cal(dataBytes=12,offset=0)
				
				idxFrom = idxTo
				idxTo += self.tlvLength
				#print(f'(v1012) type:{ttype} length:{self.tlvLength} ')
				try:
					for i in range(points):
						(tid,maxZ,minZ) = struct.unpack('I2f', uartBuf[idxFrom + i*dataBytes : idxFrom + (i + 1)*dataBytes])
						#print(f'JB>(1012) point({i}) tid:{tid} minZ:{minZ} maxZ:{maxZ}  ')
						v1012.append((tid,maxZ,minZ))
				except:
					if self.dbg == True:
						print("(9)Improper Type 1012 Value structure found: ")
					return (False,v1010,v1011,v1012,v1020,v1021)
				 
				(chk,lstate,tlvCount) = self.idle_tl_check(tlvCount = tlvCount,state= lstate)
				if chk:
					return (True,v1010,v1011,v1012,v1020,v1021)
				
				 
					
			elif lstate == '1021': #Prescence Indication
				(points,dataBytes) = self.points_cal(dataBytes=4,offset=0)
				idxFrom = idxTo
				idxTo += self.tlvLength
			
				#print(f'(v1021) type:{ttype} length:{self.tlvLength} ')
				try:
					for i in range(points):
						pri = struct.unpack('I', uartBuf[idxFrom + i*dataBytes : idxFrom + (i + 1)*dataBytes])
						v1012.append(pri)
				except:
					if self.dbg == True:
						print("(10)Improper Type 1021 Value structure found: ")
					return (False,v1010,v1011,v1012,v1020,v1021)
				
				(chk,lstate,tlvCount) = self.idle_tl_check(tlvCount = tlvCount,state= lstate)
				if chk:
					return (True,v1010,v1011,v1012,v1020,v1021)
				
			else:
				lstat = 'idle'
				#print("===============state error====================")
				return (False,v1010,v1011,v1012,v1020,v1021)
					
	def points_cal(self,dataBytes= None,offset = None): 
		datalen = self.tlvLength - offset
		points = int(datalen/dataBytes)
		return (points,dataBytes)
		
	def idle_tl_check(self,tlvCount = None,state= None,points = None):
		chk = False
		tlvCount -= 1
		if tlvCount == 0:
			if self.sm == True:
				print(f"JB> ({state})->(idle)   tlvCount:{tlvCount}")
			state = 'idle'
			chk = True
			
		else:
			if self.sm == True:
				print(f"JB> ({state})->(TL)  tlvCount:{tlvCount}")
			state = 'TL'
		
		return (chk,state,tlvCount)
		

	def rotate_matrix(self,x, y, angle, x_shift=0, y_shift=0, units="DEGREES"):
		# Shift to origin (0,0)
		x = x - x_shift
		y = y - y_shift
		
		# Convert degrees to radians
		if units == "DEGREES":
			angle = np.radians(angle)

		# Rotation matrix multiplication to get rotated x & y
		xr = (x * np.cos(angle)) - (y * np.sin(angle)) + x_shift
		yr = (x * np.sin(angle)) + (y * np.cos(angle)) + y_shift
		return xr, yr



		
	def getRecordData(self,frameNum):
		s_fn = frameNum +  self.sim_startFN
		print(" s_fn:({:})  = frameNum:{:} + sim_startFN: {:}      ".format(s_fn,frameNum,self.sim_startFN))
		v20d = self.v1020simo[self.v1020simo['fn'] == s_fn]
		 
		print(v20d)
		chk = 0
		if v20d.count != 0:
			chk = 1
		return (chk,v20d)
		
	
		
	def readFile(self,fileName):
		#fileName = "pc32021-03-19-10-02-17.csv"  
		#df = pd.read_csv(fileName, error_bad_lines=False, warn_bad_lines=False) 
		self.fileName = fileName 
		#          ['time','fN','type','elv','azimuth','range' ,'doppler','snr','sx', 'sy', 'sz']
		df = pd.read_csv(self.fileName, names = self.v1020_col_names,skiprows = [0]) 
		df.dropna()
		#print("------------------- df --------------------shape:{:}".format(df.shape))
		
		print(df.info())
		print(df.info(memory_usage="deep")) 
		
		
		
		v1020simori = df[(df.type == 'v1020')]
		print("=============v1020simori=================")
		print(v1020simori)
		print("=============v1020simori=  xxx================")
		self.sim_startFN = df['fN'].values[0]
		self.sim_stopFN  = df['fN'].values[-1]
		
		print(f"sim_start: {self.sim_startFN} sim_stop: {self.sim_stopFN}")
		
		#print("-------------------v1020simo------------:{:}".format(v1020simori.shape))
		
		self.v1020simo = v1020simori.loc[:,['sx', 'sy', 'sz','ran' ,'elv','azi','dop','snr','fn']] # in this case
		#self.v1020simo['fn'] = self.v1020simo['fn'].astype(int, errors = 'raise') 
		
		#print(self.v1020simo)
		#print("-------------------v1020simo--------  end  ---------")
		
		 
		df10 = pd.read_csv(self.fileName, names = self.v1010_col_names, skiprows = [0])  
		
		#------------- v1010 sim ---------------
		v1010simc = df10[df10['type'] == 'v1010']
		self.v1010simo  = v1010simc.loc[:,['fN','type','posX','posY','posZ','velX','velY','velZ','accX','accY','accZ','tid']]
		self.v1010simo['posX'] = self.v1010simo['posX'].astype(float, errors = 'raise') 
		
		
		#------------- v8 sim ---------------
		v8simc = df[df['type'] == 'v8']
		self.v8simo  = v8simc.loc[:,['fN','type','elv']]
		self.v8simo.columns = ['fN','type','targetID']
		
		#print(self.v8simo)
		return (self.v1020simo,self.v1010simo) #,self.v8simo)
		 
		 




