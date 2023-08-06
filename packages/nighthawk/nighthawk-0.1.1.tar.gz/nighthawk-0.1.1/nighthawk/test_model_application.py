from pathlib import Path
import gc
import time

import tensorflow as tf


PACKAGE_DIR_PATH = Path(__file__).parent
MODEL_DIR_PATH = PACKAGE_DIR_PATH / 'saved_model_with_preprocessing'

RECORDING_DURATION = 16000
HOP_DURATION = .2
RECORD_COUNT = int(round(RECORDING_DURATION / HOP_DURATION))
RECORD_SIZE = 22050
MESSAGE_PERIOD = 128
CHUNK_DURATION = 800
CHUNK_RECORD_COUNT = int(round(CHUNK_DURATION / HOP_DURATION))


def main():

    print('Initializing...')
    model = load_model()
    samples = get_samples()

#     time_processing(apply_model_and_retain_results, model, samples)
#     time_processing(apply_model_and_retain_result_chunks, model, samples)
    time_processing(apply_model_and_discard_results, model, samples)


def load_model():
    return tf.saved_model.load(MODEL_DIR_PATH)


def get_samples():
    return tf.random.uniform((RECORD_SIZE,), minval=-.9, maxval=.9)


def time_processing(function, *args):

    print('Applying model to samples...')

    start_time = time.time()

    function(*args)

    end_time = time.time()
    elapsed_time = end_time - start_time
    speed = RECORDING_DURATION / elapsed_time

    print(
        f'Processed {RECORDING_DURATION} seconds of audio in '
        f'{elapsed_time} seconds, {speed:.1f} times faster than '
        f'real time.')


def apply_model_and_retain_results(model, samples):

    results = []

    start_time = time.time()
	
    for i in range(RECORD_COUNT):

        if i != 0 and i % MESSAGE_PERIOD == 0:
#             print(i * HOP_DURATION)
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            speed = MESSAGE_PERIOD * HOP_DURATION / elapsed_time
            print(f'pos:{i * HOP_DURATION:.2f}\tspeed:{speed:.2f}')
            start_time = time.time()

        
        results.append(model(samples))


def apply_model_and_retain_result_chunks(model, samples):

	start_time = time.time()
	for i in range(RECORD_COUNT):

		if i != 0 and i % MESSAGE_PERIOD == 0:
# 			print(i * HOP_DURATION)

			end_time = time.time()
			elapsed_time = end_time - start_time
			speed = MESSAGE_PERIOD * HOP_DURATION / elapsed_time
			print(f'pos:{i * HOP_DURATION:.2f}\tspeed:{speed:.2f}')
			start_time = time.time()

		if i % CHUNK_RECORD_COUNT == 0:
			print('discarding results...')
			results = []
			gc.collect()
			print('clearing session...')
			tf.keras.backend.clear_session()


		results.append(model(samples))


def apply_model_and_discard_results(model, samples):

    results = []

    start_time = time.time()
	
    for i in range(RECORD_COUNT):

        if i != 0 and i % MESSAGE_PERIOD == 0:
#             print(i * HOP_DURATION)
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            speed = MESSAGE_PERIOD * HOP_DURATION / elapsed_time
            print(f'pos:{i * HOP_DURATION:.2f}\tspeed:{speed:.2f}')
            start_time = time.time()
            
        model(samples)
        
        


if __name__ == '__main__':
    main()
