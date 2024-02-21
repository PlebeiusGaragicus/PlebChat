import requests

address = "turkeybiscuit@getalby.com"
url = "https://api.getalby.com/lnurl/generate-invoice"

response = requests.get(url,
                        params=
                            {
                                "ln": address,
                                "amount": 100 * 1000 # in millisats
                            }
                    )

print(response.status_code)
print(response)
print(response.json())

{
    'invoice': {
        'pr': 'lnbc1u1pjava5dpp5mg8du4vqnr4lqtlgrja5ml7t0qmcszsswj050zeff5kz5fzttytqhp5fwml5q5dckdwq4c2njau2jc9prswd0q43t5aauwv56zwdgw6h6pscqzzsxqyz5vqsp5pmljg7dg5rg38ww44c23w7lv86cru63x4qem63n2q6sn5xh55n0q9qyyssqmtq8a5stf46hshr9s269egpcp63rhg85jdszh7yxskc2tj05f03qm3y2zsatapv5hg3m4act8t9j7fqtc27n0m96n6wsnnxy9s8wf7sqdf5fg6',
        'routes': [],
        'status': 'OK',
        'successAction': {
            'message':
            'Thanks, sats received!',
            'tag': 'message'
        },
            'verify': 'https://getalby.com/lnurlp/turkeybiscuit/verify/529WSuzxHNbsgLHvF6TpdH3Z'
    }
}


{
    "status": "OK",
    "settled": false,
    "preimage": null,
    "pr": "lnbc1u1pjava5dpp5mg8du4vqnr4lqtlgrja5ml7t0qmcszsswj050zeff5kz5fzttytqhp5fwml5q5dckdwq4c2njau2jc9prswd0q43t5aauwv56zwdgw6h6pscqzzsxqyz5vqsp5pmljg7dg5rg38ww44c23w7lv86cru63x4qem63n2q6sn5xh55n0q9qyyssqmtq8a5stf46hshr9s269egpcp63rhg85jdszh7yxskc2tj05f03qm3y2zsatapv5hg3m4act8t9j7fqtc27n0m96n6wsnnxy9s8wf7sqdf5fg6"
}
