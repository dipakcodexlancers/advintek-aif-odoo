{
    'name': 'LHDN Invoice',
    'version': '1.0.0',
    'summary': 'LHDN Integration Base Module',
    'description': 'Base module for LHDN e-Invoice integration',
    'author': 'Advintek',
    'category': 'Accounting',
    'depends': ['account'],
    'data': [
        'views/account_move_view.xml',
    ],
    'installable': True,
    'application': False,
}