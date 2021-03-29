from aiohttp import web
import redis
import json
from exceptions import *


r = redis.Redis(host='localhost', port=6379, db=0)


async def get_conversion(cur_from, cur_to, amount):
    result = 0.0
    if cur_to != 'RUR' and cur_from != 'RUR':
        rub_from = r.get(cur_from)
        rub_to = r.get(cur_to)
        result = float(rub_from) * float(amount) / float(rub_to)
    elif cur_to == 'RUR':
        result = float(r.get(cur_from)) * float(amount)
    elif cur_from == 'RUR':
        result = float(amount) / float(r.get(cur_to))
    return result


async def conversion_checks(cur_to, cur_from, amount):
    if cur_to == cur_from:
        raise SimilarCurrencyException(f"Similar currencies! {cur_to} and {cur_from}")
    elif not cur_to.isalpha():
        raise UnsupportedType(f"Currency must be a word. Got '{cur_to}'")
    elif not cur_from.isalpha():
        raise UnsupportedType(f"Currency must be a word. Got '{cur_from}'")
    elif cur_to != 'RUR' and r.get(cur_to) is None:
        raise NoValueException(f"No currency like '{cur_to}'")
    elif cur_from != 'RUR' and r.get(cur_from) is None:
        raise NoValueException(f"No currency like '{cur_from}'")
    if not amount.isdigit():
        raise UnsupportedValueException(f"Amount must be a digit. Got '{amount}'")


async def convert_handler(request):
    try:
        cur_from = request.query['from']
        cur_to = request.query['to']
        amount = request.query['amount']

        await conversion_checks(cur_to, cur_from, amount)

        result = await get_conversion(cur_from, cur_to, amount)
        response_obj = {'code': 200, 'status': 'success', 'result': str(round(result, 2))}

        return web.json_response(response_obj, status=200)
    except NoValueException as e:
        response_obj = {'code': 404, 'status': 'failed', 'reason': str(e)}
        return web.json_response(response_obj, status=404)
    except (UnsupportedValueException, SimilarCurrencyException) as e:
        response_obj = {'code': 422, 'status': 'failed', 'reason': str(e)}
        return web.json_response(response_obj, status=422)
    except UnsupportedType as e:
        response_obj = {'code': 415, 'status': 'failed', 'reason': str(e)}
        return web.json_response(response_obj, status=415)
    except KeyError as e:
        response_obj = {'code': 400, 'status': 'failed', 'reason': 'Invalid data. Maybe you meant '+str(e)}
        return web.json_response(response_obj, status=400)
    except Exception as e:
        response_obj = {'code': 500, 'status': 'failed', 'reason': str(e)}
        return web.json_response(response_obj, status=500)