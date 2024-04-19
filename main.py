import flask
from googleapiclient.errors import HttpError

import sheetsApi.sheets as sheets

import asyncio
import threading
import time

app = flask.Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

SPREADSHEET_ID = "1cJy3DYsIVj5pbszMqrekUNod-PeCrM7OCNKrhstQsnY"
ROOT_ROW = 2 

SHEET_RANGE = "A2:D"
CODE_INDEX = 0 
NUMBER_INDEX = 1
NAME_INDEX = 2 
ENTERED_INDEX = 3 

CODE_COL = "A"
NUMBER_COL = "B"
NAME_COL = "C"
ENTERED_COL = "D"

loop = None
def start_loop():
    global loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_forever()

loop_thread = threading.Thread(target=start_loop)
loop_thread.daemon = True 
loop_thread.start()

def run_coroutine_in_loop(coroutine):
    if loop is not None:
        asyncio.run_coroutine_threadsafe(coroutine, loop)

loop2 = None
def start_loop2():
    global loop2
    loop2 = asyncio.new_event_loop()
    asyncio.set_event_loop(loop2)
    loop2.run_forever()

loop_thread2 = threading.Thread(target=start_loop2)
loop_thread2.daemon = True 
loop_thread2.start()

def run_coroutine_in_loop2(coroutine):
    if loop2 is not None:
        asyncio.run_coroutine_threadsafe(coroutine, loop2)

@app.route('/')
def index():
    return flask.render_template("index.html")

async def updateCallback(sheets, cell):
    sheets.updateValue(SPREADSHEET_ID, f"LinkTicketSheet!{cell}", True)

@app.route('/checkin')
def checkin():
    # Returns JSON response, takes HTML args as input
    code = flask.request.args.get("code")
    logLine("Check-in:  " + code)

    try:
        values = sheets.getValues(SPREADSHEET_ID, f"LinkTicketSheet!{SHEET_RANGE}", run_coroutine_in_loop)

        ticketCode = [row[CODE_INDEX] for row in values]
        ticketStatus = [row[ENTERED_INDEX] for row in values]
        rawCode = code.lstrip("TICKET")
                
        
        if rawCode in ticketCode:
            i = ticketCode.index(rawCode)
            # Fetch other details
            number = values[i][NUMBER_INDEX]
            name = values[i][NAME_INDEX]
            
            if ticketStatus[i] == "FALSE":
                # Set status to true
                row = str(i + ROOT_ROW)
                status_cell = ENTERED_COL + row 
                
                run_coroutine_in_loop2(updateCallback(sheets, status_cell))

                logLine("Check-in:  " + code + ": Success")
                return f"1\n{number}\n{name}"
            elif ticketStatus[i] == "TRUE":
                # Already checked in, return 0
                logLine("Check-in:  " + code + ": Already checked in")
                return f"0\n{number}\n{name}"
        else:
            # Invalid ticket code, return -1
            logLine("Check-in:  " + code + ": Invalid ticket code")
            return "-1"
    except HttpError as err:
        logLine(err)
        logLine("Check-in:  " + code + ": Error")
        return "-2" + err.resp.status

    return "WTF"
    
# @app.route('/checkout')
# def checkout():
#     # Returns JSON response, takes HTML args as input
#     code = flask.request.args.get("code")
#     logLine("Check-out: " + code)

def logLine(line):
    #print(line)
    with open("log/general.log", "a") as logFile:
        logFile.write(line + "\n")

def main():
    app.run(port=80, host="0.0.0.0")

if __name__ == "__main__":
    main()
