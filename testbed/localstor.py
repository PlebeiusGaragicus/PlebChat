import streamlit as st
from streamlit_ws_localstorage import injectWebsocketCode, getOrCreateUID

# from streamlit_ws_localstorage import websocket_server.ws
from streamlit_ws_localstorage.websocket_server.ws_server import server as websocket_server

# Main call to the api, returns a communication object
# conn = injectWebsocketCode(hostPort='linode.liquidco.in', uid=getOrCreateUID())
# websocket_server.

st.write('setting into localStorage')
ret = websocket_server.setLocalStorageVal(key='k1', val='v1')
st.write('ret: ' + ret)

st.write('getting from localStorage')
ret = websocket_server.getLocalStorageVal(key='k1')
st.write('ret: ' + ret)
