import os
import tkinter as tk
from tkinter import ttk, Entry
import threading
from tkinterdnd2 import DND_FILES, TkinterDnD
from pydub import AudioSegment
from pydub.silence import detect_nonsilent

AudioSegment.converter = "ffmpeg.exe"



def export_audio(sound, output_path):
    """将有声音频导出为一个文件"""
    detail = ""
    if FuncMode.get() == "analysis":
        detail = " 干音分析"
    else:
        detail = " 音频处理"
        if AudioType.get() == "mono":
            detail += " 单声道"
        else:
            detail += " 双声道"
        if SampleRate.get() == 48000:
            detail += " 48000hz"
        else:
            detail += " 44100hz"
        if Normalize.get():
            detail += " 标准化"
    #获取文件名
    filename = output_path.split("/")[-1]
    #获取文件地址并去除文件名
    output_path = output_path.replace("\\","/")
    output_path = output_path.split("/")
    output_path = "/".join(output_path[:-1])
    print(output_path)
    #判断原文件地址是否有output文件夹，没有则创建
    if not os.path.exists(output_path+"/output/"):
        os.makedirs(output_path+"/output/")
    print(filename.split("."))
    output_path = output_path+"/output/" + filename.split(".")[0] + detail +"." + filename.split(".")[1]
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
def analysis_files(audio_paths):
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
def process_files(audio_paths):
    #将音频转换为AudioType和SampleRate对应格式
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

        sound = AudioSegment.from_file(audio_path)
        sound = sound.set_frame_rate(SampleRate.get())
        if AudioType.get() == "mono":
            sound = sound.set_channels(1)
        else:
            sound = sound.set_channels(2)
        if Normalize.get():
            sound = sound.apply_gain(-sound.max_dBFS)
        export_audio(sound, audio_path)
    progress_bar.destroy()
    result_var.set(f"处理完成")
def on_checkA():

    if AValue.get() == 1:
        FuncMode.set("analysis")
        print(FuncMode)
        #显示阈值输入框
        threshold_entry.pack()
        threshold_label.pack()
        #将另一个checkbox设置为不选中
        PValue.set(0)
        app.update_idletasks()
        #隐藏单声道、双声道、48000hz、44100hz等checkbox
        chkStereo.pack_forget()
        chkMono.pack_forget()
        chk48000.pack_forget()
        chk44100.pack_forget()
        chkNmlz.pack_forget()

    else:
        #隐藏阈值输入框
        FuncMode.set("process")
        print(FuncMode)
        threshold_entry.pack_forget()
        threshold_label.pack_forget()
        PValue.set(1)
        #显示单声道、双声道、48000hz、44100hz等checkbox
        chkStereo.pack()
        chkMono.pack()
        chk48000.pack()
        chk44100.pack()
        chkNmlz.pack()

def on_checkP():
    if PValue.get() == 1:
        FuncMode.set("process")
        print(FuncMode)
        #隐藏阈值输入框
        threshold_entry.pack_forget()
        threshold_label.pack_forget()
        #将另一个checkbox设置为不选中
        AValue.set(0)
        #显示单声道、双声道、48000hz、44100hz等checkbox
        chkStereo.pack()
        chkMono.pack()
        chk48000.pack()
        chk44100.pack()
        chkNmlz.pack()
    else:
        FuncMode.set("analysis")
        AValue.set(1)
        #隐藏阈值输入框
        threshold_entry.pack()
        threshold_label.pack()
        #隐藏单声道、双声道、48000hz、44100hz等checkbox
        chkStereo.pack_forget()
        chkMono.pack_forget()
        chk48000.pack_forget()
        chk44100.pack_forget()
        chkNmlz.pack_forget()
def on_checkStereo():
    if SValue.get() == 1:
        AudioType.set("stereo")
        MValue.set(0)
    else:
        AudioType.set("mono")
        MValue.set(1)
def on_checkMono():
    if MValue.get() == 1:
        AudioType.set("mono")
        SValue.set(0)
    else:
        AudioType.set("stereo")
        SValue.set(1)
def on_check48000():
    if C48Value.get() == 1:
        SampleRate.set(48000)
        C41Value.set(0)
    else:
        SampleRate.set(44100)
        C41Value.set(1)
def on_check44100():
    if C41Value.get() == 1:
        SampleRate.set(44100)
        C48Value.set(0)
    else:
        SampleRate.set(48000)
        C48Value.set(1)
def on_drop(event):
    global current_file_index
    audio_paths = app.tk.splitlist(event.data)
    print(FuncMode)
    if FuncMode.get() == "analysis":
        threading.Thread(target=analysis_files, args=(audio_paths,)).start()
    else:
        threading.Thread(target=process_files, args=(audio_paths,)).start()
def on_checkNmlz():
    if NValue.get() == 1:
        Normalize.set(True)
    else:
        Normalize.set(False)




app = TkinterDnD.Tk()
app.title('DryVocalTimeAnalyser')
app.iconbitmap('icon.ico')
AValue = tk.IntVar(value=1)
PValue = tk.IntVar(value=0)
C48Value = tk.IntVar(value=1)
C41Value = tk.IntVar(value=0)
SValue = tk.IntVar(value=1)
MValue = tk.IntVar(value=0)
NValue = tk.IntVar(value=0)
FuncMode = tk.StringVar(value="analysis")
SampleRate = tk.IntVar(value=48000)
AudioType = tk.StringVar(value="stereo")
Normalize = tk.BooleanVar(value=False)
#默认为干音分析
chkA = ttk.Checkbutton(app, text='干音分析', variable=AValue,onvalue=1,offvalue=0,command=on_checkA)
chkA.pack()
chkP = ttk.Checkbutton(app, text='素材处理', variable=PValue,onvalue=1,offvalue=0,command=on_checkP)
chkP.pack()
chkStereo = ttk.Checkbutton(app, text='双声道', variable=SValue,onvalue=1,offvalue=0,command=on_checkStereo)
chkMono = ttk.Checkbutton(app, text='单声道', variable=MValue,onvalue=1,offvalue=0,command=on_checkMono)
chk48000 = ttk.Checkbutton(app, text='48000hz', variable=C48Value,onvalue=1,offvalue=0,command=on_check48000)
chk44100 = ttk.Checkbutton(app, text='44100hz', variable=C41Value,onvalue=1,offvalue=0,command=on_check44100)
chkNmlz = ttk.Checkbutton(app, text='标准化', variable=NValue,onvalue=1,offvalue=0,command=on_checkNmlz)
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

app.geometry('400x300')
app.mainloop()
