# Pulse Lighting Pro

An early engineering prototype for moving-head stage lighting control. **Version 0.1 is not production-ready or hardware-verified.**

## Features implemented

- Basic 8-bit pan, tilt, dimmer, RGBW control with a 2D simulated preview
- Custom channel-offset mapping for identical fixtures
- Sequential multi-universe patching (fixtures do not cross universe boundaries)
- Save/recall scenes and export/import JSON projects
- Static, slow sweep and circle effects
- Experimental Art-Net unicast and ENTTEC DMX USB Pro outputs
- Blackout button (software-only; not a guaranteed emergency stop)

## Run

Install Python 3.10 or newer with Tkinter support. From the repository directory:

```bash
python app.py
```

On macOS/Linux use `python3 app.py`. Linux may need its distribution's `python3-tk` package.

ENTTEC serial output additionally requires:

```bash
python -m pip install pyserial
```

Start in **Simulation** mode. For any real fixture, verify its manufacturer-provided channel mapping, fixture footprint, and starting address before setting channel offsets. Apply the patch while disarmed; hardware output requires a separate arm action and initially starts in blackout state. Art-Net targets UDP port 6454 with a zero-based universe number. ENTTEC output supports one universe in this prototype.

## Hardware safety

**Do not use during a live event.** Begin with simulation, then test with a single isolated fixture in a clear movement area and an independent physical disconnect/blackout. The software does not discover fixtures automatically; never guess a DMX channel assignment. The blackout only zeros mapped dimmer channels, which is not safe for every fixture. A crash or disconnection can leave fixtures at the last transmitted state. There is no watchdog, fail-safe guarantee, hardware test evidence, shutter mapping, or RDM discovery.

## Roadmap

- Verified fixture profiles, RDM discovery and guided identification for non-RDM devices
- 16-bit movement, per-fixture control, groups, bounded motion and robust safety interlocks
- sACN, OSC, MIDI, Companion, ProPresenter, OBS and DAW integrations
- Audio-responsive effects, timeline control and optional intelligent scene suggestions
- Native, efficient desktop engine and cross-platform installers

This first prototype uses Python/Tkinter; CPU/RAM consumption has not been benchmarked. Features in the roadmap are not implemented yet.
