import os
import re
import decisions
from base64 import b64decode
from hashlib import md5


def test_make_decisions_empty():
    _make_decisions(
        """<Request/>""",
        """<Response/>"""
    )


def test_make_decisions_client_without_contracts():
    _make_decisions(
        """<?xml version='1.0' encoding='utf8'?><Request><Application>
	<applicationDate>2021-12-01</applicationDate>
	<clientNumber>1</clientNumber>
	<clientName>MARY SUE</clientName>
</Application></Request>""",
        """<Response/>"""
    )


def test_make_decisions_client_without_desired_contract():
    _make_decisions(
        """<?xml version='1.0' encoding='utf8'?><Request><Application>
	<applicationDate>2021-12-01</applicationDate>
	<clientNumber>1</clientNumber>
	<clientName>MARY SUE</clientName>
	<contract>
		<contractNumber>1</contractNumber>
		<issueDate>2021-01-01</issueDate>
		<accountBalance>100.00</accountBalance>
		<totalDue>4000.00</totalDue>
	</contract>
</Application></Request>""",
        """<Response/>"""
    )


def test_make_decisions_client_with_predelinquency_contract():
    _make_decisions(
        """<?xml version='1.0' encoding='utf8'?><Request><Application>
	<applicationDate>2021-12-01</applicationDate>
	<clientNumber>2</clientNumber>
    <clientName>ABRAAM DAI</clientName>
	<contract>
		<contractNumber>3</contractNumber>
		<issueDate>2021-01-01</issueDate>
		<accountBalance>100.00</accountBalance>
		<totalDue>4000.00</totalDue>
        <nextPayment>
            <nextPaymentDate>2021-12-07</nextPaymentDate>
            <nextPaymentSum>1001.00</nextPaymentSum>
        </nextPayment>
	</contract>
</Application></Request>""",
        """<Response>
	<decision>
		<clientNumber>2</clientNumber>
		<DecisionType>SMS</DecisionType>
		<smsType>2</smsType>
		<smsText>Напоминаем о предстоящем платеже по контракту 3 в размере 1001.00 р</smsText>
		<decisionDate>2021-12-01</decisionDate>
	</decision>
</Response>"""
    )


def test_make_decisions_client_with_delinquency_contract():
    _make_decisions(
        """<?xml version='1.0' encoding='utf8'?><Request><Application>
	<applicationDate>2021-12-01</applicationDate>
	<clientNumber>1</clientNumber>
	<clientName>MARY SUE</clientName>
	<contract>
		<contractNumber>1</contractNumber>
		<issueDate>2021-01-01</issueDate>
		<accountBalance>100.00</accountBalance>
		<totalDue>4000.00</totalDue>
		<daysOverdue>10</daysOverdue>
		<totalOverdue>1110.00</totalOverdue>
	</contract>
</Application></Request>""",
        """<Response>
	<decision>
		<clientNumber>1</clientNumber>
		<DecisionType>SMS</DecisionType>
		<smsType>1</smsType>
		<smsText>На 2021-12-01 по контракту 1 образовалась просрочка в размере 1110.00 р</smsText>
		<decisionDate>2021-12-01</decisionDate>
	</decision>
</Response>"""
    )


def test_make_decisions_client_with_delinquency_and_delinquency_contracts():
    passwd = os.environ.get('passwd', '')
    _make_decisions(
        decode("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", passwd),
        decode("CjBdS0hWV0FXXDk4CFZTBgpLDQtWC29sbF9aClgDC0R4F1VaXUsHAw5NUF1dV1gRLU0JBl1HW29sagUiVAUMQ18NVmxBSVwMYS9gDRt2UwYKSw0LVmEcFQBdM284WhZdRTZBSF0HCA4dEV5CYEtGAF0ybW0ERggWMQZBEg+2+OCGQgoICggUAwBPAwAU4om13Ri03uiLtdi04ejm4da1iufg6bsYCBnijLKC4LTihrXU6Nq0iuXVtd6zibewt+kQ5t3puOiH6LPj4uOP5bXm37OIRLSKFbTltdPp0eHatYXn4uiNGAgIAwJMAwEU47ZZTEsJF2xQHRFbaTBvDQIAU18RUVdWfVhGV1wBAQYDG1RRFVRVBBoBAAYKSg9eCCFRQgcGMjEFFlZXAVpCXV1YW2kxWABdVgwWDAxXWDtvbAxVDlFdVk13R18AVkMKAwpKAFQNAVZBKxAIAVwUD2xsOQomXVtRSlBdXDZKQVEMZSgwBEsgXVYMFgwMVzJIFgAOPGsxBEtUSmZLElYPBQ4ZFg5LMB1IUFtvbGoFFVwVMVVOFgbopemJEgBSAQAZAwRIUwlEtIfl20W12enY4du0sufi6Ijog+iw4+ETAxTiiLXS6eS0iOXStduzi7aBtt7ghrO56bQZ6Y3j4uOP5bPn5bOGtePoj7XVRbOLRuDmtYDm1eiE6IzosuLXEwAFAwZLUwhEtbgJShYIEG0DSRJbOj9rBFxdWlBBWw1ddVVGU1tRCFZVFQRXSFVSBUlVAwZZRQtXVnxYTVcMaDoNG1ZTBgpLDQtWC29sWQdcBVgVDF9YXDIxMQVaXlsHXUV6R1sHBkpaVgQaBgkMBlcSfxMIUlMQBjIxMAV2VwFaQl1dWDEaSAFaa3g2WUonXAVYFQxfWDZBSF0HMzs7XkBcR2ZPFQYGVlgXRggWMRpJAw9sbDkKEVVLbFxBRgyyruGE4om13ejYtIDl2LXVs4y2jUa1jhayh+m46YzihrOy4LbiiLTs6e20jeXZRbXc6d3h1rSy5tfojuiMGeKNso0R5Ijm27OFtebptbXVtdno5ODlRQMWsooY6bnpguLV443kh+fls41EVQgFVEtVUxm3sVpKQ1sRbF1ATQc4O2sPVVFRXxYKVwogWUEAW1dTC1ccV1cdBlMEF1xcWltBC1xfcFNCAF0ybVgXUQAGDBBQCV9YbwwZMF1LSFZXQVdc", passwd)
    )


def _make_decisions(input_content, expected_content):
    input_file = 'test.xml'
    with open(input_file, 'w') as file:
        file.write(input_content)
    decisions.make_decisions(input_file)
    expected_out_file = 'response_test.xml'
    assert os.path.exists(expected_out_file), f'Файла {expected_out_file} не существует'
    with open(expected_out_file, 'r') as actual_file:
        assert format_xml_string(actual_file.read()) == format_xml_string(expected_content), \
            f'Содержимое файла {expected_out_file} не соответствует эталону'


xml_replace_template = re.compile(r'\n+\s*')
xml_version_eraser_template = re.compile(r'<\?xml[^>]+\?>')
xml_empty_tag_template = re.compile(r' />')


def format_xml_string(strng):
    return xml_empty_tag_template.sub('/>', xml_version_eraser_template.sub('', xml_replace_template.sub('', strng)))


def decode(b64encoded_string: str, passwd: str):
    b64encoded = b64decode(b64encoded_string.encode())
    passwd = md5(passwd.encode()).hexdigest().encode()
    return bytes(a ^ passwd[i % len(passwd)] for i, a in enumerate(b64encoded)).decode('utf8')
