from payu import PayU
import test_settings as ts

payu = PayU(ts.MERCHANT, ts.SECRET)


from flask import Flask, request

app = Flask(__name__)


def ordered_storage(f):
    import werkzeug.datastructures
    import flask
    def decorator(*args, **kwargs):
        flask.request.parameter_storage_class = werkzeug.datastructures.ImmutableOrderedMultiDict
        return f(*args, **kwargs)
    return decorator


@app.route('/', methods=['POST'])
@ordered_storage
def ipn():
    ipn = payu.ipn(request.form)

    print ipn.data

    return ipn.sign()


app.run(port=9981, debug=True)
