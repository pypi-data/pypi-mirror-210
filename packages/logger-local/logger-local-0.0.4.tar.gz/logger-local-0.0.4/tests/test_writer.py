import pymysql
import os
from src.MessageSeverity import MessageSeverity
from src.LoggerServiceSingleton import locallgr

ID = 5000001
# ID = 1

def get_connection() -> pymysql.connections.Connection:
    return pymysql.connect(
        user=os.getenv('RDS_USERNAME'),
        password=os.getenv('RDS_PASSWORD'),
        host=os.getenv('RDS_HOSTNAME'),
        database=os.getenv('RDS_DB_NAME')
    )
def test_log():
    object_to_insert_1 = {
        'ipv4': 'ipv4-py',
        'ipv6': 'ipv6-py',
        'latitude': 33,
        'longitude': 35,
        'user_id': ID,
        'profile_id': ID,
        'activity': 'test from python',
        'activity_id': ID,
        'payload': 'log from python -object_1',
        'component_id': ID,
        'variable_id': ID,
        'variable_value_old': 'variable_value_old-python',
        'variable_value_new': 'variable_value_new-python',
        'created_user_id': ID,
        'updated_user_id': ID
    }
    locallgr.info(object=object_to_insert_1)
    conn = get_connection()
    cursor = conn.cursor()
    sql = f"""SELECT severity_id FROM logger.logger_table WHERE payload = '{object_to_insert_1['payload']}' ORDER BY timestamp DESC LIMIT 1;"""
    cursor.execute(sql)
    result = cursor.fetchone()
    assert result[0] == MessageSeverity.Information.value

def test_error():
    object_to_insert_2 = {
        'ipv4': 'ipv4-py',
        'ipv6': 'ipv6-py',
        'latitude': 33,
        'longitude': 35,
        'user_id': ID,
        'profile_id': ID,
        'activity': 'test from python',
        'activity_id': ID,
        'payload': 'payload from python -object_2',
        'component_id': ID,
    }
    locallgr.error(object=object_to_insert_2)
    conn = get_connection()
    cursor = conn.cursor()
    sql = f"""SELECT severity_id FROM logger.logger_table WHERE payload = '{object_to_insert_2['payload']}' ORDER BY timestamp DESC LIMIT 1;"""
    cursor.execute(sql)
    result = cursor.fetchone()
    assert result[0] == MessageSeverity.Error.value

def test_verbose():
    object_to_insert_3 = {
        'ipv4': 'ipv4-py',
        'ipv6': 'ipv6-py',
        'latitude': 33,
        'longitude': 35,
        'variable_id': ID,
        'variable_value_old': 'variable_value_old-python-object_3',
        'variable_value_new': 'variable_value_new-python',
        'created_user_id': ID,
        'updated_user_id': ID
    }
    locallgr.verbose(object=object_to_insert_3)

    conn = get_connection()
    cursor = conn.cursor()
    sql = f"""SELECT severity_id FROM logger.logger_table WHERE variable_value_old = '{object_to_insert_3['variable_value_old']}' ORDER BY timestamp DESC LIMIT 1;"""
    cursor.execute(sql)
    result = cursor.fetchone()
    assert result[0] == MessageSeverity.Verbose.value
def test_warn():
    object_to_insert_4 = {
        'ipv4': 'ipv4-py',
        'ipv6': 'ipv6-py',
        'latitude': 33,
        'longitude': 35,
        'user_id': ID,
        'profile_id': ID,
        'activity': 'test from python',
        'activity_id': ID,
        'payload': 'payload from python -object_4',
        'variable_value_new': 'variable_value_new-python',
        'created_user_id': ID,
        'updated_user_id': ID
    }
    locallgr.warn(object=object_to_insert_4)

    conn = get_connection()
    cursor = conn.cursor()
    sql = f"""SELECT severity_id FROM logger.logger_table WHERE payload = '{object_to_insert_4['payload']}' ORDER BY timestamp DESC LIMIT 1;"""
    cursor.execute(sql)
    result = cursor.fetchone()
    assert result[0] == MessageSeverity.Warning.value
def test_add_message():
    # option to insert only message
    message = 'only message error from python'
    locallgr.error(message)

    conn = get_connection()
    cursor = conn.cursor()
    sql = f"""SELECT severity_id FROM logger.logger_table WHERE payload = '{message}' ORDER BY timestamp DESC LIMIT 1;"""
    cursor.execute(sql)
    result = cursor.fetchone()
    assert result[0] == MessageSeverity.Error.value

def test_debug():
    object_to_insert_5 = {
        'payload': 'just payload & activity_id - python',
        'activity_id': ID
    }
    locallgr.debug(object=object_to_insert_5)

    conn = get_connection()
    cursor = conn.cursor()
    sql = f"""SELECT severity_id FROM logger.logger_table WHERE payload = '{object_to_insert_5['payload']}' ORDER BY timestamp DESC LIMIT 1;"""
    print(sql)
    cursor.execute(sql)
    result = cursor.fetchone()
    assert result[0] == MessageSeverity.Debug.value








