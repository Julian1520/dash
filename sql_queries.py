sparkasse_balance_query = '''
select amount * {} as amount from sparkasse_balance where date(date) =
                                             (select max(date(date)) from sparkasse_balance)
'''

dkb_balance_query = '''
select amount * {} as amount from dkb_balance where date(date) =
                                             (select max(date(date)) from dkb_balance)
'''

cc_balance_query = '''
select amount * {} as amount from credit_card_balance where date(date) =
                                             (select max(date(date)) from credit_card_balance)
'''

depot_balance_query = '''
select sum(value) * {} as amount from depot_data
'''

balance_over_all_query = '''
select distinct amount * {obscure_int} as amount, 'sparkasse' as allocation from sparkasse_balance where date(date) =
    (select max(date(date)) from sparkasse_balance)
union all
select distinct amount * {obscure_int} as amount, 'dkb' as allocation from dkb_balance where date(date) =
    (select max(date(date)) from dkb_balance)
union all
select sum(value) * {obscure_int} as amount, 'depot' as allocation from depot_data
union all
select amount * {obscure_int} as amount, 'credit card' as allocation from credit_card_balance where date(date) =
    (select max(date(date)) from credit_card_balance)
'''

transactions_query = '''
select amount, applicant_name, date(date), posting_text, purpose, bank_name,tag from dkb_transactions
union all
select amount, applicant_name, date(date), posting_text, purpose, bank_name,tag from sparkasse_transactions
union all
select amount, description as applicant_name, to_date(voucher_date, 'dd.mm.yy'), 'NA' as posting_text, 'NA' as purpose, 'NA' as bank_name, tag  from credit_card_data
order by date desc
'''

stocks_query = '''
select value * {} as value, name from depot_data
'''

overview_query = '''
select 'Stocks' as "Asset", sum(value) * {obscure_int} as "Value"
from depot_data
union all
select 'Cash' as "Asset",
       ROUND((select amount * {obscure_int} from sparkasse_balance order by date(date) desc limit 1) +
             (select amount * {obscure_int}from dkb_balance order by date(date) desc limit 1) +
             (select amount * {obscure_int}from credit_card_balance order by date(date) desc limit 1)) as "Cash value"
union all
select '' as "Asset",
       ROUND((select amount * {obscure_int}from sparkasse_balance order by date(date) desc limit 1) +
             (select amount * {obscure_int}from dkb_balance order by date(date) desc limit 1) +
             (select amount * {obscure_int}from credit_card_balance order by date(date) desc limit 1))+
             (select sum(value) * {obscure_int} as "Value" from depot_data)
'''

in_out_query = '''
select * from (
select date_trunc('month',date(date)),tag, sum(amount) * {} as amount from sparkasse_transactions where tag != 'Internal transaction' group by 1,2
union all
select date_trunc('month',date(date)),tag, sum(amount) * {} as amount from dkb_transactions where tag != 'Internal transaction' group by 1,2
union all
select date_trunc('month',to_date(value_date, 'dd.mm.yy')),tag, sum(amount) * {} as amount from credit_card_data where tag != 'Internal transaction' group by 1,2)a
'''

balance_chart_query = '''
select '2019-01-01' as date, 500 as amount,'dkb' as "Cash location"
union all
select '2019-01-02' as date, 600 as amount,'dkb' as "Cash location"
union all
select '2019-01-03' as date, 700 as amount,'dkb' as "Cash location"
union all
select '2019-01-01' as date, 300 as amount,'sparkasse' as "Cash location"
union all
select '2019-01-02' as date, 900 as amount,'sparkasse' as "Cash location"
union all
select '2019-01-03' as date, 1000 as amount,'sparkasse' as "Cash location"
'''