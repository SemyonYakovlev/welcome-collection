import os
import re
import decisions

xml_replace_template = re.compile(r'\n+\s*')


def test_make_decisions_empty():
    _make_decisions(
        """<?xml version='1.0' encoding='utf8'?><Request />""",
    	"""<?xml version='1.0' encoding='utf8'?><Response />"""
    )


def test_make_decisions_client_without_contracts():
    _make_decisions(
        """<?xml version='1.0' encoding='utf8'?><Request><Application>
	<applicationDate>2021-12-01</applicationDate>
	<clientNumber>1</clientNumber>
	<clientName>MARY SUE</clientName>
</Application></Request>""",
    	"""<?xml version='1.0' encoding='utf8'?><Response />"""
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
		<accountBalance>100</accountBalance>
		<totalDue>4000</totalDue>
	</contract>
</Application></Request>""",
    	"""<?xml version='1.0' encoding='utf8'?><Response />"""
    )


def test_make_decisions_client_with_deliquency_contract():
    _make_decisions(
        """<?xml version='1.0' encoding='utf8'?><Request><Application>
	<applicationDate>2021-12-01</applicationDate>
	<clientNumber>1</clientNumber>
	<clientName>MARY SUE</clientName>
	<contract>
		<contractNumber>1</contractNumber>
		<issueDate>2021-01-01</issueDate>
		<accountBalance>100</accountBalance>
		<totalDue>4000</totalDue>
		<daysOverdue>10</daysOverdue>
		<totalOverdue>1110</totalOverdue>
	</contract>
</Application></Request>""",
    	"""<?xml version='1.0' encoding='utf8'?>
<Response>
	<decision>
		<clientNumber>1</clientNumber>
		<DecisionType>SMS</DecisionType>
		<smsType>1</smsType>
		<smsText>На 2021-12-01 по контракту 1 образовалась просрочка в размере 1110 р</smsText>
		<decisionDate>2021-12-01</decisionDate>
	</decision>
</Response>"""
    )


def _make_decisions(input_content, expected_content):
    input_file = 'test.xml'
    with open(input_file, 'w') as file:
        file.write(input_content)
    decisions.make_decisions(input_file)
    expected_out_file = 'response_test.xml'
    assert os.path.exists(expected_out_file), f'Файла {expected_out_file} не существует'
    with open(expected_out_file, 'r') as actual_file:
        assert format_xml_string(actual_file.read()) == format_xml_string(expected_content), f'Содержимое файла {expected_out_file} не соответствует эталону'


def format_xml_string(strng):
    return xml_replace_template.sub('', strng)
