# Medium Range Radar Raw Data (MRR)
# ver:0.0.1
# 2021/12/31
# parsing Medium Range Radar
# hardware:(Batman-601):  
# company: Joybien Technologies: www.joybien.com
# author: Zach Chen
#===========================================
# output: V1,V2,V3,v4 Raw data
# v0.0.1 : 2021/12/31 release
# v0.0.2 : 2022/02/07 format revised
# v0.1.0 : 2022/06/01 tune to fit v3
# v1.0.0 : 2022/06/08 change get Uart method
# v1.0.1 : 2022/06/09 added headerShowAll()
# v1.0.2 : 2023/03/24 header enable/disable in inital
#         class MRR:  def __init__(self,port,show = True):

import serial
import time
import struct
import pandas as pd
import numpy as np

class header:
	version = 0
	totalPackLen = 0
	platform = 0
	frameNumber = 0
	cpuProcessTime = 0
	numOBJs = 0
	numTLVs = 0
	subFrameNumber = 0

class byteInfo:
	headerByte = 32


class MRR:
    
	magicWord =  [b'\x01',b'\x02',b'\x03',b'\x04',b'\x05',b'\x06',b'\x07',b'\x08',b'\0x99']
	magicLen = 8
	port = ''
	hdr = header
	hdr0 = header()
	hdr1 = header()
	info = byteInfo
	hdrA = [hdr0,hdr1]
	headerDic = {0:hdr0, 1:hdr1}
	
	clearQBuf = True
	# provide csv file dataframe
	# real-time 
	v1_col_names_rt = ['fN','type','doppler','peakVal','X' ,'Y','Z']  
	v2_col_names_rt = ['fN','type','ccX','ccY','csX','csY']
	v3_col_names_rt = ['fN','type', 'tX','tY','velX','velY','csX','csY']
	v4_col_names_rt = ['fN','type','parkingA']  
	
	# read from file for trace point clouds
	fileName = ''
	v1_col_names = ['time','fN','type','doppler','peakVal','X' ,'Y','Z']
	v2_col_names = ['time','fN','type','ccX','ccY','csX','csY']
	v3_col_names = ['time','fN','type', 'tX','tY','velX','velY','csX','csY']
	v4_col_names = ['time','fN','parkingA']  
	sim_startFN = 0
	sim_stopFN  = 0 
	
	v1simo = []
	v2simo = []
	v3simo = []
	v4simo = []
	
	buf = b''
	
	v1 = ([])
	v2 = ([])
	v3 = ([])
	v4 = ([])
	v1df = ([])
	v2df = ([])
	v3df = ([])
	v4df = ([])
	
	def clearBuffer_v124(self):
		if self.clearQBuf == True:
			self.v1 = ([])
			self.v2 = ([])
			#self.v3 = ([])
			self.v4 = ([])
			self.v1df = ([])
			self.v2df = ([])
			#self.v3df = ([])
			self.v4df = ([])
			
	def clearBuffer_v3(self):
		if self.clearQBuf == True:
			self.v3 = ([])
			self.v3df = ([])

	# add for interal use
	tlvLength = 0

	# for debug use 
	dbg = False #Packet unpacket Check: True show message 
	sm = True #Observed StateMachine: True Show message
	 
	
	def __init__(self,port,show = True):
		self.port = port
		if show:
			print("(jb)Medium Range Radar(MRR) raw Data lib initial")
			print("(jb)For Hardware:Batman-601(ISK)")
			print("(jb)Version: v0.1.0")
			print("(jb)Hardware: IWR-6843 ES2.0")
			print("(jb)Firmware: MRR")
			print("(jb)UART Baud Rate:921600")
			print("==============Info=================")
			print("Output: V1,V2,V3,V4 data:(RAW)")
			print("V1: Detected Object")
			print("V1 structure: [(hdr,Doppler,peakVal,X,Y,Z),......]")
			print("V2: Cluster")
			print("V2 structure: [(hdr,ClusterX,ClusterY,ClusterSizeX,ClusterSizeY),....]")
			print("V3: Tracking Object")
			print("V3 structure: [(hdr,TrackingX,TrackingY,velX,velY,ClusterSizeX,ClusterSizeY)....]")
			print("V4: Parking Assist")
			print("V4 [hdr,....] length:32")
			print("===================================")
	 
		
	def useDebug(self,ft):
		self.dbg = ft
		
	def stateMachine(self,ft):
		self.sm = ft
		
	def getHeader(self):
		return self.hdr
		
	def headerShow(self):
		print("***Header***********")  # 32 bytes
		print("Version:     \t%x "%(self.hdr.version))
		print("TotalPackLen:\t%d "%(self.hdr.totalPackLen))
		print("Platform:    \t%X "%(self.hdr.platform))
		print("PID(frame#): \t%d "%(self.hdr.frameNumber))
		print("Inter-frame Processing Time:\t{:d} us".format(self.hdr.cpuProcessTime))
		print("number of Objects:     \t%d "%(self.hdr.numOBJs))
		print("numTLVs:     \t%d "%(self.hdr.numTLVs))
		print("subframe#  : \t%d "%(self.hdr.subFrameNumber))
		print("***End Of Header***") 
		
	
	def headerShowAll(self):
		for i in range(2):
			print(f'hdrA({i})  : fn = { self.headerDic[i].frameNumber} ')
			print("***Header***********")  # 32 bytes
			print("Version:     \t%x "%( self.headerDic[i].version))
			print("TotalPackLen:\t%d "%( self.headerDic[i].totalPackLen))
			print("Platform:    \t%X "%( self.headerDic[i].platform))
			print("PID(frame#): \t%d "%( self.headerDic[i].frameNumber))
			print("Inter-frame Processing Time:\t{:d} us".format( self.headerDic[i].cpuProcessTime))
			print("number of Objects:     \t%d "%( self.headerDic[i].numOBJs))
			print("numTLVs:     \t%d "%( self.headerDic[i].numTLVs))
			print("subframe#  : \t%d "%( self.headerDic[i].subFrameNumber))
			print("***End Of Header***") 
	
	def list2df(self,chk,l1,l2,l3,l4):
		#print("---------------list2df: v1----------------")
		#print(l1)
		
		ll1 = pd.DataFrame(l1,columns=self.v1_col_names_rt)
		ll2 = pd.DataFrame(l2,columns=self.v2_col_names_rt)
		ll3 = pd.DataFrame(l3,columns=self.v3_col_names_rt)
		ll4 = pd.DataFrame(l4,columns=self.v4_col_names_rt)
		#print("------ll1---------list2df: v1----------------")
		#print(ll1)
		return (chk,ll1,ll2,ll3,ll4)
		
	 
	#################################################################################
	# FUNCTION: jb_getUartBuf(); get from serial port into buffer uartBuf[]
	#################################################################################
	JB_syncFlag = 0
	def jb_getUartBuf(self,disp = None):
		idx = 0
		self.buf = b''
		self.buf1 = b''
		bufDic = {}
		version = 0 
		totalPackLen = 0 
		platform = 0
		frameNumber = 0 
		cpuProcessTime = 0
		numOBJs = 0 
		numTLVs = 0
		subFrameNumber = 0
		hdr0 = header()
		hdr1 = header()
		self.headerDic = {0:hdr0, 1:hdr1}
		
		while True:
			if self.JB_syncFlag == 0:
				ch = self.port.read() # here ch type is byte
				if ch == self.magicWord[idx]: # 0..7
					self.buf += ch
					idx += 1 # 1..8
					if idx == 8:
						idx = 8
						self.JB_syncFlag = 1
						self.JB_t0 = time.time()
						self.JB_tMagic = time.time()
			else:
				self.JB_syncFlag = 0 # magic word ch mismatch loop back again
				idx = 0 # init
				self.buf = b""
				
			if self.JB_syncFlag == 1:
				# read next 32 bytes for header version, len, platform, fn
				for i in range(self.info.headerByte):
					ch = self.port.read()
					self.buf += ch
				if len(self.buf) == (self.magicLen + self.info.headerByte): 
					try: 
						(version,totalPackLen,platform,frameNumber,cpuProcessTime,numOBJs,numTLVs,subFrameNumber
						) = struct.unpack('8I', self.buf[8:40])
						
						(self.hdr.version,self.hdr.totalPackLen,self.hdr.platform,self.hdr.frameNumber,
						self.hdr.cpuProcessTime,self.hdr.numOBJs,self.hdr.numTLVs,self.hdr.subFrameNumber
						) = (version,totalPackLen,platform,frameNumber,cpuProcessTime,numOBJs,numTLVs,subFrameNumber)
						#if self.dbg == True:
						if disp:
							self.headerShow()
						 
					except:
						#if self.dbg == True:
						print("(Header)Improper TLV structure found: ")
						return (bufDic,self.headerDic)
					
					fn = self.hdr.frameNumber
					self.JB_syncFlag = 2
					
				else:
					self.JB_syncFlag = 0 # len mismatch loop back again
					idx = 0
					self.buf = b""

			if self.JB_syncFlag == 2:
				
				dataLen =  totalPackLen - self.magicLen - self.info.headerByte
				#print(f'----------JB_sync=2  data length: {dataLen}------------')
				r = self.port.read(dataLen) # read rest of bytes
				self.buf += r
				#self.port.flushInput() 
				dt = time.time()- self.JB_t0
				self.JB_tBuf = time.time()
				
				if self.hdr.subFrameNumber == 1:
					bufDic[1]    = self.buf
					(hdr1.version,hdr1.totalPackLen,hdr1.platform,hdr1.frameNumber,hdr1.cpuProcessTime,hdr1.numOBJs,hdr1.numTLVs,hdr1.subFrameNumber
					) = (version,totalPackLen,platform,frameNumber,cpuProcessTime,numOBJs,numTLVs,subFrameNumber)
					#headerDic[1] = hdr1
					self.JB_syncFlag == 0
					#print(f"--------1-----------{hdr1.totalPackLen}--------{ time.time() - self.JB_t0 }")
					self.port.flushInput() 
					return (bufDic,self.headerDic)
				 
				if self.hdr.subFrameNumber == 0:
					bufDic[0] = self.buf
					
					(hdr0.version,hdr0.totalPackLen,hdr0.platform,hdr0.frameNumber,hdr0.cpuProcessTime,hdr0.numOBJs,hdr0.numTLVs,hdr0.subFrameNumber
					) =  (version,totalPackLen,platform,frameNumber,cpuProcessTime,numOBJs,numTLVs,subFrameNumber)
					#headerDic[0] = hdr0
					self.JB_syncFlag == 0
					idx = 0
					self.buf = b""
					#print(f"--------0-----------{hdr0.totalPackLen}--------{ time.time() - self.JB_t0 }")
				 
	#################################################################
