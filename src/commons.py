import math

import numpy as np
from note_seq import note_sequence_to_pretty_midi
from note_seq.midi_io import note_sequence_to_pretty_midi
from pretty_midi.containers import TimeSignature
from tensor2tensor.data_generators import text_encoder

SF2_PATH = "content/Yamaha-C5-Salamander-JNv5.1.sf2"
SAMPLE_RATE = 16000


KEY_MAP = [
    # "Cb",
    "C",
    # "C#",
    "Db",
    "D",
    "Eb",
    "E",
    "F",
    # "F#",
    "Gb",
    "G",
    "Ab",
    "A",
    "Bb",
    "B",
]


def time_to_ticks(time, qpm, ppq):
    return round(((time * qpm) / 60.0) * ppq)


# Decode a list of IDs.
def decode(ids, encoder):
    ids = list(ids)
    if text_encoder.EOS_ID in ids:
        ids = ids[: ids.index(text_encoder.EOS_ID)]
    return encoder.decode(ids)


def _time_to_tick(time, final_tick_scale, tick_to_time_map):
    # Find the index of the ticktime which is smaller than time
    tick = np.searchsorted(tick_to_time_map, time, side="left")
    # If the closest tick was the final tick in tick_to_time_map...
    if tick == len(tick_to_time_map):
        # start from time at end of tick_to_time_map
        tick -= 1
        # Add on ticks assuming the final tick_scale amount
        tick += (time - tick_to_time_map[tick]) / final_tick_scale
        # Re-round/quantize
        return int(round(tick))
    # If the tick is not 0 and the previous ticktime in a is closer to time
    if tick and (
        math.fabs(time - tick_to_time_map[tick - 1])
        < math.fabs(time - tick_to_time_map[tick])
    ):
        # Decrement index by 1
        return tick - 1
    else:
        return tick


def note_sequence_to_tonejs_midi_json(ns):
    pm = note_sequence_to_pretty_midi(ns)
    ppq = ns.ticks_per_quarter

    tempos = []
    current_ticks = 0
    tick_scales = [(0, 60.0 / (120.0 * ppq))]
    for i, tempo in enumerate(ns.tempos):
        if i > 0:
            current_ticks += time_to_ticks(
                tempo.time - ns.tempos[i - 1].time,
                ns.tempos[i - 1].qpm,
                ppq,
            )

        tempos.append({"ticks": current_ticks, "bpm": tempo.qpm})

        if current_ticks == 0:
            tick_scales = [(0, 60.0 / (tempo.qpm * ppq))]
        else:
            _, last_tick_scale = tick_scales[-1]
            tick_scale = 60.0 / (tempo.qpm * ppq)
            if tick_scale != last_tick_scale:
                tick_scales.append((current_ticks, tick_scale))

    total_time = max(
        ns.total_time,
        ns.time_signatures[-1].time,
        ns.key_signatures[-1].time,
        ns.tempos[-1].time,
    )

    total_quantized_steps = (
        time_to_ticks(total_time - ns.tempos[-1].time, ns.tempos[-1].qpm, ppq)
        + tempos[-1]["ticks"]
    )

    tick_to_time_map = np.zeros(total_quantized_steps + 1)
    last_end_time = 0
    for (start_tick, tick_scale), (end_tick, _) in zip(
        tick_scales[:-1], tick_scales[1:]
    ):
        ticks = np.arange(end_tick - start_tick + 1)

        tick_to_time_map[start_tick : end_tick + 1] = last_end_time + tick_scale * ticks
        last_end_time = tick_to_time_map[end_tick]

    start_tick, tick_scale = tick_scales[-1]
    ticks = np.arange(total_quantized_steps + 1 - start_tick)
    tick_to_time_map[start_tick:] = last_end_time + tick_scale * ticks

    time_signatures = []
    for i, ts in enumerate(ns.time_signatures):
        ticks = _time_to_tick(ts.time, tick_scales[-1][1], tick_to_time_map)

        time_signatures.append(
            {"ticks": ticks, "timeSignature": [ts.numerator, ts.denominator]}
        )

    for i, ts in enumerate(time_signatures):
        last_event = time_signatures[i - 1] if i > 0 else time_signatures[0]
        elapsed_beats = (ts["ticks"] - last_event["ticks"]) / ppq
        elapsed_measures = int(
            elapsed_beats
            / last_event["timeSignature"][0]
            / (last_event["timeSignature"][1] / 4)
        )

        if "measures" not in last_event:
            last_event["measures"] = 0

        time_signatures[i]["measures"] = elapsed_measures + last_event["measures"]

    key_signatures = []
    for i, ks in enumerate(ns.key_signatures):
        ticks = _time_to_tick(ks.time, tick_scales[-1][1], tick_to_time_map)
        key = KEY_MAP[ks.key]
        scale = "major" if ks.mode == 0 else "minor"
        key_signatures.append({"ticks": ticks, "key": key, "scale": scale})

    return {
        "header": {
            "tempos": tempos,
            "timeSignatures": time_signatures,
            "keySignatures": key_signatures,
            "meta": "not_implemented",
            "name": "not_implemented",
            "ppq": ppq,
        },
        "tracks": "not_implemented",
    }
