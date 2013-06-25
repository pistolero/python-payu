from payu import PayU
import test_settings as ts

payu = PayU(ts.MERCHANT, ts.SECRET)

print payu.token(ts.TOKEN).new_sale('1.1', 'UAH', ts.REFNO, ext_ref_no='22')
# {u'message': u'Operation successful', u'code': u'0', u'tran_ref_no': u'6951255'}
