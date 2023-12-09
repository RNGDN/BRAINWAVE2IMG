import numpy as np
import time
from pylsl import StreamInlet, resolve_byprop
import utils

class Band:
    Delta = 0
    Theta = 1
    Alpha = 2
    Beta = 3
    Gamma = 4

BUFFER_LENGTH = 5
EPOCH_LENGTH = 1
OVERLAP_LENGTH = 0.8
SHIFT_LENGTH = EPOCH_LENGTH - OVERLAP_LENGTH
INDEX_CHANNEL = [0]

def select_word(gamma_value, words_file):
    try:
        with open(words_file, 'r') as file:
            words = file.readlines()
            words = [word.strip() for word in words]
    except Exception as e:
        print(f"Error reading words file: {e}")
        return None

    min_gamma, max_gamma = -0.15, 1 
    scale = (max_gamma - min_gamma) / (len(words) - 1) 

    gamma_value = max(min_gamma, min(gamma_value, max_gamma))

    index = int((gamma_value - min_gamma) / scale)
    index = max(0, min(index, len(words) - 1)) 
    return words[index]



def write_word_to_file(word, file_path, gamma_value):
    try:
        with open(file_path, 'a') as file:
            file.write(word + '\n')
        print(f"Gamma Value: {gamma_value:.3f}, Added word to prompt.txt: {word}")
    except Exception as e:
        print(f"Error writing to file: {e}")

def clear_file_if_too_long(file_path, max_lines=50):
    try:
        with open(file_path, 'r+') as file:
            lines = file.readlines()
            if len(lines) > max_lines:
                file.seek(0)
                file.truncate()
    except Exception as e:
        print(f"Error managing file {file_path}: {e}")

if __name__ == "__main__":
    print('Looking for an EEG stream...')
    streams = resolve_byprop('type', 'EEG', timeout=2)
    if len(streams) == 0:
        raise RuntimeError('Can\'t find EEG stream.')

    print("Start acquiring data")
    inlet = StreamInlet(streams[0], max_chunklen=12)
    info = inlet.info()
    fs = int(info.nominal_srate())

    eeg_buffer = np.zeros((int(fs * BUFFER_LENGTH), 1))
    filter_state = None
    n_win_test = int(np.floor((BUFFER_LENGTH - EPOCH_LENGTH) / SHIFT_LENGTH + 1))
    band_buffer = np.zeros((n_win_test, 5))

    words_file = 'C:\\Users\\harry\\OneDrive\\Desktop\\Code\\words.txt'
    prompt_file = "C:\\Users\\harry\\OneDrive\\Desktop\\Code\\prompt.txt"

    stream_connected = True



try:
    while True:
        eeg_data, timestamp = inlet.pull_chunk(timeout=1, max_samples=int(SHIFT_LENGTH * fs))

        if not eeg_data:  
            print("No data received. EEG stream might be disconnected.")
            break 

        ch_data = np.array(eeg_data)[:, INDEX_CHANNEL]
        eeg_buffer, filter_state = utils.update_buffer(eeg_buffer, ch_data, notch=True, filter_state=filter_state)

        data_epoch = utils.get_last_data(eeg_buffer, EPOCH_LENGTH * fs)
        band_powers = utils.compute_band_powers(data_epoch, fs)
        band_buffer, _ = utils.update_buffer(band_buffer, np.asarray([band_powers]))
        gamma_value = band_buffer[-1, Band.Gamma]

        selected_word = select_word(gamma_value, words_file)
        if selected_word:
            clear_file_if_too_long(prompt_file) 
            write_word_to_file(selected_word, prompt_file, gamma_value) 

        time.sleep(1)

except Exception as e:
    print(f"Error with the stream: {e}")

except KeyboardInterrupt:
    print('Manually stopped.')

print('Program terminated.')
