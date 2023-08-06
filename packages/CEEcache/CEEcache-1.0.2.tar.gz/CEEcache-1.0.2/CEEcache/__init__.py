import json
import hashlib
import os
import redis
import time
import copy
from CEEcache.logger import log_emmiter
import requests
import sys
import traceback

def sort_json_recursively(d):
    if isinstance(d, dict):
        new_dict = {}
        for k in sorted(d.keys()):
            new_dict[k] = sort_json_recursively(d[k])
        return new_dict
    elif isinstance(d, list):
        if d and isinstance(d[0], dict):
            for i in range(len(d)):
                d[i] = sort_json_recursively(d[i])
            ls = [json.dumps(obj) for obj in d]
            ls.sort()
            d = [json.loads(obj) for obj in ls]
            return d
        else:
            return sorted(d)
    else:
        return d

def generate_key(payload, md5_key_include, md5_key_exclude, prepend_key, request_id):
    try:
        global md5_key
        payload_copy = copy.deepcopy(payload)
        # If both md5_key_include and md5_key_exclude is passed then only md5_key_include will be given selected.
        if md5_key_include:
            filtered_payload = {k: v for k, v in payload_copy.items() if k in md5_key_include}
        elif md5_key_exclude:
            filtered_payload = {k: v for k, v in payload_copy.items() if k not in md5_key_exclude}
        else:
            filtered_payload = payload_copy
        filtered_payload = sort_json_recursively(filtered_payload)
        json_string = json.dumps(filtered_payload)
        md5_hash = hashlib.md5(json_string.encode()).hexdigest()
        client_id = payload_copy["cid"]
        md5_key = f"{client_id}_{md5_hash}"
        if prepend_key:
            md5_key = prepend_key + "_" + md5_key
        log_emmiter({"request_id": request_id, "key_generated": md5_key})
    except:
        e = sys.exc_info()
        traceback_output = "".join(traceback.format_exception(e[0], e[1], e[2]))
        err_msg = f"Error occured while generating key for request_id: {request_id}\n{str(traceback_output)}"
        print(err_msg)
        log_emmiter({"request_id": request_id, "message": err_msg}, "ERROR")
        send_slack_alert(err_msg, request_id)
        md5_key = None

def send_slack_alert(err_msg, request_id):
    url = os.environ.get("slack_web_hook", "")
    headers = {"Content-Type": "application/json"}
    payload = {"text": err_msg}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        err_msg = f"Failed to send Slack message. Error: {response.text}"
        print(err_msg)
        log_emmiter({"request_id": request_id, "message": err_msg}, "ERROR")

def connect_to_redis(request_id):
    max_attempts = 3
    retry_delay = 3
    host = os.environ.get("cache_redis_host", "")
    port = int(os.environ.get("cache_redis_port", 0))
    r = redis.Redis(host, port, db = 0)
    for attempt in range(max_attempts):
        try:
            if r.ping():
                return r
            else:
                time.sleep(retry_delay)
        except:
            time.sleep(retry_delay)
    err_msg = f"Error occured while connecting to redis host: {host}, port: {port} within the caching library.\nrequest_id: {request_id}"
    print(err_msg)
    log_emmiter({"request_id": request_id, "message": err_msg}, "ERROR")
    send_slack_alert(err_msg, request_id)
    return None

def read_from_redis(request_id):
    r = connect_to_redis(request_id)
    if r is None:
        return None
    resp = None
    if r.exists(md5_key):
        resp_str = r.hget(md5_key, "value").decode("utf-8")
        resp = json.loads(resp_str)
    r.close()
    return resp

def write_to_redis(payload, value):
    caching_info = payload.get("caching_info", {})
    ttl = caching_info.get("stale_time_acceptable", int(os.environ.get("stale_time_acceptable", 0)))
    force_reset = caching_info.get("force_reset", 0)
    request_id = payload.get("request_id", "")
    
    if ttl == 0:
        return None
    if md5_key is None:
        return None
    
    r = connect_to_redis(request_id)
    if r is None:
        return None
    
    timestamp = time.time()
    r.hset(md5_key, "value", json.dumps(value))
    r.hset(md5_key, "set_time", timestamp)
    if force_reset == 1 or r.ttl(md5_key) < ttl * 60:
        r.expire(md5_key, ttl * 60)
    r.close()

def get_cache_set_time(request_id):
    r = connect_to_redis(request_id)
    if r is None:
        return None
    resp_str = r.hget(md5_key, "set_time").decode("utf-8")
    resp = float(resp_str)
    r.close()
    return resp

def change_ttl(ttl, request_id):
    r = connect_to_redis(request_id)
    if r is None:
        return None
    if r.ttl(md5_key) < ttl * 60:
        r.expire(md5_key, ttl * 60)
    r.close()

def main(payload, md5_key_include, md5_key_exclude):
    request_id = payload.get("request_id", "")
    caching_info = payload.get("caching_info", {})
    stale_time_acceptable = caching_info.get("stale_time_acceptable", int(os.environ.get("stale_time_acceptable", 0)))
    force_reset = caching_info.get("force_reset", 0)
    prepend_key = caching_info.get("prepend_key", os.environ.get("prepend_key", None))
    
    if stale_time_acceptable == 0:
        message = "stale_time_acceptable == 0. Real Time data request. Querying vertica..."
        print(message)
        log_emmiter({"request_id": request_id, "message": message})
        return None
    
    generate_key(payload, md5_key_include, md5_key_exclude, prepend_key, request_id)
        
    if md5_key is None:
        return None

    if force_reset == 1:
        message = "force_reset == 1. Querying vertica and writing to redis"
        print(message)
        log_emmiter({"request_id": request_id, "message": message})
        return None
    
    ret = read_from_redis(request_id)

    if ret is None:
        message = "Key not found in redis. Querying vertica and writing to redis."
        print(message)
        log_emmiter({"request_id": request_id, "message": message})
        return None
    
    set_time = get_cache_set_time(request_id)
    if set_time is None:
        return None
    acceptable_time_for_key = set_time + stale_time_acceptable * 60
    if acceptable_time_for_key < time.time():
        message = "Data is older than stale_time_acceptable. Querying vertica and writing to redis."
        print(message)
        log_emmiter({"request_id": request_id, "message": message})
        return None
    
    message = "Data found within the stale_time_acceptable. Returning from redis."
    print(message)
    log_emmiter({"request_id": request_id, "message": message})
    change_ttl(stale_time_acceptable, request_id)
    return ret