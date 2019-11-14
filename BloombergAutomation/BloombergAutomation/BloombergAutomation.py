import blpapi as blp
##import pdblp as blp
from optparse import OptionParser
import json

##Configuration Stage
with open("Configuration.json") as json_file:
    basic_config=json.load(json_file)

print(basic_config)


def printErrorInfo(leadingStr, errorInfo):
    print("%s%s (%s)" % (leadingStr, errorInfo.getElementAsString(CATEGORY),
                         errorInfo.getElementAsString(MESSAGE)))

def processMessage(msg):
    pass

def processResponseEvent(event):
    for msg in event:
        print(msg)
        if msg.hasElement(RESPONSE_ERROR):
            printErrorInfo("REQUEST FAILED: ", msg.getElement(RESPONSE_ERROR))
            continue
        processMessage(msg)

def eventLoop(session):
    done = False
    while not done:
        # nextEvent() method below is called with a timeout to let
        # the program catch Ctrl-C between arrivals of new events
        event = session.nextEvent(500)
        if event.eventType() == blpapi.Event.PARTIAL_RESPONSE:
            print("Processing Partial Response")
            processResponseEvent(event)
        elif event.eventType() == blpapi.Event.RESPONSE:
            print("Processing Response")
            processResponseEvent(event)
            done = True
        else:
            for msg in event:
                if event.eventType() == blpapi.Event.SESSION_STATUS:
                    if msg.messageType() == SESSION_TERMINATED:
                        done = True

def main():
    options = parseCmdLine()

    # Fill SessionOptions
    sessionOptions = blpapi.SessionOptions()
    sessionOptions.setServerHost(options.host)
    sessionOptions.setServerPort(options.port)

    print("Connecting to %s:%s" % (options.host, options.port))
    # Create a Session
    session = blpapi.Session(sessionOptions)

    # Start a Session
    if not session.start():
        print("Failed to start session.")
        return

    try:
        # Open service to get historical data from
        if not session.openService("//blp/refdata"):
            print("Failed to open //blp/refdata")
            return
        SWPMRequest(session,options)
        # wait for events from session.
        eventLoop(session)

    finally:
        # Stop the session
        session.stop()

if __name__ == "__main__":
    print("IntradayBarExample")
    try:
        main()
    except KeyboardInterrupt:
        print("Ctrl+C pressed. Stopping...")