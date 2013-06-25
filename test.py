from payu import PayU
import test_settings as ts
payu = PayU(ts.MERCHANT, ts.SECRET)

order = payu.order('UAH', debug=True, test_order=False, back_ref='https://teamroom.me/backref/')
order.add_product('123', '1 uah subscription', 1, 1, 0)
#order.add_product('223', 'pubs', 200.5, 2, 10, info='Super pubs')
order.enable_token()

z = unicode(order)
print z

with open('z.html', 'w') as f:
    f.write(z)


