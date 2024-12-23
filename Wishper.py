import streamlit as st
import sounddevice as sd
import wave
import whisper
import os

# Function to record audio from microphone
def record_audio(file_path, duration=5, samplerate=44100):
    st.info("Recording... Speak now!")  # (録音しています...今話してください！) (Recording... Speak now!)
    try:
        # Record audio (Mono - 1 channel)
        recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype="int16")
        sd.wait()  # Wait for the recording to finish

        # Save the recorded audio as a WAV file
        with wave.open(file_path, "wb") as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(samplerate)
            wf.writeframes(recording.tobytes())

        st.success("Recording complete! Audio saved.")  # (録音が完了しました！音声が保存されました。) (Recording complete! Audio saved.)
    except Exception as e:
        st.error(f"Error during recording: {e}")  # (録音中にエラーが発生しました：{e}) (Error during recording: {e})
        return False
    return True

# Function to transcribe audio using Whisper
def transcribe_audio(file_path):
    model = whisper.load_model("base", device="cpu")
    result = model.transcribe(file_path, fp16=False)
    return result["language"], result["text"]

# Function to save transcription to a text file
def save_transcription(text, file_name="transcription.txt"):
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(text)
    return file_name

# Streamlit App
def main():
    # Title and description
    st.markdown("""
        <h1 style='text-align: center; color: #f63366; font-size: 50px;'>
        日本語の音声認識システムと文字起こし  # (Japanese Speech Recognition System with Transcription)
        </h1>
    """, unsafe_allow_html=True)

    st.write("やりたいことを選んでください：音声を録音するか、ファイルをアップロードする")  # (Select the action you want to perform: record audio or upload a file)

    # Custom CSS to increase font size and center headings
    st.markdown("""
        <style>
        .big-font {
            font-size:36px !important;
            font-weight: bold;
            text-align: center;
        }
        .highlight-box {
            border: 2px solid #f63366;
            padding: 20px;
            margin: 20px 0;
            border-radius: 10px;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    # Dropdown to select action
    option = st.selectbox("アクションを選んでください：", ["音声を録音する", "音声ファイルをアップロードする"])  # (Choose an action: record audio and upload audio file)

    if option == "音声を録音する":
        # Record Audio
        st.markdown("<div class='highlight-box'><span class='big-font'>🎙️ 音声を録音する</span></div>", unsafe_allow_html=True)  # (Record Audio)
        duration = st.slider("録音時間を選んでください（秒）:", min_value=3, max_value=60, value=5)  # (Select recording duration (seconds))
        record_button = st.button("録音を開始する")  # (Start recording)

        if record_button:
            recorded_file = "recorded_audio.wav"
            success = record_audio(recorded_file, duration=duration)

            if success and os.path.exists(recorded_file):
                st.info("Transcribing audio...")  # (音声を文字起こししています...) (Transcribing audio...)
                detected_language, transcription_text = transcribe_audio(recorded_file)
                st.write(f"**Detected Language:** {detected_language}")
                st.subheader("Transcription:")
                st.write(transcription_text)

                transcription_file = save_transcription(transcription_text)
                st.download_button(
                    label="文字起こしをダウンロード",  # (Download Transcription)
                    data=open(transcription_file, "rb"),
                    file_name="transcription.txt",
                    mime="text/plain"
                )

                os.remove(recorded_file)

    elif option == "音声ファイルをアップロードする":
        # Upload File
        st.markdown("<div class='highlight-box'><span class='big-font'>📂 音声ファイルをアップロードする</span></div>", unsafe_allow_html=True)  # (Upload audio file)
        uploaded_file = st.file_uploader("音声ファイルをアップロードする", type=["mp3", "wav", "m4a"])  # (Upload an audio file)

        if uploaded_file is not None:
            uploaded_file_path = "uploaded_audio.wav"
            with open(uploaded_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("ファイルがアップロードされました！")  # (File uploaded successfully!)

            if st.button("アップロードしたファイルを文字起こしする"):  # (Transcribe Uploaded File)
                st.info("音声を文字起こししています...")  # (Transcribing audio...)
                detected_language, transcription_text = transcribe_audio(uploaded_file_path)
                st.write(f"**Detected Language:** {detected_language}")
                st.subheader("Transcription:")
                st.write(transcription_text)

                transcription_file = save_transcription(transcription_text)
                st.download_button(
                    label="文字起こしをダウンロード",  # (Download Transcription)
                    data=open(transcription_file, "rb"),
                    file_name="transcription.txt",
                    mime="text/plain"
                )

                os.remove(uploaded_file_path)

if __name__ == "__main__":
    main()
