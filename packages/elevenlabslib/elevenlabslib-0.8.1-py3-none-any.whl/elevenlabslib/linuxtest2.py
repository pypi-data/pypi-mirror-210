import io
import queue
import sys
import threading
import pyaudio
import requests
import sounddevice as sd
import soundfile as sf


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

blocksize = 2048
buffersize = 4
pyABackend = pyaudio.PyAudio()
defaultOutputInfo = pyABackend.get_default_output_device_info()
deviceID = defaultOutputInfo['index']
q = queue.Queue(maxsize=buffersize)
audioData = requests.get("https://files.catbox.moe/hpemr0.mp3").content
audioFile = io.BytesIO(audioData)
audioFile.seek(0)


event = threading.Event()


def callback(outdata, frames, time, status):
    assert frames == blocksize
    if status.output_underflow:
        print('Output underflow: increase blocksize?', file=sys.stderr)
        raise sd.CallbackAbort
    assert not status
    try:
        data = q.get_nowait()
    except queue.Empty as e:
        print('Buffer is empty: increase buffersize?', file=sys.stderr)
        raise sd.CallbackAbort from e
    if len(data) < len(outdata):
        outdata[:len(data)] = data
        outdata[len(data):] = b'\x00' * (len(outdata) - len(data))
        raise sd.CallbackStop
    else:
        outdata[:] = data


try:
    with sf.SoundFile(audioFile) as f:
        for _ in range(buffersize):
            data = f.buffer_read(blocksize, dtype='float32')
            if not data:
                break
            q.put_nowait(data)  # Pre-fill queue
        stream = sd.RawOutputStream(
            samplerate=f.samplerate, blocksize=blocksize,
            device=deviceID, channels=f.channels, dtype='float32',
            callback=callback, finished_callback=event.set)
        with stream:
            timeout = blocksize * buffersize / f.samplerate
            while data:
                data = f.buffer_read(blocksize, dtype='float32')
                q.put(data, timeout=timeout)
            event.wait()  # Wait until playback is finished
except KeyboardInterrupt:
    print("Interrupted by user")
    exit()
except queue.Full:
    # A timeout occurred, i.e. there was an error in the callback
    exit(1)
except Exception as e:
    exit(type(e).__name__ + ': ' + str(e))
