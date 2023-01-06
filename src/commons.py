import math

import numpy as np
from tensor2tensor.data_generators import text_encoder

SF2_PATH = "content/Yamaha-C5-Salamander-JNv5.1.sf2"
SAMPLE_RATE = 16000

_KEY_MAP = [
    "C",
    "Db",
    "D",
    "Eb",
    "E",
    "F",
    "Gb",
    "G",
    "Ab",
    "A",
    "Bb",
    "B",
]

_INSTRUMENT_BY_PATCH_ID = [
    "acoustic grand piano",
    "bright acoustic piano",
    "electric grand piano",
    "honky-tonk piano",
    "electric piano 1",
    "electric piano 2",
    "harpsichord",
    "clavi",
    "celesta",
    "glockenspiel",
    "music box",
    "vibraphone",
    "marimba",
    "xylophone",
    "tubular bells",
    "dulcimer",
    "drawbar organ",
    "percussive organ",
    "rock organ",
    "church organ",
    "reed organ",
    "accordion",
    "harmonica",
    "tango accordion",
    "acoustic guitar (nylon)",
    "acoustic guitar (steel)",
    "electric guitar (jazz)",
    "electric guitar (clean)",
    "electric guitar (muted)",
    "overdriven guitar",
    "distortion guitar",
    "guitar harmonics",
    "acoustic bass",
    "electric bass (finger)",
    "electric bass (pick)",
    "fretless bass",
    "slap bass 1",
    "slap bass 2",
    "synth bass 1",
    "synth bass 2",
    "violin",
    "viola",
    "cello",
    "contrabass",
    "tremolo strings",
    "pizzicato strings",
    "orchestral harp",
    "timpani",
    "string ensemble 1",
    "string ensemble 2",
    "synthstrings 1",
    "synthstrings 2",
    "choir aahs",
    "voice oohs",
    "synth voice",
    "orchestra hit",
    "trumpet",
    "trombone",
    "tuba",
    "muted trumpet",
    "french horn",
    "brass section",
    "synthbrass 1",
    "synthbrass 2",
    "soprano sax",
    "alto sax",
    "tenor sax",
    "baritone sax",
    "oboe",
    "english horn",
    "bassoon",
    "clarinet",
    "piccolo",
    "flute",
    "recorder",
    "pan flute",
    "blown bottle",
    "shakuhachi",
    "whistle",
    "ocarina",
    "lead 1 (square)",
    "lead 2 (sawtooth)",
    "lead 3 (calliope)",
    "lead 4 (chiff)",
    "lead 5 (charang)",
    "lead 6 (voice)",
    "lead 7 (fifths)",
    "lead 8 (bass + lead)",
    "pad 1 (new age)",
    "pad 2 (warm)",
    "pad 3 (polysynth)",
    "pad 4 (choir)",
    "pad 5 (bowed)",
    "pad 6 (metallic)",
    "pad 7 (halo)",
    "pad 8 (sweep)",
    "fx 1 (rain)",
    "fx 2 (soundtrack)",
    "fx 3 (crystal)",
    "fx 4 (atmosphere)",
    "fx 5 (brightness)",
    "fx 6 (goblins)",
    "fx 7 (echoes)",
    "fx 8 (sci-fi)",
    "sitar",
    "banjo",
    "shamisen",
    "koto",
    "kalimba",
    "bag pipe",
    "fiddle",
    "shanai",
    "tinkle bell",
    "agogo",
    "steel drums",
    "woodblock",
    "taiko drum",
    "melodic tom",
    "synth drum",
    "reverse cymbal",
    "guitar fret noise",
    "breath noise",
    "seashore",
    "bird tweet",
    "telephone ring",
    "helicopter",
    "applause",
    "gunshot",
]

_INSTRUMENT_FAMILY_BY_ID = [
    "piano",
    "chromatic percussion",
    "organ",
    "guitar",
    "bass",
    "strings",
    "ensemble",
    "brass",
    "reed",
    "pipe",
    "synth lead",
    "synth pad",
    "synth effects",
    "world",
    "percussive",
    "sound effects",
]

_DRUM_KIT_BY_PATCH_ID = {
    0: "standard kit",
    8: "room kit",
    16: "power kit",
    24: "electronic kit",
    25: "tr-808 kit",
    32: "jazz kit",
    40: "brush kit",
    48: "orchestra kit",
    56: "sound fx kit",
}


def _midi_to_pitch(midi):
    octave = math.floor(midi / 12) - 1
    return _midi_to_pitch_class(midi) + str(octave)


