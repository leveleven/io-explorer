import requests
import json
import math
import queue
import _thread

from models import Blocks, BlcokReward
from database import db_session, init_db
from sqlalchemy.exc import IntegrityError
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API_URL = "https://api.io.solutions/v1/io-blocks/blocks/"
TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ink2SUlqV1JidlBKR1pIRzdCYV9rYSJ9.eyJodHRwczovL2lvLm5ldC91c2VyIjp7ImNyZWF0ZWQiOmZhbHNlLCJpb19pZCI6IjJkNWQ0ZGMxLTc2ZTYtNDVjMC05OWEwLWUwYzNhM2U0ZTI3ZCIsInByaW1hcnlfbWFpbCI6ImlwZnNkYXRhMkBnbWFpbC5jb20ifSwiaXNzIjoiaHR0cHM6Ly90ZXN0LXVzZXJzLW1pZ3JhdGlvbi51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjYyN2MwNDFkNTZmODMzYWFjMTYyZTRlIiwiYXVkIjpbImh0dHBzOi8vdGVzdC11c2Vycy1taWdyYXRpb24udXMuYXV0aDAuY29tL2FwaS92Mi8iLCJodHRwczovL3Rlc3QtdXNlcnMtbWlncmF0aW9uLnVzLmF1dGgwLmNvbS91c2VyaW5mbyJdLCJpYXQiOjE3MjExMTE5NzgsImV4cCI6MTcyMjgzOTk3OCwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCB1cGRhdGU6Y3VycmVudF91c2VyX21ldGFkYXRhIHJlYWQ6Y3VycmVudF91c2VyIG9mZmxpbmVfYWNjZXNzIiwiYXpwIjoicnY5amkzb2o0YnRzSWljVXNya0hyN0JzdkNSaHV3SGIifQ.h2Xu4OomRyJTtSbew2jDJn1uBMHLddFIoY_VdgfNmvLEYVZteFKNkYUrVeGvjFZ1ocMR-IlhHb0chxJtfY-o7vOQHlQtIB5IpHy8rhHoN7xGyATHY1dWbpzdOLZClCMsqCYkiHJEk0p1LVoEju0OlFctncr74Z_IWW_2Yd31VfBMjyzQN7kl4utYakZMj23lBLY3gLAmg4wU75alcxqLH7qn8gs6AOQEZBVkTN5-ixNtbzVOLgIZsHO2uESERu3aFeDd4q0_m2JYh-AASKQgtIvO36iURfg-Mpql7jbGd1ABz2BT_R47_sDJ60pFNZmdLPdZhllAeMj-ATXWy3_7sA"
PAGE_SIZE = 20

class DataBase():
    def __init__(self):
        pass

    def create(models, **kwargs):
        w_db = models(**kwargs)
        try:
            db_session.add(w_db)
            db_session.commit()
        except IntegrityError as e:
            db_session.rollback()
            return str(e)

    def serialization():
        pass

def progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', print_end="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        print_end   - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
    # Print New Line on Complete
    if iteration == total: 
        print()

def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session

def initdataset():
    headers = {
        "Token": TOKEN
    }
    # total_workers = 0
    q = queue.Queue()
    session = requests_retry_session()
    
    ## blocks
    blocks, total_workers = get_blocks(session, headers)
    for block in blocks:
        DataBase.create(Blocks, **block)
        # total_workers = total_workers + block["nominated_workers"]
    db_session.close()

    ## blocks reward
    current = 0
    kill_signal = False
    ## 开启队列写入数据库
    try:
        _thread.start_new_thread(queue_to_commit, (q, current, total_workers, kill_signal))
    except:
        print("开启队列进程错误，异常退出")

    for block in blocks[0:10]:
        if block['status'] != "Completed":
            continue
        total_workers_pages = math.ceil(block["nominated_workers"] / PAGE_SIZE)
        pool= ThreadPoolExecutor(max_workers=30)
        # 请求前检查
        find_rewards_count = db_session.query(BlcokReward).filter_by(block_id=block["block_id"]).count()
        if find_rewards_count == block["nominated_workers"]:
            current += block["nominated_workers"]
            continue
        all_task = [pool.submit(get_block_rewards, session, block["block_id"], page, headers, q) for page in range(total_workers_pages)]
        for task in all_task:
            task.result()
        pool.shutdown()

    kill_signal = True

def get_block_rewards(session, block_id, page, headers, q):
    reward_url = API_URL + block_id + "/workers/all/" + str(page+1)
    response = session.get(url=reward_url, headers=headers)
    try:
        data = json.loads(response.text)
        q.put(data["block_rewards"])
    except:
        print(response.text)

def get_blocks(session, headers):
    blocks_url = API_URL + "all/"
    response = session.get(url=blocks_url + "1", headers=headers)
    data = json.loads(response.text)
    total_blocks = data["total_blocks"]
    total_workers = 0

    for block in data["blocks"]:
        total_workers += block["nominated_workers"]

    total_blocks_pages = math.ceil(total_blocks / PAGE_SIZE)
    blocks = []
    for page in range(total_blocks_pages):
        response = session.get(url=blocks_url + str(page + 1), headers=headers)
        data = json.loads(response.text)
        blocks.extend(data["blocks"])
        progress_bar(page + 1, total_blocks_pages, prefix='Fetch remote blocks data:', suffix='Complete', length=50)
    return blocks, total_workers

def queue_to_commit(q, current, total_workers, kill_signal):
    while True:
        if q.empty():
            continue
        rewards = q.get()
        for reward in rewards:
            find_rewards_count = db_session.query(BlcokReward).filter_by(block_id=reward["block_id"], device_id=reward["device_id"]).count()
            if find_rewards_count == 0:
                DataBase.create(BlcokReward, **reward)
            current += 1
            progress_bar(current, total_workers, prefix='Fetch remote reward data:', suffix=str(current) + '/' + str(total_workers) +' Complete', length=50)
        if kill_signal:
            break

# def update():
#     blocks = get_blocks()
#     for block in blocks:
#         exist_block 

if __name__ == "__main__":
    init_db()
    initdataset()
