import os
import tkinter as tk
from tkinter import ttk, Entry
import threading
from tkinterdnd2 import DND_FILES, TkinterDnD
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from tkinter import messagebox
import json
AudioSegment.converter = "ffmpeg.exe"
from playsound import playsound


def export_audio(sound, output_path):
    """将有声音频导出为一个文件"""
    detail = ""
    if NameValue.get() == 1:
        if FuncMode.get() == "analysis":
            detail = "_干音分析"
            print(detail)
        else:
            detail = "_音频处理"
            if AudioType.get() == "auto":
                detail += "_"+AutoDetect.get()
            else:
                if AudioType.get() == "mono":
                    detail += "_mono"
                else:
                    detail += "_stereo"
            if SampleRate.get() == 48000:
                detail += "_48000hz"
            else:
                detail += "_44100hz"
            if Normalize.get():
                detail += "_normalized"
            print(detail)
    #获取文件名
    output_path = output_path.replace("\\","/")
    filename = output_path.split("/")[-1]
    #获取文件地址并去除文件名
    output_path = output_path.split("/")
    output_path = "/".join(output_path[:-1])
    print(output_path)
    #判断原文件地址是否有output文件夹，没有则创建
    if not os.path.exists(output_path+"/output/"):
        os.makedirs(output_path+"/output/")
    #去除文件名后缀文件可能存在多个.所以只删除最后一个元素
    filename = filename.split(".")
    filename = ".".join(filename[:-1])
    print(filename)

    #文件名为按.分离的倒数第二个元素
    output_path = output_path+"/output/" + filename+ detail +"." + OutputFormat.get()
    #如果为MP3
    if OutputFormat.get() == "mp3":
        sound.export(output_path, format="mp3", bitrate="320k")
    else:
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
    progress_bar = ttk.Progressbar(middle_frame, variable=progress_var, maximum=total_files)
    progress_bar.grid(row=16, column=0, pady=0, sticky='n')
    for audio_path in audio_paths:
        if is_audio_file(audio_path) == False:
            current_file_index += 1
            continue
        current_file_index += 1
        result_var.set(f"正在处理第 {current_file_index}/{total_files} 个文件")
        progress_var.set(current_file_index)
        app.update_idletasks()
        total_duration += analyze_audio(audio_path,threshold)
    result_var.set(f"有声音的总长度（去除静音部分）：{total_duration / 1000}秒")
    playsound('sound.wav')
    progress_bar.destroy()
def process_files(audio_paths):
    #将音频转换为AudioType和SampleRate对应格式
    current_file_index = 0
    total_files = len(audio_paths)
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(middle_frame, variable=progress_var, maximum=total_files)
    progress_bar.grid(row=16, column=0, pady=0, sticky='n')
    for audio_path in audio_paths:
        if is_audio_file(audio_path) == False:
            current_file_index += 1
            continue
        current_file_index += 1
        result_var.set(f"正在处理第 {current_file_index}/{total_files} 个文件")
        progress_var.set(current_file_index)
        app.update_idletasks()

        sound = AudioSegment.from_file(audio_path)
        sound = sound.set_frame_rate(SampleRate.get())
        if AudioType.get() == "auto":
            if sound.channels == 1:
                sound = sound.set_channels(1)
                AutoDetect.set("mono")
            else:
                #如果双声道的音频相同，则转为单声道
                if sound.split_to_mono()[0] == sound.split_to_mono()[1]:
                    sound = sound.set_channels(1)
                    AutoDetect.set("mono")
                else:
                    #如果双声道的其中一轨没有声音，则转为单声道
                    if sound.split_to_mono()[0].max_dBFS == -96 or sound.split_to_mono()[1].max_dBFS == -96:
                        sound = sound.set_channels(1)
                        AutoDetect.set("mono")
                    else:
                        sound = sound.set_channels(2)
                        AutoDetect.set("stereo")
        if AudioType.get() == "mono":
            sound = sound.set_channels(1)
        if AudioType.get() == "stereo":
            sound = sound.set_channels(2)
        if Normalize.get():
            sound = sound.apply_gain(-sound.max_dBFS)
        export_audio(sound, audio_path)
    progress_bar.destroy()
    result_var.set(f"处理完成")
    playsound('sound.wav')
def on_checkA():

    if AValue.get() == 1:
        FuncMode.set("analysis")
        print(FuncMode.get())
        #将另一个checkbox设置为不选中
        PValue.set(0)
        app.update_idletasks()
    else:
        #隐藏阈值输入框
        FuncMode.set("process")
        print(FuncMode.get())
        PValue.set(1)

