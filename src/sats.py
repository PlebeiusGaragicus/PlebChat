import os
import time
import json
import requests

import qrcode

import streamlit as st

from src.common import set, get, not_init, INVOICES_PATH

TOKENS_PER_SAT = 30

# https://guides.getalby.com/developer-guide/v/alby-wallet-api/lightning-address-details-proxy
# https://github.com/getAlby/js-lightning-tools
# https://guides.getalby.com/developer-guide/v/lightning-tools/introduction/receiving-bitcoin-payments
# https://guides.getalby.com/developer-guide/v/alby-wallet-api/reference/authorization


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

    # invoice_number = payment_request[:6] + "..." + payment_request[-6:]
    # st.write(f"Invoice: :green[{invoice_number}]")

    generate_qr()

    if st.button("Check for payment status"):
        if check_for_payment():
            archive_invoice()
        else:
            st.warning("Invoice has not been paid yet.")




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



def return_stored_invoice():
    invoice_filename = f"{INVOICES_PATH}/{get('username')}.invoice"

    try:
        with open(invoice_filename, "r") as f:
            invoice = json.load(f)['invoice']
            print("INVOICE FILE FOUND:")
            print(invoice)
            return invoice

    except FileNotFoundError:
        return None

    except json.JSONDecodeError:
        st.error("INVALID INVOICE FILE")
        # TODO - should probably delete the file..
        # ALSO... LOG THE ERROR AND SEND IT TO ME!!! look at that one mCoding youtube video
        return None



def display_create_invoice_button():
    add_sats_placeholder = st.empty()

    if add_sats_placeholder.button("⚡️ :green[add sats] ⚡️", use_container_width=True):
        add_sats_placeholder.empty()
        st.session_state.invoice = return_stored_invoice()
        if st.session_state.invoice is None:
            create_invoice_file()

        display_invoice_link()
        if check_for_payment():
            archive_invoice()




def display_invoice_pane():
    with st.container(border=True):
        if not_init('invoice') or st.session_state.invoice is None:
            display_create_invoice_button()
        else:
            display_invoice_link()



def archive_invoice():
    """ rename {username}.invoice to {username}.invoice.archive.{last6} """

    payment_request = get('invoice')['pr']
    last6 = payment_request[-6:] # last 6 characters of payment_request
    new_filename = f"{INVOICES_PATH}/{get('username')}.invoice.archive.{last6}"

    invoice_filename = f"{INVOICES_PATH}/{get('username')}.invoice"
    os.rename(invoice_filename, new_filename)

    del st.session_state.invoice

    time.sleep(3) # allow toast to display before rerunning
    st.rerun()




def check_for_payment():
    verify_url = get('invoice')['verify']

    response = requests.get(verify_url)
    if response.status_code == 200:
        settled = response.json()['settled']

        # status = "settled" if get('invoice')['settled'] else "pending"
        status = "settled" if settled else "pending"
        st.write(f"Status: :orange[{status}]")

        if settled:
            st.success("Invoice has been paid! 🎉")

            # TODO I don't want to hardcode numbers here, but there's no amount in the invoice that I can see!
            st.session_state.redis_conn.incrby(get('username'), 100 * TOKENS_PER_SAT)
            return True
        else:
            return False
    else:
        print(response.status_code, response.text)
        print("ERROR IN VERIFYING INVOICE PAYMENT STATUS")
        st.error("ERROR IN VERIFYING INVOICE PAYMENT STATUS")
        st.toast("ERROR IN VERIFYING INVOICE PAYMENT STATUS")

        return False






def generate_qr():
    # look for QR code file
    qr_filename = f"{INVOICES_PATH}/{get('username')}.qr.png"
    pr = get('invoice')['pr']

    if not os.path.exists(qr_filename):
        # Prefix the invoice with "lightning:" to make it compatible with wallet apps
        invoice_for_qr = f"lightning:{pr}"

        # Generate the QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(invoice_for_qr)
        qr.make(fit=True)

        # Create an Image object from the QR Code instance
        img = qr.make_image(fill_color="black", back_color="white")

        # Save the QR code to a file inside the invoices folder
        img.save(qr_filename)

    caption = f"Invoice: {pr[0:10]}...{pr[-10:]}"
    st.image(qr_filename, caption=caption, use_column_width=True)
