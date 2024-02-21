# import redis

import streamlit as st

from streamlit_javascript import st_javascript

from src.common import get


def charge_user(amount: int = None):
    if amount is None:
        amount = st.session_state.token_cost_accumulator

    sats_left = st.session_state.redis_conn.decrby(get('username'), amount)
    st.session_state.token_cost_accumulator = 0
    return sats_left



def load_sats_balance():
    return int(st.session_state.redis_conn.get(st.session_state.username) or 0)


def add_sats(amount: int):
    # current_sats = int(st.session_state.redis_conn.get(st.session_state.username) or 0)
    # new_sats = current_sats + amount
    # st.session_state.redis_conn.set(st.session_state.username, new_sats)

    await_payment()





    


# def await_payment():
#     # html = """
#     # <button id="pay">Pay</button>
#     # <p>Invoice: <span id="invoice"></span></p>
#     # <p>Status: <span id="status">unpaid</span></p>

#     # <script>
#     # document.getElementById("pay").addEventListener("click", function() {
#     #     document.getElementById("status").innerText = "paid";
#     # });
#     # </script>
#     # """

#     # st.components.v1.html(html)
#     # st.markdown(html, unsafe_allow_html=True) # this displays the button, but the javascript doesn't work


#     # st.components.v1.html("""<script src="https://unpkg.com/@getalby/lightning-tools"></script>""")

#     st.components.v1.html("""<script type="module">
#         import { LightningAddress } from "https://esm.sh/@getalby/lightning-tools@5.0.0"; // jsdelivr.net, skypack.dev also work
#         """)


#     sample = """await fetch("https://reqres.in/api/products/3").then(function(response) {
#         return response.json();
#     }) """

#     # javascript = """const ln = new LightningAddress("turkeybiscuit@getalby.com");
#     #     const invoice = ln.requestInvoice({ satoshi: 1000 });
#     #     console.log("Invoice: ", invoice);

#     #     // or use the convenenice method:
#     #     // return invoice.isPaid();
#     #     return 10
#     # """

#     javascript = """(async () => {
#         console.log("hi")
#         console.log(new LightningAddress("turkeybiscuit@getalby.com"))
#         const ln = new LightningAddress("hello@getalby.com");
#         await ln.fetch();
#         console.log(ln.lnurlpData);
#         })();
#     """

#     return_value = st_javascript(javascript)

#     st.markdown(f"Return value was: {return_value}")
#     print(f"Return value was: {return_value}")

#     import time
#     time.sleep(1)




def await_payment():
    import requests

    pr = """lnbc1u1pjava5dpp5mg8du4vqnr4lqtlgrja5ml7t0qmcszsswj050zeff5kz5fzttytqhp5fwml5q5dckdwq4c2njau2jc9prswd0q43t5aauwv56zwdgw6h6pscqzzsxqyz5vqsp5pmljg7dg5rg38ww44c23w7lv86cru63x4qem63n2q6sn5xh55n0q9qyyssqmtq8a5stf46hshr9s269egpcp63rhg85jdszh7yxskc2tj05f03qm3y2zsatapv5hg3m4act8t9j7fqtc27n0m96n6wsnnxy9s8wf7sqdf5fg6"""

    html = f"""<a href="lightning:{pr}" target="_blank">Pay with Lightning</a>"""
    st.markdown(html, unsafe_allow_html=True)
