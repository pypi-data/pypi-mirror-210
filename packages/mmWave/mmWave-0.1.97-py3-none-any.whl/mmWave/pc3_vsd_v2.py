# People Counting 3D + VSD  V2 
# 2022/09/12: beta
# v0.0.1
# v0.0.2 change dictionary: swap 'br' & 'hr'
# parsing People Counting 3D + VSD data use AOP
# hardware: BM-501 AOP
#     
# company: Joybien Technologies: www.joybien.com
# author: Zach Chen
#===========================================
# output: v1020,v1010,v1011,v1021 & v1040 raw data
# 

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
	timeCpuCycles = 0
	numDetectedObj = 0
	numTLVs = 0
	subframeNumber = 0


class vsInfo:
	tid 				 = int(0)
	rangeBin 			 = int(0)
	breathingDeviation   = float(0.0)
	heart_rate 			 = float(0.0)
	breathing_rate 		 = float(0.0)
	vitalSign_heart_buf  = [float(0.0)] * 15
	vitalSign_breath_buf = [float(0.0)] * 15
	

class Pc3_VSD_v2:
	MAGICWORD =  [b'\x01',b'\x02',b'\x03',b'\x04',b'\x05',b'\x06',b'\x07',b'\x08',b'\0x99']
	LEN_MAGIC_HEADER = 40
	port = ""
	hdr = header
	
	vs = vsInfo()  #vsos()
	playback = 0 
	sim_startFN = 0
	sim_stopFN  = 0 
	
	# add for interal use
	tlvLength = 0
	numOfPoints = 0
	# for debug use 
	dbg = False #Packet unpacket Check: True show message 
	sm  = False #Observed StateMachine: True Show message
	plen = 16 
	vitalSign_len = (8 * 11 + 2 * 4)
	#vsdic = {}
	vsdic= {'tid':0,'rangeBin' : 0,
					'breathDev': 0, 'br' : 0  ,'hr':0,
					'hrBuf': [], 'brBuf':[]
					}
	def __init__(self,port,azi_degree = None, bufSize = None):
		self.port = port
		self.port.reset_input_buffer()
		self.port.ReadBufferSize = bufSize
		self.degree = azi_degree
		self.azi_offset = 0.0 if azi_degree == None else azi_degree * np.pi/180.0
		
		print("\n\n\n(jb)People Counting 3D + VSD V2 initial")
		print("(jb)vsersion:v0.1.0")
		print("(jb)For Hardware:BM-501 (AOP)")
		print("(jb)Hardware: BM501-AOP")
		print("(jb)Firmware:")
		print("(jb)UART Baud Rate:921600")
		print("(jb)Output: v1020,v1010,v1011,v1021 & v1040 data:(RAW)\n\n\n\n")
		 
		
	def useDebug(self,ft):
		self.dbg = ft
		
	def stateMachine(self,ft):
		self.sm = ft
		
	def getHeader(self):
		return self.hdr
		
	def headerShow(self):
		print("******* Header ********") 
		print("Version:     \t%x "%(self.hdr.version))
		print("Platform:    \t%X "%(self.hdr.platform))
		print("TotalPackLen:\t%d "%(self.hdr.totalPackLen))
		print("PID(frame#): \t%d "%(self.hdr.frameNumber))
		print("Time in CPU Cycles:\t{:d} us".format(self.hdr.timeCpuCycles))
		print("numTLVs:     \t%d "%(self.hdr.numTLVs))
		print("subframe#  : \t%d "%(self.hdr.subframeNumber))
		print("***End Of Header***") 
			


