from graham import GrahamClient
import os

def main():
    client = GrahamClient(os.getenv('API_KEY'), os.getenv('COMPANY_ID'))

    results, err = client.Tables(os.getenv('TABLE_ID')).Read(query={})
    print (results, err)
    # client.Tables().Write(data={})
    # client.Tables().Delete(query={})
    # client.Tables().Update(query={}, data={})

main()