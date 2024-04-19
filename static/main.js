import QrScanner from "/static/qr-scanner/qr-scanner.min.js"; // if using plain es6 import

const recentRequests = {}

function main() {
  setupScanner();
}

function setupScanner() {
  const videoElem = document.getElementById("qrVideo");

  const qrScanner = new QrScanner(
    videoElem,
    async (result) => {
      //document.getElementById("test").innerHTML = "decoded qr code: " + result.data;
      const code = result.data;

      // Format checks
      if (code.startsWith("TICKET")) {
        //test2.innerHTML = "QUERYING" + code
        queryTicket(code);
      }
    },
    {
      maxScansPerSecond: 5,
      highlightScanRegion: true,
      highlightCodeOutline: true,
    }
  );

  qrScanner.start()
}

function queryTicket(scannedId) {
  // Check for recent request
  // Send request to server
  // Receive status code
  // Display in page
  
  const time = (new Date()).getTime()
  if ((recentRequests[scannedId] != undefined) && (time - recentRequests[scannedId] < 2000)) {
    return
  } else {
    recentRequests[scannedId] = time
  }

  const mode = queryModeId 


  //document.getElementById("test").innerHTML = scannedId + "Sending request" 
  const xhr = new XMLHttpRequest()
  let path = ""
  if (mode == 0) {
    path = "checkin?code=" + scannedId 
  } else {
    path = "checkout?code=" + scannedId
  }
  xhr.open("GET", path)
  xhr.send()

  xhr.onload = (response) => {
    if (xhr.readyState == 4 & xhr.status == 200) {
      console.log(xhr.response)
      ticketQueryResponse(mode, xhr.response)
    } else {
      ticketQueryResponse(mode, "-2: " + xhr.status)
    }
  }
}

function ticketQueryResponse(mode, response){
  let success = false
  let status = ""

  const statusLine = response.split("\n")[0]
  const statusCode = parseInt(statusLine.split(":")[0])

  if (statusCode == 1) {
    status = "Success"
    success = true
  } else if (statusCode == 0) {
    if (mode == 0) {
      status = "Already Entered"
    } else if (mode == 0){
      status = "Already Left"
    }
  } else if (statusCode == -1) {
    status = "Invalid QR code. Please try again or edit the sheet"
  } else if (statusCode == -2){
    status = statusLine.split(":"[1])
  }

  if (status == ""){
    status = "Error handling response. Please manually edit the sheet"
  }

  if (statusCode == 1 || statusCode == 0){
    const number = response.split('\n')[1]
    const name = response.split("\n")[2]
    displayResponse(success, status, number, name)
  } else {
    displayResponse(success, status, 0, "")
  }
}

let timeout = null
function displayResponse(success, status, number, name){ 
  console.log(`${success}, ${status}, ${number}, ${name}`)

  const audio = new Audio("/static/assets/twobeeps.mp3")
  audio.play()
  
  const resultsElm = document.getElementById("results") 
  const prevSuccess = resultsElm.classList.contains("success")
  if (!prevSuccess && success){
    resultsElm.classList.add("success")
  } else if (prevSuccess && !success){
    resultsElm.classList.remove("success")
  }

  document.getElementById("status").innerHTML = status 
  document.getElementById("number").innerHTML = number 
  document.getElementById("name").innerHTML = name

  resultsElm.classList.add('visible')
  clearTimeout(timeout)
  timeout = setTimeout(() => {
    document.getElementById("results").classList.remove("visible")
  }, 3000)
}

let queryModeId = 0

function setupModes(){
  document.getElementById("modeOne").addEventListener("click", () => {
    updateMode(0)
  })
  document.getElementById("modeTwo").addEventListener("click", () => {
    updateMode(1)
  })
}

function updateMode(modeId){
  queryModeId = modeId
  if (modeId == 0){
    document.getElementById("modeOne").classList.add("selected")
    document.getElementById("modeTwo").classList.remove("selected")
  } else {
    document.getElementById("modeTwo").classList.add("selected")
    document.getElementById("modeOne").classList.remove("selected")
  }
}

setupScanner();
//setupModes();
