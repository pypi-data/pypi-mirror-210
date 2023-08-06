from attr import dataclass
import requests
import json

@dataclass
class SignalServiceDomain:
    iam_service:str
    portfolio_service:str

def publish_signals_to_all_domains(data):
    domains = [SignalServiceDomain('http://10.11.0.99:30965','http://10.11.0.99:30982')]

    for domain in domains:
        try:
            publish_signals_to_domain(domain,data)
        except Exception as e:
            print(e)
            print(f'error publish signal to {domain}')

def publish_signals_to_domain(domain:SignalServiceDomain,data):
    token = get_token(domain.iam_service)
    publish_signals(domain.portfolio_service,token,data)

def publish_signals(domain:str,token:str,data):
    
    url = f"{domain}/v1/signal/create"

    print(domain)

    headers = {
    'Authorization': f'Bearer {token}',
    'Cookie': 'JSESSIONID=C8BEE7F4C0ECCDAC4183D867819FE5FE; JSESSIONID=03273813B9359E33074821215EF72442',
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=json.dumps(data))
    print(response.text)

def get_token(domain:str)->str:
    url = f"{domain}/v1/authentication/login"

    payload = json.dumps({})
    headers = {
    'Content-Type': 'application/json',
    'Accept': '*',
    'grant-type': 'client_credential',
    'client-id': 'ff120ac8-9911-4b0f-8041-9dce64d5dbad',
    'client-secret': '123456'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return json.loads(response.text)['data']['token']