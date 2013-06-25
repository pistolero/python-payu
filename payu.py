import requests
import datetime
import hmac
import hashlib
from collections import OrderedDict


class SignatureBuilder(object):
    def __init__(self, secret):
        self.secret = secret
        self.s = ''

    def add(self, val, key=None):
        val = unicode(val)
        if val is not None:
            self.s += '%d%s' % (len(val), val)
            #print '%s=%r' % (key, val)

    def __str__(self):
        #print repr(s)
        #print self.s
        return hmac.HMAC(self.secret, self.s, hashlib.md5).hexdigest()


class PayU(object):
    def __init__(self, merchant, secret, lu_url='https://secure.payu.ua/order/lu.php'):
        self.merchant = merchant
        self.secret = secret
        self.lu_url = lu_url

    def order(self, currency, ref=None, date=None, discount=None, destination_city=None, destination_state=None, destination_country=None, pay_method=None, test_order=False, debug=False, language=None, back_ref=None):
        kw = locals()
        kw.pop('self')
        return PayUOrder(self, **kw)

    def ipn(self, data):
        return PayUIpn(self, data)


class PayUIpn(object):
    def __init__(self, payu, data):
        self.payu = payu
        self.data = data

        self.verify_hash()

    def verify_hash(self):
        hash1 = self.data['HASH']

        sig = SignatureBuilder(self.payu.secret)
        for key, vals in self.data.iterlists():
            if key == 'HASH':
                continue

            for val in vals:
                sig.add(val)

        hash2 = unicode(sig)

        if hash2 != hash1:
            raise ValueError('Received hash %r is not equal to calculated %r' % (hash1, hash2))

    def sign(self):
        pid0 = self.data.getlist('IPN_PID[]')[0]
        pname0 = self.data.getlist('IPN_PNAME[]')[0]
        ipn_date = self.data.get('IPN_DATE')
        date = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        sig = SignatureBuilder(self.payu.secret)
        sig.add(pid0)
        sig.add(pname0)
        sig.add(ipn_date)
        sig.add(date)

        return '<EPAYMENT>{0}|{1}</EPAYMENT>\n'.format(date, unicode(sig))


class PayUOrder(object):
    def __init__(self, payu, currency, ref=None, date=None, discount=None, destination_city=None, destination_state=None, destination_country=None, pay_method=None, test_order=False, debug=False, language=None, back_ref=None):
        self.payu = payu
        self.action_name = ''
        if date is None:
            date = datetime.datetime.now()

        if not test_order:
            test_order = None

        if not debug:
            debug = None

        self.data = OrderedDict([
            ('MERCHANT', self.payu.merchant),
            #('LU_ENABLE_TOKEN', None),
            #('LU_TOKEN_TYPE', None),
            ('ORDER_REF', ref),
            ('ORDER_DATE', date.strftime('%Y-%m-%d %H:%M:%S')),
            ('ORDER_PNAME[]', []),
            ('ORDER_PCODE[]', []),
            ('ORDER_PINFO[]', []),
            ('ORDER_PRICE[]', []),
            ('ORDER_QTY[]', []),
            ('ORDER_VAT[]', []),
            ('ORDER_SHIPPING', 0),
            ('PRICES_CURRENCY', currency),
            ('PAY_METHOD', pay_method),
            ('ORDER_PGROUP[]', []),
            ('ORDER_PRICE_TYPE[]', []),
            ('DEBUG', debug and '1'),
            ('TESTORDER', test_order and 'TRUE'),
            ('BACK_REF', back_ref)
        ])

    def add_product(self, code, name, price, qty, vat, group=None, info=None, price_type='NET'):
        self.data['ORDER_PCODE[]'].append(code)
        self.data['ORDER_PNAME[]'].append(name)
        self.data['ORDER_PGROUP[]'].append(group)
        self.data['ORDER_PINFO[]'].append(info)
        self.data['ORDER_PRICE[]'].append(price)
        self.data['ORDER_PRICE_TYPE[]'].append(price_type)
        self.data['ORDER_QTY[]'].append(qty)
        self.data['ORDER_VAT[]'].append(vat)
        return self

    def set_billing_info(self, first_name, last_name, email, phone, address, city):
        self.data['BILL_FNAME'] = first_name
        self.data['BILL_LNAME'] = last_name
        self.data['BILL_EMAIL'] = email
        self.data['BILL_PHONE'] = phone
        self.data['BILL_ADDRESS'] = address
        self.data['BILL_CITY'] = city

        return self

    def set_delivery_info(self, first_name, last_name, email, phone, address, city):
        self.data['DELIVERY_FNAME'] = first_name
        self.data['DELIVERY_LNAME'] = last_name
        self.data['DELIVERY_EMAIL'] = email
        self.data['DELIVERY_PHONE'] = phone
        self.data['DELIVERY_ADDRESS'] = address
        self.data['DELIVERY_CITY'] = city

        return self

    def enable_token(self, token_type='PAY_ON_TIME'):
        self.data['LU_ENABLE_TOKEN'] = '1'
        self.data['LU_TOKEN_TYPE'] = token_type

        return self

    def action(self, action_name):
        self.action_name = action_name

    def __unicode__(self):
        return self.build()

    def _iter_items(self):
        for key, val in self.data.iteritems():
            if key.endswith('[]'):
                if val:
                    if all(x is None for x in val):
                        continue

                    for v in val:
                        yield key, v if v is not None else ''
            else:
                if val is not None:
                    yield key, val

    def build(self):
        sig = SignatureBuilder(self.payu.secret)
        items = []
        for key, val in self._iter_items():
            items.append('{0}:<input name="{0}" value="{1}" type="text">'.format(key, val))
            if not (key in ('DEBUG', 'TESTORDER', 'LANGUAGE', 'BACK_REF') or key.startswith('BILL_') or key.startswith('DELIVERY_') or key.startswith('LU_')):
                sig.add(val, key)

        items.append('<input name="ORDER_HASH" value="{0}" type="hidden">'.format(sig))

        return '<form action="{0}" method="post" name="frmOrder">{1}<input name="{2}" type="submit"></form>'.format(self.payu.lu_url, '<br>\n'.join(items), self.action_name)


if __name__ == '__main__':
    import test
