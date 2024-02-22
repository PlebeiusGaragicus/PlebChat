








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
