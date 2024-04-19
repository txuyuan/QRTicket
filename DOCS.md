/check-in:
    In: code[String] 
    Out: status
        1: Success
        0: Already checked-in
        -1: Invalid code
        -2 + ErrorStr: Error

/check-out:
    In: code[String]
    Out: status
        1: Success 
        0: Already checked-out 
        -1: Invalid code
        -2 + ErrorStr: Error

<statusCode|int>: <statusContent?(only if statusCode -2)|string>
<number|int>
<name|string>
<claimed|bool>
