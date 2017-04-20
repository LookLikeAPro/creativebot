import requests

requests.post(
    'https://api.kik.com/v1/config',
    auth=('jerryzmemes', '23e97815-9715-479f-b096-5a47b30a3f87'),
    headers={
        'Content-Type': 'application/json'
    },
    data=json.dumps({
        'webhook': 'https://example.com/incoming', 
        'features': {
            'receiveReadReceipts': False, 
            'receiveIsTyping': False, 
            'manuallySendReadReceipts': False, 
            'receiveDeliveryReceipts': False
        }
    })
)