def _midi_to_pitch_class(midi):
    scale_index_to_note = [
        "C",
        "C#",
        "D",
        "D#",
        "E",
        "F",
        "F#",
        "G",
        "G#",
        "A",
        "A#",
        "B",
    ]
    note = midi % 12
    return scale_index_to_note[note]


def _time_to_ticks(time, qpm, ppq):
    return round(((time * qpm) / 60.0) * ppq)


def _time_to_ticks_by_map(time, final_tick_scale, tick_to_time_map):
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
        return tick.item() - 1
    else:
        return tick.item()


# Decode a list of IDs.
def decode(ids, encoder):
    ids = list(ids)
    if text_encoder.EOS_ID in ids:
        ids = ids[: ids.index(text_encoder.EOS_ID)]
    return encoder.decode(ids)


def note_sequence_to_tonejs_midi_json(ns):
    ppq = ns.ticks_per_quarter

    tempos = []
    current_ticks = 0
    tick_scales = [(0, 60.0 / (120.0 * ppq))]
    for i, tempo in enumerate(ns.tempos):
        if i > 0:
            current_ticks += _time_to_ticks(
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
        ns.time_signatures[-1].time if ns.time_signatures else 0,
        ns.key_signatures[-1].time if ns.key_signatures else 0,
        ns.tempos[-1].time if ns.tempos else 0,
    )

    total_quantized_steps = (
        _time_to_ticks(total_time - ns.tempos[-1].time, ns.tempos[-1].qpm, ppq)
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
        ticks = _time_to_ticks_by_map(ts.time, tick_scales[-1][1], tick_to_time_map)

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
        ticks = _time_to_ticks_by_map(ks.time, tick_scales[-1][1], tick_to_time_map)
        key = _KEY_MAP[ks.key]
        scale = "major" if ks.mode == 0 else "minor"
        key_signatures.append({"ticks": ticks, "key": key, "scale": scale})

    if ns.instrument_infos:
        tracks = [
            dict(
                name=info.name,
                notes=[],
                pitchBends=[],
                endOfTrackTicks=0,
                controlChanges={},
            )
            for info in ns.instrument_infos
        ]
    else:
        num_tracks = max(map(lambda n: n.instrument, ns.notes)) + 1
        tracks = [
            dict(
                name="",
                notes=[],
                pitchBends=[],
                endOfTrackTicks=0,
                controlChanges={},
            )
            for _ in range(num_tracks)
        ]

    for note in ns.notes:
        time = note.start_time
        duration = note.end_time - note.start_time
        ticks = _time_to_ticks_by_map(time, tick_scales[-1][1], tick_to_time_map)
        durationTicks = _time_to_ticks_by_map(
            duration, tick_scales[-1][1], tick_to_time_map
        )
        velocity = note.velocity / 127
        midi = note.pitch
        name = _midi_to_pitch(midi)

        tracks[note.instrument]["notes"].append(
            {
                "time": time,
                "duration": duration,
                "ticks": ticks,
                "durationTicks": durationTicks,
                "velocity": velocity,
                "midi": midi,
                "name": name,
            }
        )

        instrument_family = (
            "drums"
            if note.is_drum
            else _INSTRUMENT_FAMILY_BY_ID[math.floor(note.program / 8)]
        )
        instrument_number = note.program
        instrument_name = (
            _DRUM_KIT_BY_PATCH_ID[note.program]
            if note.is_drum
            else _INSTRUMENT_BY_PATCH_ID[note.program]
        )

        tracks[note.instrument]["instrument"] = {
            "family": instrument_family,
            "number": instrument_number,
            "name": instrument_name,
        }

        tracks[note.instrument]["endOfTrackTicks"] = max(
            tracks[note.instrument]["endOfTrackTicks"], ticks + durationTicks
        )

    for cc in ns.control_changes:
        instrument = cc.instrument
        if str(cc.control_number) not in tracks[instrument]["controlChanges"]:
            tracks[instrument]["controlChanges"][str(cc.control_number)] = []

        number = cc.control_number
        time = cc.time
        ticks = _time_to_ticks_by_map(time, tick_scales[-1][1], tick_to_time_map)
        value = cc.control_value / 127
        tracks[instrument]["controlChanges"][str(cc.control_number)].append(
            {"number": number, "ticks": ticks, "time": time, "value": value}
        )

    return {
        "header": {
            "name": "",
            "tempos": tempos,
            "timeSignatures": time_signatures,
            "keySignatures": key_signatures,
            "ppq": ppq,
            "meta": [],
        },
        "tracks": tracks,
    }
