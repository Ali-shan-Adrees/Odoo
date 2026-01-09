{
	'name': 'Property Registration Renumbering',
	'version': '1.0',
	'license': 'LGPL-3',
	'category': 'Sales/Property Registration',
	'summary': 'Module to manage the renumbering or renaming of property files tied to Sale Orders.',
	'author': 'Ali Shan Dev at Eusol',
	'depends': ['base', 'sale', 'mail'],
	'data': [
		'security/security.xml',
		'security/ir.model.access.csv',
		'views/views.xml',
	],
	'installable': True,
	'application': True,
	'auto_install': False,

    'assets': {},
}
