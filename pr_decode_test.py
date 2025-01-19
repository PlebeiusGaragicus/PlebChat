import datetime as dt
import bolt11
from bolt11.types import Bolt11
from bolt11.models.signature import Signature


print("\n"*4)

pr = "lnbc1u1pnfc2utpp52pgctflumy77l7zcwyv8hcu37yq3ha9aleh8vqpgcalqduqtfs8shp5fwml5q5dckdwq4c2njau2jc9prswd0q43t5aauwv56zwdgw6h6pscqzzsxqyz5vqsp5897mqnprgwmchgdd4l2zx9u5szuvgrqkw73n7kaqr00pw73fgqls9qxpqysgq6ghjpqkav6qm9nt2vncv92muprv7h6zfxxcu29femukgrdud5hq3ljpf9hc7g7vajjgsysevf5cc5y3utanx2ud6lf35cagel7ugrucqpp0vfw"
# pr = "lnbc1u1pnfmkukpp5y08x9r6wga58dz6m7mpsc6tug30tgflplq8k6c2u5paqfs6shacqhp5fwml5q5dckdwq4c2njau2jc9prswd0q43t5aauwv56zwdgw6h6pscqzzsxqyz5vqsp5pjnaqnezzwcur9j6v7da2pxxq6658knxk5rf9hcg67js2aqfavks9qxpqysgqysp9cfc9c78zesrq9jzmecjq9e7gre97x94px9f34lxu8f2w2x4kgy66t94tkwelk5pc3vg8kt5qgjntpzw53jwfxfx38r8pxh7dtwgqsmplas"

decoded: Bolt11 = bolt11.decode(pr)

# print(decoded.data)

data = decoded.data
for key in data:
    print(f"  {key}: {data[key]}")


# print(decoded.__dict__)

# for item in decoded.__dict__:
#     if callable(item):
#         continue
#     print(item)
#     print(decoded.__dict__[item])


print()
print(f"Currency: {decoded.currency}")
if decoded.is_mainnet():
    print("✅ Mainnet Invoice")
else:
    print("❌ These coins are worthless!! Invoice")

print()
print(f"Date UNIX:    {decoded.date}")
print(f"Date issued:  {decoded.dt}")
print()
print(f"Expiry:       {decoded.expiry}")
print(f"Expires on:   {decoded.expiry_date}")
print()
print(f"Curr time:    {dt.datetime.now()}")

if not decoded.has_expired():
    print("✅ Invoice has not expired")
else:
    print("❌ Invoice has expired")

print()
if decoded.description:
    print(f"Description: {decoded.description}")
else:
    print("No description found")


if decoded.metadata:
    print(f"Metadata: {decoded.metadata}")
else:
    print("No metadata found")

print()
print(f"Tags: {decoded.tags}")
for t in decoded.tags:
    print(f"  {t.char}: {t.data}")

print()
print(f"Amount:\n{decoded.amount_msat} millisats\n{decoded.amount_msat / 1000} sats")


print()
print(f"Payment secret: {decoded.payment_secret}")
if decoded.has_payment_hash:
    print("✅ Payment hash found")
    print(f"Payment hash: {decoded.payment_hash}")
else:
    print("Payment hash not found")



print()
if decoded.validate():
    print("✅ Invoice is valid")
else:
    print("❌ Invoice is invalid")

