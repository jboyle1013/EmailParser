#!/bin/bash


docker exec email-preprocessing bash -c "python3 ~/EmailParser/startbycron.py True"

rm -rf //email-analysis-data/new-emails/*