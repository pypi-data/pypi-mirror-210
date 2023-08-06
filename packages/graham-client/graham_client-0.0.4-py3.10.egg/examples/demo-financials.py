from graham import GrahamClient
import os

def main():
    client = GrahamClient(os.getenv('API_KEY'), os.getenv('COMPANY_ID'))

    results, err = client.Equities().Financials().ListSummaries('pub_cmp_968b09db15804187b6e25965df1a49a2', query={})
    print (results, err)

    results, err = client.Equities().Financials().ListSECForms('pub_cmp_968b09db15804187b6e25965df1a49a2', query={})
    print (results, err)
    
    # client.Tables().Write(data={})
    # client.Tables().Delete(query={})
    # client.Tables().Update(query={}, data={})

main()