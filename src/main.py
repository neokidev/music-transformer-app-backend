from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from note_seq.midi_io import midi_file_to_note_sequence

from examples import (_230_bpm_multitrack, beat, pitch_bend_test,
                      tchaikovsky_seasons)
from examples.bach import bach_846, bach_847, bach_850, bach_format0
from examples.beethoven import symphony_7_2, symphony_7_2_singletrack
from examples.debussy import (childrens_corner_1, childrens_corner_2,
                              childrens_corner_3, childrens_corner_4,
                              childrens_corner_5, claire_de_lune, menuet,
                              passepied, prelude)
from examples.joplin import the_entertainer
from src.commons import note_sequence_to_tonejs_midi_json
from src.generate_from_unconditional_model import \
    generate_from_unconditional_model as generate_from_unconditional_model_fn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/examples/230-bpm-multitrack")
async def examples_230_bpm_multitrack():
    return _230_bpm_multitrack


@app.get("/examples/beat")
async def examples_beat():
    return beat


@app.get("/examples/pitch-bend-test")
async def examples_pitch_bend_test():
    return pitch_bend_test


@app.get("/examples/tchaikovsky-seasons")
async def examples_tchaikovsky_seasons():
    return tchaikovsky_seasons


@app.get("/examples/bach/bach-846")
async def examples_bach_846():
    return bach_846


@app.get("/examples/bach/bach-847")
async def examples_bach_847():
    return bach_847


@app.get("/examples/bach/bach-850")
async def examples_bach_850():
    return bach_850


@app.get("/examples/bach/bach-format0")
async def examples_bach_format0():
    return bach_format0


@app.get("/examples/beethoven/symphony-7-2-singletrack")
async def examples_symphony_7_2_singletrack():
    return symphony_7_2_singletrack


@app.get("/examples/beethoven/symphony-7-2")
async def examples_symphony_7_2():
    return symphony_7_2


@app.get("/examples/debussy/childrens-corner-1")
async def examples_childrens_corner_1():
    return childrens_corner_1


@app.get("/examples/debussy/childrens-corner-2")
async def examples_childrens_corner_2():
    return childrens_corner_2


@app.get("/examples/debussy/childrens-corner-3")
async def examples_childrens_corner_3():
    return childrens_corner_3


@app.get("/examples/debussy/childrens-corner-4")
async def examples_childrens_corner_4():
    return childrens_corner_4


@app.get("/examples/debussy/childrens-corner-5")
async def examples_childrens_corner_5():
    return childrens_corner_5


@app.get("/examples/debussy/claire-de-lune")
async def examples_claire_de_lune():
    return claire_de_lune


@app.get("/examples/debussy/menuet")
async def examples_menuet():
    return menuet


@app.get("/examples/debussy/passepied")
async def examples_passepied():
    return passepied


@app.get("/examples/debussy/prelude")
async def examples_prelude():
    return prelude


@app.get("/examples/joplin/the-entertainer")
async def examples_the_entertainer():
    return the_entertainer


@app.get("/tests/bach/bach-846")
async def tests_bach_846():
    midi_file = "examples/bach/bach_846.mid"
    ns = midi_file_to_note_sequence(midi_file)
    return note_sequence_to_tonejs_midi_json(ns)


@app.get("/generate-from-unconditional-model")
async def generate_from_unconditional_model():
    return generate_from_unconditional_model_fn()
