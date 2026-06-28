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

- **Anechoic simulation:** about **0.05° mean error**, robust under heavy background noise.
- **Reverberant room** (image-source simulation + short-window averaging): about **1° mean error** — the method holds up well once realistic echoes are added.

These are controlled simulations with exact ground truth. The next rungs are measured head-related transfer functions and public benchmark recordings (see Roadmap).

## What's here

- `direction_finder.py` — the prototype (run it to see the accuracy test and figure)
- `direction_finder_demo.html` — an interactive demo (open in any browser; drag the slider or press play)
- `doa_accuracy.png` — accuracy of the estimator across angles
- `reverb_test.py` — a tougher test in a simulated reverberant room (image-source method)

## Run it

```
pip install numpy matplotlib
python3 direction_finder.py
```

Or just open `direction_finder_demo.html` in a browser — no install needed.

## Roadmap

Toward research-grade evaluation and lower error:

- A stronger classical estimator (SRP-PHAT) for heavier reverberation
- A small machine-learning model on binaural features
- Evaluation on measured head-related transfer functions (CIPIC / SOFA)
- Evaluation on public benchmarks (DCASE SELD / STARSS, the Wearable SELD dataset)

## Author

Chaemin Song — high-school student, Daejeon, South Korea. Work in progress; feedback and collaboration welcome.
