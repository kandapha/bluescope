#!/bin/bash

source venv/bin/activate
streamlit run regis.py --ui.hideTopBar true --server.headless true --runner.fastReruns true --server.runOnSave true --client.toolbarMode developer
