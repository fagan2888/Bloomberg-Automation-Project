import blpapi as blp
##import pdblp as blp
from optparse import OptionParser
import json

##Configuration Stage
with open("Configuration.json") as json_file:
    basic_config=json.load(json_file)

APIFLDS_SVC="[Name of the Service]"

FIELD_ID = blpapi.Name("id")
FIELD_MNEMONIC = blpapi.Name("mnemonic")
FIELD_DATA = blpapi.Name("fieldData")
FIELD_DESC = blpapi.Name("description")
FIELD_INFO = blpapi.Name("fieldInfo")
FIELD_ERROR = blpapi.Name("fieldError")
FIELD_MSG = blpapi.Name("message")

ID_LEN = 13
MNEMONIC_LEN = 36
DESC_LEN = 40

##Setting Up Connection:
def parseCmdLine():
    parser = OptionParser(description="Swap Manager Automation")
    parser.add_option("-a",
                      "--ip",
                      dest="host",
                      help="server name or IP (default: %default)",
                      metavar="ipAddress",
                      default="localhost")
    parser.add_option("-p",
                      dest="port",
                      type="int",
                      help="server port (default: %default)",
                      metavar="tcpPort",
                      default=8194)

    (options, args) = parser.parse_args()

    return options

def printField(field):
    fldId = field.getElementAsString(FIELD_ID)
    if field.hasElement(FIELD_INFO):
        fldInfo = field.getElement(FIELD_INFO)
        fldMnemonic = fldInfo.getElementAsString(FIELD_MNEMONIC)
        fldDesc = fldInfo.getElementAsString(FIELD_DESC)

        print("%s%s%s" % (fldId.ljust(ID_LEN), fldMnemonic.ljust(MNEMONIC_LEN),
                          fldDesc.ljust(DESC_LEN)))
    else:
        fldError = field.getElement(FIELD_ERROR)
        errorMsg = fldError.getElementAsString(FIELD_MSG)

        print()
        print(" ERROR: %s - %s" % (fldId, errorMsg))


def printHeader():
    print("%s%s%s" % ("FIELD ID".ljust(ID_LEN), "MNEMONIC".ljust(MNEMONIC_LEN),
                      "DESCRIPTION".ljust(DESC_LEN)))
    print("%s%s%s" % ("-----------".ljust(ID_LEN), "-----------".ljust(MNEMONIC_LEN),
                      "-----------".ljust(DESC_LEN)))

def main():
    global options
    options=parseCmdLine()

    #Fill Session options
    sessionOptions=blpapi.SessionOptions()
    sessionOptions.setServerHost(options.host)
    sessionOptions.setServerPort(options.port)

    print("Connecting to %s:%d" % (options.host, options.port))

    # Create a Session
    session = blpapi.Session(sessionOptions)

    # Start a Session
    if not session.start():
        print("Failed to start session.")
        return

    if not session.openService(APIFLDS_SVC):
        print("Failed to open", APIFLDS_SVC)
        return

    fieldInfoService = session.getService(APIFLDS_SVC)
    request = fieldInfoService.createRequest("FieldSearchRequest")
    request.set("searchSpec", "last price")
    exclude = request.getElement("exclude")
    exclude.setElement("fieldType", "Static")
    request.set("returnFieldDocumentation", False)

    print("Sending Request:", request)
    session.sendRequest(request)

    printHeader()
    try:
        # Process received events
        while(True):
            # We provide timeout to give the chance to Ctrl+C handling:
            event = session.nextEvent(500)
            if event.eventType() != blpapi.Event.RESPONSE and \
                    event.eventType() != blpapi.Event.PARTIAL_RESPONSE:
                continue
            for msg in event:
                fields = msg.getElement("fieldData")
                for field in fields.values():
                    printField(field)
                print()
            # Response completly received, so we could exit
            if event.eventType() == blpapi.Event.RESPONSE:
                break
    finally:
        # Stop the session
        session.stop()