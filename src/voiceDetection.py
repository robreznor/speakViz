
import sys
sys.path.append('../lib/')
import webrtcvad
import numpy as np
import time
from mic_array.mic_array import MicArray
from voice_engine.source import Source
from voice_engine.channel_picker import ChannelPicker
from mic_array.pixels import pixels
import pyaudio


#import matplotlib.pyplot as plt
#from gpiozero import LED

RATE = 16000
CHANNELS = 4
VAD_FRAMES = 20     # ms
#DOA_FRAMES = 200    # ms
DOA_FRAMES =350   # ms

def main():
	vad = webrtcvad.Vad(3)
	speech_count = 0
	chunks = []
	user = []
	user.append([])
	user.append([])
	user.append([])
	user.append([])
	doa_chunks = int(DOA_FRAMES / VAD_FRAMES)    
	file = open('output.txt','w')
	frames = []
	try:	
			
		with MicArray(RATE, CHANNELS, RATE * VAD_FRAMES / 1000)  as mic:
			start = time.time()
			newArrival = True
			tiempo = 0
			currentframe = start

			for chunk in mic.read_chunks():				
				# Use single channel audio to detect voice activity
				if vad.is_speech(chunk[0::CHANNELS].tobytes(), RATE):
					speech_count += 1
					sys.stdout.write('1')
					file.write('1')                   
				else:
					sys.stdout.write('0') 
					file.write('0')

				tiempo = 0.02 + tiempo				
				sys.stdout.flush()
				chunks.append(chunk)

				if len(chunks) == doa_chunks:					
					if speech_count > (doa_chunks / 2):
						finalTime = time.time() - start
						frames = np.concatenate(chunks)
						direction = mic.get_direction(frames)
						print('\nTiempo: {0:.2f}' .format(tiempo))
						#print('\nTiempo Inicio: {0:.2f}' .format(startTime))
						#print('\nTiempo Fin: {0:.2f}' .format(finalTime))
						print('\nDireccion: {}'.format(int(direction)))
						pixels.wakeup(direction)
						if int(direction) < 90:
							micPos = 0
						elif int(direction) < 180:
							micPos = 1
						elif int(direction) < 270:
							micPos = 2
						else:
							micPos = 3

						user[micPos].append(float("{0:.2f}".format(tiempo)))
						file.write('\n{}' .format(int(direction)))
						file.write('\n')
						
					speech_count = 0
					chunks = []			
			time.sleep(1)
			file.close()
			mic.stop()
	except KeyboardInterrupt:
		pass
		#plt.ylim(0,5)		
		print 'intervenciones' 		
		#labels = ['Usuario 1', 'Usuario 2', 'Usuario 3', 'Usuario 4']
		#plt.yticks([1,2,3,4], labels)
		for x in range(0,len(user)):
			print "usuario", x+1,":", user[x] 
			#plt.plot(user[x],[x+1]*len(user[x]),'o')
		
		#plt.show()
		#plt.savefig("figura")
if __name__ == '__main__':
	main()