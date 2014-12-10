python-klikbca-parser
=====================

Parser untuk ambil balance dan transaksi dari klikbca personal

Cara penggunaan
---------------

```python
import bcaparser

bca = bcaparser.BCA_parser(username , password)

if bca.login():
	balance = bca.get_balance()
	transactions = bca.get_transactions()
	bca.logout()
	update_balance(conn , username , balance , process_notes(transactions) , pb_account)
```
