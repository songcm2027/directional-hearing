# Directional Hearing — an earbud-based sound direction finder

A prototype that helps people with single-sided deafness sense **which direction** a sound is coming from, using the two microphones in a pair of earbuds.

## Why

I have single-sided deafness, so I hear with one ear and can't tell which direction a sound comes from — a real safety problem near traffic. This project recovers that missing sense of direction computationally.

## How it works

Two earbuds sit on opposite sides of the head (~18 cm apart), forming a binaural microphone array. The tiny difference in *when* a sound reaches each ear (the inter-ear delay) encodes its direction. The code:

1. Estimates the inter-ear delay with **GCC-PHAT** (generalized cross-correlation with phase transform).
2. Converts that delay to an angle: `angle = arcsin(delay × c / d)`.
3. Cues the user to the correct side.

## Results

In idealized (anechoic) simulation, the estimator reaches about **0.05° mean error** and stays accurate under heavy background noise. These are upper-bound numbers from a clean simulation — the next step is testing on reverberation and real recordings.

## What's here

- `direction_finder.py` — the prototype (run it to see the accuracy test and figure)
- `direction_finder_demo.html` — an interactive demo (open in any browser; drag the slider or press play)
- `doa_accuracy.png` — accuracy of the estimator across angles

## Run it

```
pip install numpy matplotlib
python3 direction_finder.py
```

Or just open `direction_finder_demo.html` in a browser — no install needed.

## Author

Chaemin Song — high-school student, Daejeon, South Korea. Work in progress; feedback and collaboration welcome.
