import json
import sys

from subprocess import Popen, PIPE

_ENCODING = sys.getdefaultencoding()

def action(alert, fields, kwargs):
	'''
	'''
	try:
		kwargs = json.loads(kwargs)
	except ValueError:
		return "Received invalid kwargs in configuration."

	search = kwargs.get('query')

	parameters = [alert.get(field) for field in fields]

	try:
		search = search % tuple(parameters)
	except TypeError:
		return "Unable to compile query string."

	cmd = ["/usr/bin/python2", 
		"/usr/local/bin/splunk/search.py",
		search,
		"--config=/etc/err/splunk.conf",
		"--output_mode=json"]

	proc = Popen(cmd, stdout=PIPE, stderr=PIPE)

	output = [line.decode(_ENCODING) for line in proc.stdout]
	output = ''.join(output)

	alert['splunk'] = json.loads(output.strip("b'").strip())
	alert['splunk'] = alert['splunk']['results']
	results = alert['splunk']
	if len(results) < 1:
		return '''
\`\`\`
Splunk
No records found.
\`\`\`
'''
	
	# If the _raw field is missing, then a stats command was used and we
	# need to change what the output will look like.
	raw_missing = False
	for result in results:
		if result.get('_raw') == None:
			raw_missing = True

	# This should print a tab delimited table.
	if raw_missing:
		records = []
		for result in results:
			line = ''
			for key in result:
				line = '%s\t%s' % (line, result[key])
			records.append(line)
		records = '\n'.join(records)
	else:
		# This will print the raw log record on each line
		records = '\n'.join([record.get('_raw') for 
			record in results])
	return '''
\`\`\`
Splunk
%s
\`\`\`
''' % (records)