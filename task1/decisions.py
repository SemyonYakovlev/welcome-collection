import sys
from lxml import etree as et
from datetime import datetime
def make_decisions(input_filename):
    with open(input_filename, 'r') as xml_file:
        data = et.parse(xml_file)
    datatree = data.getroot()
    rootName = et.QName('Response')
    root = et.Element(rootName)
    sheet = et.ElementTree(root)
    for contracts in datatree.findall('Application'):
        for contract in contracts.findall('contract'):
          try:
              if float(contract.find('totalOverdue').text) > 0:
                decision = et.SubElement(root, "decision")
                clientNumber = et.SubElement(decision, "clientNumber")
                clientNumber.text = contracts.find('clientNumber').text
                DecisionType = et.SubElement(decision, "DecisionType")
                DecisionType.text = 'SMS'
                smsType = et.SubElement(decision, "smsType")
                smsType.text = '1'
                smsText = et.SubElement(decision, "smsText")
                smsText.text = f"На {contracts.find('applicationDate').text} по контракту {contract.find('contractNumber').text} образовалась просрочка в размере {contract.find('totalOverdue').text} р"
                decisionDate = et.SubElement(decision, "decisionDate")
                decisionDate.text = f"{contracts.find('applicationDate').text}"
          except Exception: 
                pass
          try:
              for nextpay in contract.findall('nextPayment'):
                if (abs(datetime.strptime(nextpay.find('nextPaymentDate').text, "%Y-%m-%d") - datetime.strptime(contracts.find('applicationDate').text, "%Y-%m-%d")).days) in (5,6,7) and float(contract.find('accountBalance').text) < float(nextpay.find('nextPaymentSum').text):
                  decision = et.SubElement(root, "decision")
                  clientNumber = et.SubElement(decision, "clientNumber")
                  clientNumber.text = contracts.find('clientNumber').text
                  DecisionType = et.SubElement(decision, "DecisionType")
                  DecisionType.text = 'SMS'
                  smsType = et.SubElement(decision, "smsType")
                  smsType.text = '2'
                  smsText = et.SubElement(decision, "smsText")
                  smsText.text = f"Напоминаем о предстоящем платеже по контракту {contract.find('contractNumber').text} в размере {nextpay.find('nextPaymentSum').text} р"
                  decisionDate = et.SubElement(decision, "decisionDate")
                  decisionDate.text = f"{contracts.find('applicationDate').text}"
          except Exception: 
                pass
    with open(f"response_{input_filename}", "wb") as file:
        sheet.write(file, pretty_print = True,standalone='yes', encoding='cp1251')
