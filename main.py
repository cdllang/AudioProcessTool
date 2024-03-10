import tkinter as tk
from tkinter import ttk, Entry
import threading
from tkinterdnd2 import DND_FILES, TkinterDnD
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
AudioSegment.converter = "ffmpeg.exe"
def export_audio(sound, output_path):
    """将有声音频导出为一个文件"""
    output_path = output_path + "修改.wav"
    sound.export(output_path, format="wav")
def analyze_audio(audio_path, threshold=-40, min_silence_len=500):
    """分析音频，返回去除低于阈值音量的声音后的有声时长（单位：毫秒）"""
    sound = AudioSegment.from_file(audio_path)
    nonsilent_chunks = detect_nonsilent(sound, min_silence_len=min_silence_len, silence_thresh=threshold)
    total_duration = sum((end - start for start, end in nonsilent_chunks))
    # export_audio(sound, nonsilent_chunks, audio_path)
    # 将声音大于阈值的部分拉到最大
    for start, end in nonsilent_chunks:
        segment = sound[start:end]
        max_dB = segment.max_dBFS
        segment = segment + (0 - max_dB-threshold)
        sound = sound.overlay(segment, position=start)

    export_audio(sound, audio_path)
    return total_duration
def process_files(audio_paths):
    if threshold_entry.get() == "":
        threshold = -40
    else:
        threshold = int(threshold_entry.get())
    if not threshold:
        threshold = -40
    total_duration = 0
    current_file_index = 0
    total_files = len(audio_paths)
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(app, variable=progress_var, maximum=total_files)
    progress_bar.pack(pady=10)
    for audio_path in audio_paths:
        current_file_index += 1
        result_var.set(f"正在处理第 {current_file_index}/{total_files} 个文件")
        progress_var.set(current_file_index)
        app.update_idletasks()
        total_duration += analyze_audio(audio_path,threshold)
    result_var.set(f"有声音的总长度（去除静音部分）：{total_duration / 1000}秒")
    progress_bar.destroy()

def on_drop(event):
    global current_file_index
    audio_paths = app.tk.splitlist(event.data)
    threading.Thread(target=process_files, args=(audio_paths,)).start()

app = TkinterDnD.Tk()
app.title('DryVocalTimeAnalyser')
app.iconbitmap('icon.ico')
result_var = tk.StringVar()
result_label = tk.Label(app, textvariable=result_var)
result_label.pack(pady=10)
threshold_entry = Entry(app)
threshold_entry.pack(pady=10)
threshold_var = tk.StringVar()
threshold_label = tk.Label(app, textvariable=threshold_var)
threshold_label.pack(pady=10)
threshold_var.set("输入阈值（默认-40）")
result_var.set("请直接拖拽音频文件到此窗口\n程序会自动处理并输出处理结果到原文件路径下\n文件名后会加上“修改”字样以示区别")
app.drop_target_register(DND_FILES)
app.dnd_bind('<<Drop>>', on_drop)

app.geometry('400x200')
app.mainloop()
