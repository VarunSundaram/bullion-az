import datetime
import logging
import azure.functions as func
import positionaltrade as ps

app = func.FunctionApp()

@app.schedule(schedule="0 50 15 * * *", arg_name="myTimer", run_on_startup=True,
              use_monitor=False) 
def loftypts(myTimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    ps.startSession()
