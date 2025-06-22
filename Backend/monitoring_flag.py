main_monitoring_should_stop = False

def set_main_monitoring_should_stop(value: bool):
    global main_monitoring_should_stop
    main_monitoring_should_stop = value

def get_main_monitoring_should_stop():
    return main_monitoring_should_stop 