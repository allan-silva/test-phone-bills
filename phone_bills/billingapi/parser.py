class BillResponseParser:
    def parse(self, bill_call_doc):
        _id = bill_call_doc['_id']
        bill = dict(
            subscriber=_id['subscriber'],
            period=f"{_id['month']}/{_id['year']}")
        calls = []
        for call in bill_call_doc['calls']:
            start_at = call['start_at']
            duration = call['duration']
            bill_call = dict(
                destination=call['destination'],
                start_date=start_at.strftime('%d/%m/%Y'),
                start_time=start_at.strftime('%H:%M:%S'),
                duration=f"{duration['d']}d{duration['h']}h{duration['m']}m{duration['s']}s",
                price=round(call['price'],2))
            calls.append(bill_call)
        bill['calls'] = calls
        return bill