def on_checkP():
    if PValue.get() == 1:
        FuncMode.set("process")
        print(FuncMode.get())
        #将另一个checkbox设置为不选中
        AValue.set(0)
    else:
        FuncMode.set("analysis")
        print(FuncMode.get())
        AValue.set(1)
def on_checkStereo():
    if SValue.get() == 1:
        AudioType.set("stereo")
        print(AudioType.get())
        MValue.set(0)
        ATValue.set(0)
    else:
        AudioType.set("mono")
        print(AudioType.get())
        MValue.set(1)
        ATValue.set(0)
def on_checkMono():
    if MValue.get() == 1:
        AudioType.set("mono")
        print(AudioType.get())
        SValue.set(0)
        ATValue.set(0)
    else:
        AudioType.set("stereo")
        print(AudioType.get())
        SValue.set(1)
        ATValue.set(0)
def on_checkAuto():
    if ATValue.get() == 1:
        AudioType.set("auto")
        print(AudioType.get())
        MValue.set(0)
        SValue.set(0)
    else:
        AudioType.set("stereo")
        print(AudioType.get())
        SValue.set(1)
        MValue.set(0)
def on_check48000():
    if C48Value.get() == 1:
        SampleRate.set(48000)
        print(SampleRate.get())
        C41Value.set(0)
    else:
        SampleRate.set(44100)
        print(SampleRate.get())
        C41Value.set(1)
def on_check44100():
    if C41Value.get() == 1:
        SampleRate.set(44100)
        print(SampleRate.get())
        C48Value.set(0)
    else:
        SampleRate.set(48000)
        print(SampleRate.get())
        C48Value.set(1)
def on_drop(event):
    global current_file_index
    audio_paths = app.tk.splitlist(event.data)
    if FuncMode.get() == "analysis":
        threading.Thread(target=analysis_files, args=(audio_paths,)).start()
    else:
        threading.Thread(target=process_files, args=(audio_paths,)).start()
def on_checkNmlz():
    if NValue.get() == 1:
        Normalize.set(True)
        print("Normalized")
    else:
        Normalize.set(False)
        print("Not Normalized")
def on_checkOutputFormat():
    if OutputFormat.get() == "wav":
        OutputFormat.set("wav")
        print("wav")
    else:
        OutputFormat.set("mp3")
        print("mp3")
def on_checkName():
    if NValue.get() == 1:
        print("添加命名后缀")
    else:
        print("不添加命名后缀")

def is_audio_file(file_path):
    """判断文件是否为能处理的音频文件"""
    try:
        AudioSegment.from_file(file_path)
        return True
    except:
        return False
def handle_file_1(event):
    # 分析
    global current_file_index
    audio_paths = app.tk.splitlist(event.data)
    FuncMode.set("analysis")
    threading.Thread(target=analysis_files, args=(audio_paths,)).start()

def handle_file_2(event):
    # 处理
    global current_file_index
    audio_paths = app.tk.splitlist(event.data)
    FuncMode.set("process")
    threading.Thread(target=process_files, args=(audio_paths,)).start()

def read_json_file():
    """读取 JSON 文件并提取 color1 和 color2"""
    bool = True
    try:
        with open("config.json", 'r') as file:
            data = json.load(file)
            color1 = data.get("color1", "未找到 color1")
            color2 = data.get("color2", "未找到 color2")
    except Exception as e:
        bool = False
        messagebox.showerror("错误", f"读取 JSON 文件时出错: {e}")
    if bool:
        return color1, color2
    else:
        return "lightblue", "lightgreen"

# 创建主窗口
app = TkinterDnD.Tk()
app.title('DryVocalTimeAnalyser')
app.iconbitmap('icon.ico')
app.geometry('600x450')
colorA = "lightblue"
colorP = "lightgreen"
colorA,colorP = read_json_file()
# 设置变量
AValue = tk.IntVar(value=1)
PValue = tk.IntVar(value=0)
NameValue = tk.IntVar(value=1)
C48Value = tk.IntVar(value=1)
C41Value = tk.IntVar(value=0)
SValue = tk.IntVar(value=0)
MValue = tk.IntVar(value=0)
ATValue = tk.IntVar(value=1)
NValue = tk.IntVar(value=0)
FuncMode = tk.StringVar(value="analysis")
SampleRate = tk.IntVar(value=48000)
AudioType = tk.StringVar(value="auto")
Normalize = tk.BooleanVar(value=False)
AutoDetect = tk.StringVar(value="None")
OutputFormat = tk.StringVar(value="wav")

# 使用grid布局管理器
app.columnconfigure(0, weight=1, minsize=150)
app.columnconfigure(1, weight=1, minsize=300)
app.columnconfigure(2, weight=1, minsize=150)
app.rowconfigure(0, weight=1)

