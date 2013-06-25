from payu import PayU
import test_settings as ts
payu = PayU(ts.MERCHANT, ts.SECRET)

order = payu.order('UAH', debug=True, test_order=False, back_ref='https://teamroom.me/backref/', pay_method='CCVISAMC')
order.add_product('123', '1 uah subscription', 1, 1, 0)
#order.add_product('223', 'pubs', 200.5, 2, 10, info='Super pubs')
order.enable_token()
order.set_billing_info('Sergey', 'Kirillov', 'serg@teamroom.me', '11111', 'ul. Asdasda', 'Kiev')
order.set_delivery_info('Sergey', 'Kirillov', 'serg@teamroom.me', '11111', 'ul. Asdasda', 'Kiev')

z = unicode(order)
print z

with open('z.html', 'w') as f:
    f.write(z)


