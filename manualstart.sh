#!/bin/bash


docker exec email-preprocessing bash -c "python3 ~/EmailParser/manualstart.py True"

rm -rf //email-analysis-data/new-emails/*