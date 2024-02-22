import os
import json
import requests

import streamlit as st

from src.common import set, get, not_init, INVOICES_PATH

TOKENS_PER_SAT = 30

# https://guides.getalby.com/developer-guide/v/alby-wallet-api/lightning-address-details-proxy



def charge_user(amount: int = None):
    if amount is None:
        amount = st.session_state.token_cost_accumulator

    sats_left = st.session_state.redis_conn.decrby(get('username'), amount)
    st.session_state.token_cost_accumulator = 0
    return sats_left



def load_sats_balance():
    return int(st.session_state.redis_conn.get(st.session_state.username) or 0)

    


def display_invoice_link():
    payment_request = get('invoice')['pr']

    # html = f"""<a href="lightning:{payment_request}" target="_blank">Buy tokens with Lightning ⚡️</a>"""
    html = f"""<a href="lightning:{payment_request}" target="_blank">Click to pay with Lightning ⚡️</a>"""
    st.markdown(html, unsafe_allow_html=True)
    invoice_number = payment_request[:6] + "..." + payment_request[-6:]
    st.write(f"Invoice: :green[{invoice_number}]")

    if st.button("Check for payment status"):
        if check_for_payment():
            archive_invoice()




def create_invoice_file(sats: int = 100):

    ln_address = "turkeybiscuit@getalby.com"
    url = "https://api.getalby.com/lnurl/generate-invoice"
    params = {
        "ln": ln_address,
        "amount": sats * 1000, # in millisats
         "comment": f"Purchased {sats * TOKENS_PER_SAT} PlebChat tokens (chat.plebby.me) 🗣️🤖💬"
    }

    response = requests.get(url, params=params)


    if response.status_code == 200:
        st.toast("Invoice created! 🎉")
        print("CREATED INVOICE:")
        print(response.json())
    else:
        st.error(f"Failed to create invoice: {response.status_code} {response.text}")
        st.toast(f"Failed to create invoice: {response.status_code} {response.text}")
        raise Exception(f"Failed to create invoice: {response.status_code} {response.text}")

    invoice_filename = f"{INVOICES_PATH}/{get('username')}.invoice"
    with open(invoice_filename, "w") as f:
        f.write(json.dumps(response.json()))

    st.session_state.invoice = response.json()['invoice']
    # st.rerun()
    # return response.json()


def return_stored_invoice():
    invoice_filename = f"{INVOICES_PATH}/{get('username')}.invoice"

    try:
        with open(invoice_filename, "r") as f:
            invoice = json.load(f)['invoice']
            print("INVOICE FILE FOUND:")
            print(invoice)
            return invoice

    except FileNotFoundError:
        # del st.session_state.invoice
        # st.session_state.invoice = None
        # st.error("No invoice file!")
        return None

    except json.JSONDecodeError:
        st.error("INVALID INVOICE FILE")
        # TODO - should probably delete this..
        # ALSO... LOG THE ERROR AND SEND IT TO ME!!! look at that one mCoding youtube video
        return None



def display_create_invoice_button():
    if st.button("Create invoice"):
        st.session_state.invoice = return_stored_invoice()
        if st.session_state.invoice is None:
            create_invoice_file()

        display_invoice_link()



# def check_and_display_invoice():
#     create


def display_invoice_pane():
    # check for stored invoice
    # if not_init('invoice') or st.session_state.invoice is None:
        # st.session_state.invoice = return_stored_invoice()

    # print(get('invoice'))

    # if not found, display create invoice button
    if not_init('invoice') or st.session_state.invoice is None:
        display_create_invoice_button()
    else:
        display_invoice_link()

        # if st.button("Check for payment status"):
        #     if check_for_payment():
        #         archive_invoice()




def archive_invoice():
    # rename username.invoice to username.invoice.archive
    payment_request = get('invoice')['pr']
    # last 6 characters of payment_request
    last6 = payment_request[-6:]
    new_filename = f"{INVOICES_PATH}/{get('username')}.invoice.archive.{last6}"

    invoice_filename = f"{INVOICES_PATH}/{get('username')}.invoice"
    os.rename(invoice_filename, new_filename)

    del st.session_state.invoice

    import time
    time.sleep(3)
    st.rerun()




def check_for_payment():
    # return False

    verify_url = get('invoice')['verify']

    response = requests.get(verify_url)
    if response.status_code == 200:
        settled = response.json()['settled']
        if settled:
            st.success("Invoice has been paid! 🎉")
            st.toast("Invoice has been paid! 🎉")

            # TODO I don't want to hardcode 1000 here, but there's no amount in the invoice that I can see!
            st.session_state.redis_conn.incrby(get('username'), 100 * TOKENS_PER_SAT)
            return True
    else:
        print(response.status_code, response.text)
        print("ERROR IN VERIFYING INVOICE PAYMENT STATUS")
        st.error("ERROR IN VERIFYING INVOICE PAYMENT STATUS")
        st.toast("ERROR IN VERIFYING INVOICE PAYMENT STATUS")

    st.toast("Invoice has not been paid yet. 🤔")
    return False



# from streamlit_javascript import st_javascript
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
