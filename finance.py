import yfinance as yf
import os.path
import pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from datetime import date

from typing import List

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def read_file(filename: str) -> str:
    with open(filename, "r") as f:
        return f.read()


def retrieve_ticker_names():
    return read_file("ticker_list")


def get_spreadsheet_id():
    return read_file("spreadsheet")


def create_tabs(new_tabs: List[str], sheet_service, sheet_id: str):
    """
    Create tabs on the finance spreadsheet only if needed
    :param tabs: tabs to be created for the spreadsheet
    :param sheet_service: google service for spreadsheet
    :param sheet_id: id of the spreadsheet where to create tabs
    :return request result or None if nothing happened
    """
    request = []
    finance_sheet = sheet_service.get(spreadsheetId=sheet_id).execute()
    finance_sheet_tabs = [tab["properties"]["title"] for tab in finance_sheet["sheets"]]
    for new_tab in new_tabs:
        if new_tab not in finance_sheet_tabs:
            request.append(add_sheet_request(title=new_tab))
    if request:
        body = {'requests': request}
        return sheet_service.batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()


def add_sheet_request(title: str):
    return {
        'addSheet': {
            'properties': {
                "title": title,
                'hidden': "true"
            }
        }
    }


def get_google_creds():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds


if __name__ == '__main__':
    ticker_list = retrieve_ticker_names()
    tickers = yf.Tickers(ticker_list)
    stock_infos = []
    for ticker in tickers.tickers:
        info = ticker.info
        stock_infos.append((info['longName'], info['previousClose']))

    tabs = [stock_name for stock_name, _ in stock_infos]
    spreadsheet_id = get_spreadsheet_id()
    google_service = build('sheets', 'v4', credentials=get_google_creds())
    sheet = google_service.spreadsheets()

    create_tabs(tabs, sheet, spreadsheet_id)
    now = date.today()

    for stock_name, value in stock_infos:
        values = [[str(now)], [value]]
        b = {'values': values}
        sheet.values().\
            append(spreadsheetId=spreadsheet_id, valueInputOption="USER_ENTERED", range=stock_name, body=b).\
            execute()
    #values = result.get('values', [])
    #print(result.get('replies'))
    #print(values)
