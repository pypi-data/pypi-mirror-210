import hashlib

from .authorization import authorization
from .models import ClickTransaction
from .schema import ClickTransactionCreate
from .status import (PREPARE, COMPLETE, AUTHORIZATION_FAIL_CODE, AUTHORIZATION_FAIL, ACTION_NOT_FOUND,
                     ORDER_NOT_FOUND, INVALID_AMOUNT, ALREADY_PAID, TRANSACTION_NOT_FOUND, TRANSACTION_CANCELLED,
                     SUCCESS)
from app.config import settings


async def order_load(order_id):
    if int(order_id) > 1000000000:
        return None
    transaction = await ClickTransaction.get(id=order_id)
    print("transaction", transaction.amount)
    if not transaction:
        return None
    return transaction


async def click_webhook_errors(click_trans_id: str,
                               service_id: str,
                               merchant_trans_id: str,
                               amount: str,
                               action: str,
                               sign_time: str,
                               sign_string: str,
                               error: str,
                               merchant_prepare_id: str = None) -> dict:
    merchant_prepare_id = merchant_prepare_id if action and action == '1' else ''
    created_sign_string = '{}{}{}{}{}{}{}{}'.format(
        click_trans_id, service_id, settings.CLICK_SETTINGS['secret_key'],
        merchant_trans_id, merchant_prepare_id, amount, action, sign_time)
    encoder = hashlib.md5(created_sign_string.encode('utf-8'))

    created_sign_string = encoder.hexdigest()
    print(created_sign_string)
    if created_sign_string != sign_string:
        return {
            'error': AUTHORIZATION_FAIL_CODE,
            'error_note': 'SIGN CHECK FAILED!'
        }

    if action not in [PREPARE, COMPLETE]:
        return {
            'error': ACTION_NOT_FOUND,
            'error_note': 'Action not found'
        }

    order = order_load(merchant_trans_id)
    print("order 56", await order.amount)
    if not order:
        return {
            'error': ORDER_NOT_FOUND,
            'error_note': 'Order not found'
        }

    if abs(float(amount) - float(order.amount) > 0.01):
        return {
            'error': INVALID_AMOUNT,
            'error_note': 'Incorrect parameter amount'
        }

    if order.status == ClickTransaction.CONFIRMED:
        return {
            'error': ALREADY_PAID,
            'error_note': 'Already paid'
        }

    if action == COMPLETE:
        if merchant_trans_id != merchant_prepare_id:
            return {
                'error': TRANSACTION_NOT_FOUND,
                'error_note': 'Transaction not found'
            }

    if order.status == ClickTransaction.CANCELED or int(error) < 0:
        return {
            'error': TRANSACTION_CANCELLED,
            'error_note': 'Transaction cancelled'
        }
    return {
        'error': SUCCESS,
        'error_note': 'Success'
    }


async def prepare(click_trans_id: str,
                  service_id: str,
                  click_paydoc_id: str,
                  merchant_trans_id: str,
                  amount: str,
                  action: str,
                  sign_time: str,
                  sign_string: str,
                  error: str,
                  error_note: str,
                  *args, **kwargs) -> dict:
    """
    :param click_trans_id:
    :param service_id:
    :param click_paydoc_id:
    :param merchant_trans_id:
    :param amount:
    :param action:
    :param sign_time:
    :param sign_string:
    :param error:
    :param error_note:
    :param args:
    :param kwargs:
    :return:
    """
    result = await click_webhook_errors(click_trans_id, service_id, merchant_trans_id,
                                        amount, action, sign_time, sign_string, error)
    print("RESULT-compare", result)
    order = await order_load(merchant_trans_id)
    if result['error'] == '0':
        order.status = ClickTransaction.WAITING
        await order.save()
    result['click_trans_id'] = click_trans_id
    result['merchant_trans_id'] = merchant_trans_id
    result['merchant_prepare_id'] = merchant_trans_id
    result['merchant_confirm_id'] = merchant_trans_id
    return result


async def complete(click_trans_id: str,
                   service_id: str,
                   click_paydoc_id: str,
                   merchant_trans_id: str,
                   amount: str,
                   action: str,
                   sign_time: str,
                   sign_string: str,
                   error: str,
                   error_note: str,
                   merchant_prepare_id: str = None,
                   *args, **kwargs) -> dict:
    """
    :param click_trans_id:
    :param service_id:
    :param click_paydoc_id:
    :param merchant_trans_id:
    :param amount:
    :param action:
    :param sign_time:
    :param sign_string:
    :param error:
    :param error_note:
    :param merchant_prepare_id:
    :param args:
    :param kwargs:
    :return:
    """
    print("merchant: ", merchant_trans_id)
    order = await order_load(merchant_trans_id)
    result = await click_webhook_errors(click_trans_id, service_id, merchant_trans_id,
                                        amount, action, sign_time, sign_string, error, merchant_prepare_id)
    print("RESULT", result)
    if error and int(error) < 0:
        await order.change_status(ClickTransaction.CANCELED)
    if result['error'] == SUCCESS:
        await order.change_status(ClickTransaction.CONFIRMED)
        order.click_paydoc_id = click_paydoc_id
        await order.save()

    result['click_trans_id'] = click_trans_id
    result['merchant_trans_id'] = merchant_trans_id
    result['merchant_prepare_id'] = merchant_prepare_id
    result['merchant_confirm_id'] = merchant_prepare_id
    return result


def generate_url(order_id, amount, return_url=None):
    service_id = settings.CLICK_SETTINGS['service_id']
    merchant_id = settings.CLICK_SETTINGS['merchant_id']
    url = f"https://my.click.uz/services/pay?service_id={service_id}&merchant_id={merchant_id}&amount={amount}&transaction_param={order_id}"
    if return_url:
        url += f"&return_url={return_url}"
    return url
