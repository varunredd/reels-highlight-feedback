import ffmpeg
import librosa
import numpy as np

def extract_audio_from_video(video_file: str, audio_file: str):
    (
        ffmpeg
        .input(video_file)
        .output(audio_file, format="mp3", acodec="mp3", ac=1, ar="16000")
        .overwrite_output()
        .run()
    )

def align_to_silence(audio_path: str, start_s: float, end_s: float,
                     pre_window=1.2, post_window=1.2,
                     rms_thresh_db=-35.0, min_silence_len=0.15):
    """
    Move start left to nearest silence, and end right to nearest silence.
    rms_thresh_db: dBFS threshold considered "silence".
    """
    y, sr = librosa.load(audio_path, sr=None)
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=512)

    # Convert dB threshold
    rms_db = librosa.amplitude_to_db(rms + 1e-9, ref=1.0)

    def nearest_silence(t_target, direction):
        # direction: -1 for backward search, +1 for forward
        if direction == -1:
            t0, t1 = max(0.0, t_target - pre_window), t_target
        else:
            t0, t1 = t_target, min(times[-1], t_target + post_window)

        mask = (times >= t0) & (times <= t1)
        cand_idx = np.where(mask)[0]
        if len(cand_idx) == 0: return t_target

        idxs = cand_idx if direction == +1 else cand_idx[::-1]
        recent_start = None
        for i in idxs:
            if rms_db[i] < rms_thresh_db:
                # accumulate consecutive silence frames
                if recent_start is None:
                    recent_start = times[i]
                # check if silence long enough
                if times[i] - recent_start >= min_silence_len:
                    return recent_start if direction == -1 else times[i]
            else:
                recent_start = None
        return t_target

    new_start = nearest_silence(start_s, -1)
    new_end   = nearest_silence(end_s, +1)
    if new_end <= new_start:  # safety
        new_start, new_end = start_s, end_s
    return round(new_start, 3), round(new_end, 3)
