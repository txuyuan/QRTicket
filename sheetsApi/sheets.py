import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import sheetsApi.cache as sheetCache
import asyncio
import time

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
lastTime = 0

# Cache Values 
CACHE_REFRESH_REQUESTS = 2

def getValues(spreadsheet_id, sheet_range, run_coroutine_in_loop=None, bypass_cache=False):
    cacheKey = spreadsheet_id + "+" + sheet_range 
    
    cacheResult = sheetCache.fetch(cacheKey)
    if cacheResult != False and not bypass_cache:      
        # Cached return 
        global lastTime 
        epoch = int(time.time())
        if (epoch - lastTime) > 2:
            run_coroutine_in_loop(asyncUpdateValues(spreadsheet_id, sheet_range))
            lastTime = epoch 

        return cacheResult 

    service = getService()

    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(
            spreadsheetId=spreadsheet_id, 
            range=sheet_range
        )
        .execute()
    )
    values = result.get("values", [])

    sheetCache.save(cacheKey, values)
    return values

async def asyncUpdateValues(spreadsheet_id, sheet_range):
    getValues(spreadsheet_id, sheet_range, bypass_cache=True)

def updateValue(spreadsheet_id, sheet_cell, value):
    service = getService()

    values = [[value]]
    body = {
        "values": values
    }

    sheet = service.spreadsheets()
    result = (
        sheet
        .values()
        .update(
            spreadsheetId=spreadsheet_id,
            range=sheet_cell,
            valueInputOption="RAW",
            body=body
        )
        .execute()
    )
    return result.get('updatedCells')

def getService():
    creds = None
    if os.path.exists("sheetsApi/token.json"):
        creds = Credentials.from_authorized_user_file("sheetsApi/token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                    "sheetsApi/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("sheetsApi/token.json", "w") as token:
            token.write(creds.to_json())

    service = build("sheets", "v4", credentials=creds)
    return service

async def main():
        print("TEST")

        for i in range(10):
                SPREADSHEET_ID = "1cJy3DYsIVj5pbszMqrekUNod-PeCrM7OCNKrhstQsnY"
                getValues(SPREADSHEET_ID, "A2:B")
                print("==" + str(i))


if __name__ == "__main__":
        print("You are running a test of the cache system")
        asyncio.run(main())
