# `animal-soup-lite` User Manual

Welcome to `animal-soup-lite`! 

This purpose of this library is automated detection of the Hantman Lab reach-to-grab task using simple bounding box detection of the **side** video camera. 

Currently, the library has functionality for detecting two behavioral motifs: lift and grab (hopefully, more to come later). 

## How-to-use 

After installing the library (see the README), you can simply run the `run_detection.py` script, passing in the path (locally or on wasabi) to the session's videos. 

The expected format of your video is that they are stored in a single folder and are titled as followed: `[animal_id]_[recording_date]_v[trial_num]`. For example: `rb69_20260303_v001.avi`, `rb69_20260303_v002.avi`, ...

The output of running this script is a `.pkl` file containing the following:

`[trial_num]    [lift_frame]    [lift_ms]   [grab_frame]    [grab_ms]`

**NOTE:** `lift_ms` and `grab_ms` are the millisecond detection relative to cue. Cue is assume happen at frame 500 (i.e 1s into the trial).

## Auto Mode using bounding boxes

[//]: # (insert button diagram)

## Manual Mode using key modifiers