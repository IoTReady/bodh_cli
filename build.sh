#!/bin/bash
pyoxidizer build --release
mv ./build/x86_64-unknown-linux-gnu/release/install/bodh bodh.bin