#
# TLV: Type-Length-Value
# read TLV data
# input:
#     disp: True:print message
#			False: hide printing message
#     df: 
# output:(return parameter)
# (pass_fail,v1020,v1010,v1011,v1021,v1040)
#  pass_fail: True: Data available    False: Data not available
#  v1020: point cloud infomation
#  v1010: Target Object information
#  v1011: Target Index information
#  v1040: Vital Sign information
#  v10421: Presence Indication information
#  
#  v1020,v1010,v1011,v1021,v1040)
	JB_syncFlag = 0
	def jb_getUartBuf(self):
		idx = 0
		buf = b''
		while True:
			#(0) magic word
			if self.JB_syncFlag == 0:
				ch = self.port.read() # here ch type is byte
				if ch == self.MAGICWORD[idx]: # 0..7
					buf += ch
					idx += 1 # 1..8
					if idx == 8:
						idx = 8
						self.JB_syncFlag = 1
						self.JB_t0 = time.time()
			else:
				self.JB_syncFlag = 0 # magic word ch mismatch loop back again
				idx = 0 # init
				buf = b''
			
			#(1) header portion
			if self.JB_syncFlag == 1:
				for i in range(32):
					ch = self.port.read()
					buf += ch
				if len(buf) == self.LEN_MAGIC_HEADER: # version + totalLen
					try: 
						(self.hdr.version,self.hdr.totalPackLen,self.hdr.platform,
						self.hdr.frameNumber,self.hdr.timeCpuCycles,self.hdr.numDetectedObj,
						self.hdr.numTLVs,self.hdr.subframeNumber) = struct.unpack('8I', buf[8:40]) 
						self.frameNumber = self.hdr.frameNumber
					except:
						if self.dbg == True:
							print("(Header)Improper TLV structure found: ")
						return (False,'',0)
					
					#self.headerShow()
					
					self.frameNumber = self.hdr.frameNumber
					if self.playback == True:
						return (False,'',0)
					self.JB_syncFlag = 2
					
			#(2) read rest of Data  
			if self.JB_syncFlag == 2:
				r = self.port.read(self.hdr.totalPackLen - self.LEN_MAGIC_HEADER) # read rest of bytes
				return (True,r,self.hdr.numTLVs)
		 
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

	def tlvRead(self,disp,df=None):
		typeDic = {1000:'V1000',1010:'V1010',1011 :'V1011',1020 : 'V1020',1021 : 'V1021',1040 :'V1040',99: 'idle',999: 'TL'}
		restBuf = b''
		lstate = 'idle'
		
		v1020 = ([]) #v6
		v1010 = ([]) #v7
		v1011 = []   #v8
		v1021 = []
		v1040 = []   #vitalSign Information
		 
		
		idxFrom = 0
		idxTo   = 0
		ttype = 0
		tlvlength = 0
		tlvCnt = 0
		pts = 0
		pc_pts = 0
		while True:
			###############################
			# on {idle} getUartBuf() else parsing from uartBuf[]
			if lstate == 'idle':
				(chk, restBuf,tlvCnt) = self.jb_getUartBuf()
				if chk == True and len(restBuf) != 0:
					lstate = 'TL'
					 
					self.vsdic= {'tid':0,'rangeBin' : 0,
					'breathDev': 0, 'br' : 0  ,'hr':0,
					'hrBuf': [], 'brBuf':[]
					}
					 
					self.vsdic['brBuf'] = []
					self.vsdic['hrBuf'] = []
					
				else:
					return (False,v1020,v1010,v1011,v1021,v1040)
					
			elif lstate == 'TL':
				idxFrom = idxTo; idxTo += 8 #tlv: 8 bytes
				try:
					ttype, tlvlength =  struct.unpack('2I', restBuf[idxFrom:idxTo])
				except:
					print('Exception: TL data unpack')
					
				if ttype in typeDic:
					if self.sm == True:
						print(f"(SM): TL-->{lstate}  len:{tlvlength}")
					lstate = typeDic[ttype]
				else:
					return (False,v1020,v1010,v1011,v1021,v1040)
				
				
			elif lstate == 'V1010':
				idxFrom = idxTo; idxTo += tlvlength
				pts = int( tlvlength / 112)
				if self.sm == True: 
					print(f"(SM): ({lstate})   info: tlvCnt={tlvCnt} tlvlength:{tlvlength} restBuf_len:{len(restBuf)} points:{pts}")
				dataBytes = 112
				
				try:
					for i in range(pts):
						(tid,posX,posY,posZ,velX,velY,velZ,accX,accY,accZ,ec0,ec1,ec2,
						ec3,ec4,ec5,ec6,ec7,ec8,ec9,ec10,ec11,ec12,ec13,ec14,ec15,g,confi) = struct.unpack('I27f', restBuf[idxFrom + i*dataBytes : idxFrom + (i + 1)*dataBytes])
						
						#posX, posY = self.rotate_matrix(pX, pY, self.azi_offset  , x_shift=0, y_shift=0, units="RADIAN")  
						
						v1010.append((tid,posX,posY,posZ,velX,velY,velZ,accX,accY,accZ,ec0,ec1,ec2,ec3,ec4,ec5,ec6,ec7,ec8,ec9,ec10,ec11,ec12,ec13,ec14,ec15,g,confi))
				except:
					
					print('Exception: V1010 data unpack')
					return (False,v1020,v1010,v1011,v1021,v1040)

				
				tlvCnt -= 1
				if tlvCnt == 0:
					return (False,v1020,v1010,v1011,v1021,v1040)
				else:
					lstate = 'TL'
					if self.sm == True:
						print(f"(SM): (V1010) --> ({lstate})")
					
			
			elif lstate == 'V1020': # point cloud data
				# Uints
				idxFrom = idxTo; idxTo +=  20   #20 = 5 * 4
				try:
					(elvU,aziU,dopU,ranU,snrU) = struct.unpack('5f', restBuf[idxFrom:idxTo])
					pts = int((tlvlength - 20)/ 8)  # 8: 8types
					pc_pts = pts
					#print(f"(SM): ({lstate})   info: tlvCnt={tlvCnt} tlvlength:{tlvlength} restBuf_len:{len(restBuf)} points:{pts}")
					
					 
					# e,a,d,r,s
					idxFrom = idxTo; idxTo +=  (tlvlength - 20)
					for i in range(pts):
						(e,a,d,r,s) = struct.unpack('2bh2H', restBuf[idxFrom + i*8 : idxFrom + (i + 1)*8]) #8bytes
						elv = e * elvU
						azi = a * aziU
						dop = d * dopU
						ran = r * ranU
						snr = s * ranU
						sz  = ran * np.sin(elv)
						sx  = ran * np.cos(elv) * np.sin(azi)
						sy  = ran * np.cos(elv) * np.cos(azi)
						
						#v1020.append((elv,azi,ran,dop,snr,sx,sy,sz)) 
						v1020.append((sx,sy,sz,dop,snr,azi,elv,ran)) 
				except:
					return (False,v1020,v1010,v1011,v1021,v1040)
					print('Exception: V1020 data unpack')
					
				tlvCnt -= 1
				if tlvCnt == 0:
					return (True,v1020,v1010,v1011,v1021,v1040)
				else:
					lstate = 'TL'
					if self.sm == True:
						print(f"(SM): V1020 --> ({lstate})")
				
			
			elif lstate == 'V1011': #Target Index   ?????????????????????????
				idxFrom = idxTo;  idxTo += tlvlength
				pts = int(tlvlength/1)
				
				try: 
					for i in range(pts):
						ti =  struct.unpack('B', restBuf[idxFrom+i :idxFrom+(i+1)])
						v1011.append(ti[0])
				except:
					print('Exception: V1011 data unpack')
				
				if self.sm == True:
					print(f"(SM): ({lstate})   info: tlvCnt={tlvCnt} tlvlength:{tlvlength} restBuf_len:{len(restBuf)} points:{pts}")
					#print(f"v1011= {v1011}")
				
				tlvCnt -= 1
				if tlvCnt == 0:
					return (True,v1020,v1010,v1011,v1021,v1040)
				else:
					lstate = 'TL'
					if self.sm == True:
						print(f"(SM): V1011 --> ({lstate})")
			
			elif lstate == 'V1021': #Target Presence Indication
				
				idxFrom = idxTo; idxTo += tlvlength
				pts = int(tlvlength/4)
				#print(f"(SM): ({lstate})   info: tlvCnt={tlvCnt} tlvlength:{tlvlength} restBuf_len:{len(restBuf)} points:{pts}")
				try:
					for i in range(pts):
						tpi = struct.unpack('I', restBuf[idxFrom + i*4 : idxFrom + (i + 1)*4])
						v1021.append(tpi[0]) 
				except:
					print('Exception: V1021 data unpack')
					return (False,v1020,v1010,v1011,v1021,v1040)
				 
				tlvCnt -= 1
				if tlvCnt == 0:
					return (True,v1020,v1010,v1011,v1021,v1040)
				else:
					lstate = 'TL'
					if self.sm == True:
						print(f"(SM): V1021 --> ({lstate})")
			
			elif lstate == 'V1040': #vital sign information
				idxFrom = idxTo; idxTo += tlvlength
				try:
					temp = struct.unpack('2H33f',restBuf[idxFrom:idxTo])
					
					self.vs.tid 				= temp[0]
					self.vs.rangeBin			= temp[1]
					self.vs.breathingDeviation  = temp[2]
					self.vs.heart_rate 			= temp[3]
					self.vs.breathing_rate		= temp[4]
					for i in range(15):
						self.vs.vitalSign_heart_buf[i]  = temp[5+i] 
						self.vs.vitalSign_breath_buf[i] = temp[20+i]
						
					self.vsdic= {'tid':self.vs.tid,'rangeBin' : self.vs.rangeBin,
						'breathDev': self.vs.breathingDeviation, 'hr' : self.vs.heart_rate  ,'br':self.vs.breathing_rate,
						'hrBuf': self.vs.vitalSign_heart_buf, 'brBuf':self.vs.vitalSign_breath_buf
						}
					
					#print("tid:{:} rangeBin:{:} bDev:{:.3f} hr:{:.3f} br:{:.3f}".format(self.vs.tid,self.vs.rangeBin,self.vs.breathingDeviation,self.vs.heart_rate,self.vs.breathing_rate))
					#print(f"(SM): ({lstate})   info: tlvCnt={tlvCnt} tlvlength:{tlvlength} restBuf_len:{len(restBuf)} points:{pts}")
					
				except:
					print('Exception: V1041 data unpack')
					return (False,v1020,v1010,v1011,v1021,v1040)
				
				tlvCnt -= 1
				if tlvCnt == 0:
					if self.sm == True:
						print(f"(SM): V1040 --> ESC ")
					return (True,v1020,v1010,v1011,v1021,v1040)
				else:
					lstate = 'TL'
					if self.sm == True:
						print(f"(SM): V1040 --> ({lstate})")
		