# 创建两个区域
frame1 = tk.Frame(app, bg=colorA)
frame1.grid(row=0, column=0, padx=0, pady=0, sticky='nsew')

frame2 = tk.Frame(app, bg=colorP)
frame2.grid(row=0, column=2, padx=0, pady=0, sticky='nsew')

# 为两个区域设置拖拽文件功能
frame1.drop_target_register(DND_FILES)
frame1.dnd_bind('<<Drop>>', lambda event: handle_file_1(event))

frame2.drop_target_register(DND_FILES)
frame2.dnd_bind('<<Drop>>', lambda event: handle_file_2(event))

# 在frame1中添加文字
label1 = tk.Label(frame1, text="干音分析", bg=colorA)
label1.pack(expand=True)

# 在frame2中添加文字
label2 = tk.Label(frame2, text="素材处理", bg=colorP)
label2.pack(expand=True)


middle_frame = tk.Frame(app)
middle_frame.grid(row=0, column=1, padx=0, pady=10, sticky='ns')
# 在中间放置其他控件
#chkA = ttk.Checkbutton(middle_frame, text='干音分析', variable=AValue, onvalue=1, offvalue=0, command=on_checkA)
#chkP = ttk.Checkbutton(middle_frame, text='素材处理', variable=PValue, onvalue=1, offvalue=0, command=on_checkP)
chkN = ttk.Checkbutton(middle_frame, text='添加命名后缀', variable=NameValue, onvalue=1, offvalue=0, command=on_checkName)
chkStereo = ttk.Checkbutton(middle_frame, text='双声道', variable=SValue, onvalue=1, offvalue=0, command=on_checkStereo)
chkMono = ttk.Checkbutton(middle_frame, text='单声道', variable=MValue, onvalue=1, offvalue=0, command=on_checkMono)
chkAuto = ttk.Checkbutton(middle_frame, text='自动检测', variable=ATValue, onvalue=1, offvalue=0, command=on_checkAuto)
chk48000 = ttk.Checkbutton(middle_frame, text='48000hz', variable=C48Value, onvalue=1, offvalue=0, command=on_check48000)
chk44100 = ttk.Checkbutton(middle_frame, text='44100hz', variable=C41Value, onvalue=1, offvalue=0, command=on_check44100)
chkNmlz = ttk.Checkbutton(middle_frame, text='标准化', variable=NValue, onvalue=1, offvalue=0, command=on_checkNmlz)
chkOutputFormat = ttk.Checkbutton(middle_frame, text='导出为mp3(默认wav)', variable=OutputFormat, onvalue="mp3", offvalue="wav", command=on_checkOutputFormat)

#chkA.grid(row=0, column=0, sticky='n', pady=0)
#chkP.grid(row=1, column=0, sticky='n', pady=0)
chkN.grid(row=2, column=0, sticky='n', pady=0)
chkStereo.grid(row=3, column=0, sticky='n', pady=0)
chkMono.grid(row=4, column=0, sticky='n', pady=0)
chkAuto.grid(row=5, column=0, sticky='n', pady=0)
chk48000.grid(row=6, column=0, sticky='n', pady=0)
chk44100.grid(row=7, column=0, sticky='n', pady=0)
chkNmlz.grid(row=8, column=0, sticky='n', pady=0)
chkOutputFormat.grid(row=9, column=0, sticky='n', pady=0)

result_var = tk.StringVar()
result_label = tk.Label(middle_frame, textvariable=result_var)
result_label.grid(row=15, column=0, pady=0, sticky='n')

threshold_entry = tk.Entry(middle_frame)
threshold_entry.grid(row=12, column=0, pady=0, sticky='n')

threshold_var = tk.StringVar()
threshold_label = tk.Label(middle_frame, textvariable=threshold_var)
threshold_label.grid(row=13, column=0, pady=0, sticky='n')
threshold_var.set("输入阈值（默认-40）")

result_var.set("这里显示处理进度和结果")

split_label1 = tk.Label(middle_frame, text="--------------素材处理设定--------------", font=("Helvetica", 10, "bold"))
split_label1.grid(row=0, column=0, pady=5, sticky='n')

split_label2 = tk.Label(middle_frame, text="--------------干音分析设定--------------", font=("Helvetica", 10, "bold"))
split_label2.grid(row=11, column=0, pady=5, sticky='n')

split_label2 = tk.Label(middle_frame, text="-------------处理进度与结果-------------", font=("Helvetica", 10, "bold"))
split_label2.grid(row=14, column=0, pady=5, sticky='n')
#app.drop_target_register(DND_FILES)
#app.dnd_bind('<<Drop>>', on_drop)

app.mainloop()