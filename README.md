
## Quick Start

```sh
# Make VirtualEnv
$ virtualenv -p $(which python) venv
$ source venv/bin/activate
$ pip install -r requirements.txt

# Run the app
$ streamlit run regis.py
# --ui.hideTopBar BOOLEAN
# --client.showSidebarNavigation BOOLEAN
# --runner.fastReruns BOOLEAN 
# --server.headless BOOLEAN 
# --server.runOnSave BOOLEAN 
# --server.enableXsrfProtection BOOLEAN
# --server.enableCORS BOOLEAN
# --browser.serverAddress TEXT  #  CORS and XSRF protection purposes
# --browser.serverPort INTEGER
$ streamlit run regis.py --ui.hideTopBar true --runner.fastReruns true --server.runOnSave true
```
