import sounddevice as sd
from scipy.io.wavfile import write

def record_audio(filename, duration=5, fs=16000):
    """录制音频并保存为 WAV 文件。"""
    print(f"开始录制 {duration} 秒的音频...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  # 等待录音结束
    write(filename, fs, recording)  # 保存为 WAV 文件
    print(f"录音完成，音频已保存为 {filename}")

if __name__ == "__main__":
    # 录制音频并保存为 'recorded_audio.wav'
    record_audio("recorded_audio.wav", duration=5)  # 可根据需要调整持续时间