#
# TLV: Type-Length-Value
# read TLV data
# input:
#     disp: True:print message
#			False: hide printing message
# output:(return parameter)
# (pass_fail, v1, v2, v3, v4)
#  pass_fail: True: Data available    False: Data not available
#
#  v1: Detected Object List infomation
#  v2: Cluster Output information
#  v3: Tracking Output information
#  v4: Parking Assist Infomation
#
#  chk:  
#   0: empty: tlv = 0
#   1: data output
#  
#   10: idle
#   99: error
#
#
	def tlvRead(self,disp,df = None):
		#print("---tlvRead---")
		#ds = dos
		typeList   = [1,2,3,4]
		typeString = ['HDR','V1','V2','V3','V4']
		msgString  = {'HDR':"",'V1':'V1 Detected Object','V2':'V2 Cluster','V3':'V3 Tracking Object','V4':'V4 Parking Assist'}
		idx = 0
		lstate = 'idle'
		sbuf = b""
		tlvCount = 0
		pbyte = 16
		
		typeCnt = 0 # for check with tlvCount, if typeCnt equal to tlvCcount the process will completed 
		idxFrom = 0
		idxTo = 0
		magicLen  = 8
		headerLen = 32
		typeLen   = 8
		objUnitLen = 4
		
		''' 
		(uartBuf,hdrA) = self.jb_getUartBuf()
		print(f'uartBuf[0]:\n {uartBuf[0]}\n--------------------\nuartBuf[1]:\n {uartBuf[0]}\n')
		'''
		
		hdr_sf = 0 
		while True:
			
			if lstate == 'idle':
				if self.sm == True:
					print(f'(SM) {lstate}') 
					
				(uartBuf,hdrA) = self.jb_getUartBuf(disp = disp)
				lstate = 'block0'
				idxFrom = 0
				idxTo = 0
				
			if lstate == 'block0': #subFrameNumber = 0 
				hdr_sf = 0
				if self.sm == True:
						print(f'(SM) {lstate}') 
						
				if hdrA[0].numOBJs == 0 and hdrA[0].numTLVs == 0 and hdrA[0].subFrameNumber == 0:
					self.v3 = []; self.v3df = []
					lstate = 'block1'
				else:
					try:
						sbuf = uartBuf[0][40:]
					except:
						return self.list2df(99,self.v1df,self.v2df,self.v3df,self.v4df) if (df == 'DataFrame') else (99,self.v1,self.v2,self.v3,self.v4)
					#print("".join("{:02x}".format(c) for c in sbuf)) 
					idxFrom = 0
					idxTo = typeLen + objUnitLen
					tlvCount = hdrA[0].numTLVs
					lstate = 'Units'
			
			if lstate ==  'block1':
				hdr_sf = 1
				sbuf = b''
				sbuf = uartBuf[1][40:] #remove header
				if self.sm == True:
						print(f'(SM) {lstate}') 
						
				'''
				print(f'uartBuf-header Length= {len(sbuf)} objs:{hdrA[1].numOBJs} tlv#:{hdrA[1].numTLVs} subFrame:{hdrA[1].subFrameNumber}')
				print("".join("{:02x}".format(c) for c in sbuf))  
				'''
				if hdrA[1].numOBJs == 0 and hdrA[1].numTLVs == 0 and hdrA[1].subFrameNumber == 1:
					self.v1 = [];self.v1df = []; self.v2 = [];self.v2df = [];self.v4 = [];self.v4df = []
					return self.list2df(10,self.v1df,self.v2df,self.v3df,self.v4df) if (df == 'DataFrame') else (10,self.v1,self.v2,self.v3,self.v4)
				idxFrom = 0
				idxTo = typeLen + objUnitLen
				tlvCount = hdrA[1].numTLVs
				lstate = 'Units'
		
			if lstate == 'Units':
				#print(f"============= Units ================== from:to= [{idxFrom}:{idxTo}]")
				#print("".join("{:02x}".format(c) for c in sbuf[idxFrom:idxTo])) 
				ttype,self.tlvLength, objs,xyzQFormat = struct.unpack('2I2H', sbuf[idxFrom:idxTo]) 
				if ttype not in typeList:
					return self.list2df(99,self.v1df,self.v2df,self.v3df,self.v4df) if (df == 'DataFrame') else (99,self.v1,self.v2,self.v3,self.v4)
					
				vUnit = 1 / 2**xyzQFormat
				if disp:
					print(f'type/length: v{ttype}/{self.tlvLength} objs:{objs} xyzQFormat:{xyzQFormat} unit:{vUnit}')
				lstate = typeString[ttype]
				
				idxFrom = idxTo
				idxTo = idxFrom + self.tlvLength - objUnitLen 
				#print(f"============= Units -> {lstate} ====== from:to= [{idxFrom}:{idxTo}]")
			
			if lstate == 'V1' or lstate == 'V2' or lstate == 'V4' or lstate == 'V3':
				if self.sm == True:
						print(f'(SM) {lstate}') 
				tlvCount -= 1
				self.typeFunc(typeT = lstate ,vUnit= vUnit ,objs=objs,ldata = sbuf[idxFrom:idxTo], df = df)
				idxFrom = idxTo
				idxTo = idxFrom + typeLen + objUnitLen 
				lstate = 'Units'
			
			if tlvCount == 0 and hdr_sf == 0:
				lstate = 'block1'
				idxTo = 0
				idxFrom = 0
				
			if tlvCount == 0 and hdr_sf == 1:
				lstate = 'idle'
				return self.list2df(1,self.v1df,self.v2df,self.v3df,self.v4df) if (df == 'DataFrame') else (1,self.v1,self.v2,self.v3,self.v4)
			
			
	def typeFunc(self,typeT = None ,vUnit= None,objs= None,ldata = None, df = None):
		#print('typeFunc===> {}  vUnit:{:}'.format(typeT,vUnit))
		#print(":".join("{:02x}".format(c) for c in ldata))
		
		if typeT == 'V1':
			self.v1df = ([])
			self.v1   = ([])
			for i in range(objs):
				start = i * 10
				end   = (i+1) * 10
				(dt,pt,xt,yt,zt) = struct.unpack('hH3h', ldata[start:end]) # ori 5h
				d = dt * vUnit
				p = pt * vUnit
				x = xt * vUnit
				y = yt * vUnit
				z = zt * vUnit
				if self.dbg == True:
					print("V1 =>  d:{:.4f} p: {:.4f} x:{:.4f} y:{:.4f} z:{:.4f}".format(d,p,x,y,z))
				#v1_col_names_rt = ['fN','type','doppler','peakVal','X','Y','Z']
				if (df == 'DataFrame'):
					self.v1df.append((self.hdr.frameNumber,'v1',d,p,x,y,z))
					
				else:
					self.v1.append((self.hdr.frameNumber,d,p,x,y,z))
				
		if typeT == 'V2':
			self.v2df = ([])
			self.v2   = ([])
			for i in range(objs):
				start = i * 8
				end   = (i+1) * 8
				(ccXt,ccYt,csXt,csYt) = struct.unpack('4h', ldata[start:end])  # ori 4h
				ccX  =  vUnit * ccXt
				ccY  =  vUnit * ccYt
				csX  =  vUnit * csXt
				csY  =  vUnit * csYt
				if self.dbg == True:
					print("v2 => X:{:.4f} Y:{:.4f}  XD:{:.4f}  YD:{:.4f}".format(ccX,ccY,csX,csY))
				if (df == 'DataFrame'):
					self.v2df.append((self.hdr.frameNumber,'v2',ccX,ccY,csX,csY))
				else:
					self.v2.append((self.hdr.frameNumber,ccX,ccY,csX,csY)) 
					
		if typeT == 'V3': 
			self.v3 = ([])
			self.v3df = ([])
			for i in range(objs):
				start = i * 12
				end   = (i+1) * 12
				(Xt,Yt,XDt,YDt,Xsizet,Ysizet) = struct.unpack('6h', ldata[start:end]) # ori 6h
				X 	  =  vUnit * Xt
				Y     =  vUnit * Yt
				XD    =  vUnit * XDt
				YD    =  vUnit * YDt
				Xsize =  vUnit * Xsizet
				Ysize =  vUnit * Ysizet
				if self.dbg == True:
					print("v3 => X:{:.4f} Y:{:.4f}  XD:{:.4f}  YD:{:.4f} Xsize:{:.4f} Ysize:{:.4f}".format(X,Y,XD,YD,Xsize,Ysize))
				if (df == 'DataFrame' ):
					self.v3df.append((self.hdr.frameNumber,'v3',X,Y,XD,YD,Xsize,Ysize))
				else: 
					self.v3.append((self.hdr.frameNumber,X,Y,XD,YD,Xsize,Ysize))
					
		if typeT == 'V4':
			self.v4df = ([])
			self.v4   = ([])
			for i in range(objs):
				astA = [] 
				for i in range(objs):
					start = i * 2
					end   = (i+1) * 2
					ast, = struct.unpack('H', ldata[start:end]) 
					astA.append(ast * vUnit)
					
			if (df == 'DataFrame'):
				self.v4df.append((self.hdr.frameNumber,'v4',astA))
			else:
				self.v4.append((self.hdr.frameNumber,astA))
	
	

	def getRecordData(self,frameNum):
		s_fn = frameNum + self.sim_startFN
		#print("frame number:{:}".format(s_fn))
		v1d = self.v1simo[self.v1simo['fN'] == s_fn]
		
		v2d = self.v2simo[self.v2simo['fN'] == s_fn]
		v3d = self.v3simo[self.v3simo['fN'] == s_fn]
		v4d = self.v4simo[self.v4simo['fN'] == s_fn]
		return (v6d,v7d,v8d,v9d)
		
		
	'''
	def readFile(self,fileName):
		#fileName = "pc32021-03-19-10-02-17.csv"  
		#df = pd.read_csv(fileName, error_bad_lines=False, warn_bad_lines=False) 
		self.fileName = fileName 
		#          ['time','fN','type','elv','azimuth','range' ,'doppler','sx', 'sy', 'sz']
		df = pd.read_csv(self.fileName, names = self.v6_col_names, skiprows = [0,10,11,12],dtype={'fN': int,'elv': float,'azimuth':float,'range':float,'doppler':float,'sx':float,'sy':float,'sz':float}) 
		df.dropna()
		#print("------------------- df --------------------shape:{:}".format(df.shape))
		print(df)
		print(df.info())
		#print(df.info(memory_usage="deep")) 
		
		v1simOri = df[(df.type == 'v1')]
		#print("-------------------v1simo------------:{:}".format(v6simOri.shape))
									 
		self.v1simo = v1simOri.loc[:,['fN','type','range','azimuth','elv' ,'doppler','sx', 'sy', 'sz']]
		
		if len(self.v1simo):
			self.sim_startFN = df['fN'].values[0]
			self.sim_stopFN  = df['fN'].values[-1]
		#print(self.v6simo)
		
		self.v6simo['elv'] = self.v6simo['elv'].astype(float, errors = 'raise') 
		
		df7 = pd.read_csv(self.fileName, names = self.v7_col_names, skiprows = [0])  
		
		v7simc = df7[df7['type'] == 'v7']
		self.v7simo  = v7simc.loc[:,['fN','posX','posY','velX','velY','accX','accY','posZ','velZ','accZ','tid']]
		
		v8simc = df[df['type'] == 'v8']
		self.v8simo  = v8simc.loc[:,['fN','elv']]
		#print(self.v8simo)
		
		v9simc = df[df['type'] == 'v9']
		self.v9simo  = v9simc.loc[:,['fN','type','range','azimuth']]
		self.v9simo.columns = ['fN','type','snr','noise']
	
		return (self.v6simo,self.v7simo,self.v8simo,self.v9simo)
	'''


