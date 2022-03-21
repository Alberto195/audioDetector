import os

import PySimpleGUI as sg
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence


def make_window(theme):
    sg.theme(theme)
    menu_def = [['&Application', ['E&xit']],
                ['&Help', ['&About']]]
    right_click_menu_def = [[], ['Edit Me', 'Versions', 'Nothing', 'More Nothing', 'Exit']]
    graph_right_click_menu_def = [[], ['Erase', 'Draw Line', 'Draw', ['Circle', 'Rectangle', 'Image'], 'Exit']]

    # Table Data
    data = [["John", 10], ["Jen", 5]]
    headings = ["Name", "Score"]

    popup_layout = [[sg.Text("Choose audio to transcribe")],
                    [sg.Button("Open File")],
                    ]

    layout = [
        [sg.TabGroup([[sg.Tab('wav files', popup_layout)]], key='-TAB GROUP-', expand_x=True, expand_y=True)],
    ]

    layout[-1].append(sg.Sizegrip())
    window = sg.Window('Audio Detector demo', layout, right_click_menu=right_click_menu_def,
                       right_click_menu_tearoff=True, grab_anywhere=True, resizable=True, margins=(0, 0),
                       use_custom_titlebar=True, finalize=True, keep_on_top=True,
                       # scaling=2.0,
                       )
    window.set_min_size(window.size)
    return window


def main():
    window = make_window(sg.theme())

    # This is an Event Loop
    while True:
        event, values = window.read(timeout=100)
        # keep an animation running so show things are happening
        if event not in (sg.TIMEOUT_EVENT, sg.WIN_CLOSED):
            print('============ Event = ', event, ' ==============')
            print('-------- Values Dictionary (key=value) --------')
            for key in values:
                print(key, ' = ', values[key])
        if event in (None, 'Exit'):
            print("[LOG] Clicked Exit!")
            break
        elif event == "Open File":
            print("[LOG] Clicked Open File!")
            folder_or_file = sg.popup_get_file('Choose your file', keep_on_top=True)
            if str(folder_or_file) != "None" and str(folder_or_file).__contains__('.wav'):
                sg.popup_animated(image_source=sg.DEFAULT_BASE64_LOADING_GIF, time_between_frames=100, keep_on_top=True, message='Transcribing')
                folder_or_file = get_large_audio_transcription(str(folder_or_file))
                sg.popup("Transcription: " + str(folder_or_file), keep_on_top=True)
            else:
                sg.popup("Transcription: Need .wav file", keep_on_top=True)
            print("[LOG] User chose file: " + str(folder_or_file))

    window.close()
    exit(0)


def get_large_audio_transcription(path):
    """
    Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks
    """
    r = sr.Recognizer()
    # open the audio file using pydub
    sound = AudioSegment.from_wav(path)
    # split audio sound where silence is 700 miliseconds or more and get chunks
    chunks = split_on_silence(sound,
                              # experiment with this value for your target audio file
                              min_silence_len=500,
                              # adjust this per requirement
                              silence_thresh=sound.dBFS - 14,
                              # keep the silence for 1 second, adjustable as well
                              keep_silence=500,
                              )
    folder_name = "audio-chunks"
    # create a directory to store the audio chunks
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    whole_text = ""
    # process each chunk
    for i, audio_chunk in enumerate(chunks, start=1):
        # export audio chunk and save it in
        # the `folder_name` directory.
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        # recognize the chunk
        with sr.AudioFile(chunk_filename) as source:
            audio_listened = r.record(source)
            # try converting it to text
            try:
                text = r.recognize_google(audio_listened)
            except sr.UnknownValueError as e:
                print("Error:", str(e))
            else:
                text = f"{text.capitalize()}. "
                print(chunk_filename, ":", text)
                whole_text += text
    # return the text for all chunks detected
    return whole_text


if __name__ == '__main__':
    sg.theme('black')
    sg.theme('dark red')
    sg.theme('dark green 7')
    # sg.theme('DefaultNoMoreNagging')
    main()
