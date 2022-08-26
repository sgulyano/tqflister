import os
import json 
import pandas as pd

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


columns = ["type", "project_id", "private_key_id", "private_key", 
           "client_email", "client_id", "auth_uri", "token_uri", "auth_provider_x509_cert_url", "client_x509_cert_url"]
service_account_info = json.dumps({c:os.environ[c].replace("\\n", '\n') for c in columns})

# service_account_info['private_key'] = service_account_info['private_key'].replace("\\\\", "\\")


class TQFSheet:
    def __init__(self, tqf, credentials):
        try:
            self.service = build('sheets', 'v4', credentials=credentials)
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error
        self.spreadsheet_id = '1CC6uk-84V1S319pFaQ5fYNVBlOqhso6kXuWa-95BiJo' # TQF3
        # self.rows = None
        if tqf == 3 or tqf == 5:
            self.tqf = tqf
        else:
            raise Exception('Unknown TQF')

    def read_data(self, from_year=0):
        range_name = f'tqf{self.tqf}!A:C'
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id, 
                range=range_name).execute()

            rows = result.get('values', [])
            print(f"{len(rows)-1} rows of TQF{self.tqf} retrieved.")
            # self.rows = len(rows)
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error
        df = pd.DataFrame(rows[1:], columns=rows[0]).astype({'classid': 'int32', 'year': 'int16'})
        df = df[df['year'] >= from_year]
        return df

    def write_data(self, values):
        # if self.rows is None:
        #     print("Must call read_data function first")
        #     return None
        try:
            body = {'values': values}
            value_input_option = "USER_ENTERED"
            # range_name = f'tqf{self.tqf}!A{self.rows+1}:C{self.rows+len(values)}'
            range_name = f'tqf{self.tqf}!A:C'

            # result = self.service.spreadsheets().values().update(
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id, 
                range=range_name,
                valueInputOption=value_input_option, 
                body=body).execute()
            print(f"{result.get('updates').get('updatedRows')} rows of TQF{self.tqf} updated.")
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error

# service_account_info = json.load(open('service_account.json'))
# credentials = service_account.Credentials.from_service_account_info(
#     service_account_info)

def write_tqf_data(credentials, values):
    try:
        service = build('sheets', 'v4', credentials=credentials)

        body = {'values': values}
        value_input_option = "USER_ENTERED"
        range_name = f'data!A:H'
        spreadsheet_id = '1ZDpk-Pp3gKyc6J7wQUFI6IuU_zS-gLWf21BcxvDHNdo'

        # result = self.service.spreadsheets().values().update(
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption=value_input_option, body=body).execute()
        print(f"{result.get('updatedRows')-1} rows updated.")
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error

def read_tqf_data(credentials):
    try:
        service = build('sheets', 'v4', credentials=credentials)
        range_name = f'data!A:H'
        spreadsheet_id = '1ZDpk-Pp3gKyc6J7wQUFI6IuU_zS-gLWf21BcxvDHNdo'

        # result = self.service.spreadsheets().values().update(
        result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id, 
                range=range_name).execute()
        rows = result.get('values', [])
        print(f"{len(rows)-1} rows retrieved.")
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error
    df = pd.DataFrame(rows[1:], columns=rows[0]).astype({'ID': 'int32', 'Year': 'int16'})
    return df