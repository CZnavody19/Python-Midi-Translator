Python-Midi-Translator
======================
Translates midi messages to key presses and volume control.


## Config
The configuration is very simple. Below is a example...

```yml (config.yml)
setup:
  port: 0

PAD:
  36: F8
  37: "play/pause media"

POT:
  1: main
  2: Discord
  3: Chrome
```
We set the midi port to port zero and set the inividual actions.
So when Pad no. 36 is pressed the F8 key will be pressed.

The config has to be placed in the same directory as the program!
