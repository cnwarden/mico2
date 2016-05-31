# coding:utf-8

from flask import Flask, jsonify, request
from utils.logger import logger
from db.es import ESWrapper
from job.manager import Manager
import config

app = Flask(__name__)
# TODO:logger setting

es_web_client = ESWrapper()


def response_code(code=200, msg='OK', result=None):
    return jsonify(code=code, msg=msg, result=result)


@app.route("/")
def index():
    return """
     <h1>Console Page</h1>
     <ul>
     <li><a href='/docs'>LATEST DOCS</a></li>
     <li><a href='/display?ric=SH000001&count=100'>DISPLAY DOCS</a></li>
     <li><a href='/jobs'>JOBS</a></li>
     <li><a href='/rank'>RANK CONFIGED ITEM</a></li>
     <li><a href='/hot'>HOT SUMMARY</a></li>
     <li><a href='/hot?type=user'>HOT USER</a></li>
     <li><a href='/hot?type=code'>HOT INSTRUMENT</a></li>
     <li><a href='/symbols'>MONITORING SYMBOLS</a></li>
     </ul>
    """


@app.route("/docs")
def request_latest_doc():
    try:
        sym = request.args.get('ric')
        count = int(request.args.get('count')) if request.args.get('count') else 20
        global es_web_client
        docs = es_web_client.get_doc_list(sym, count)
        return jsonify(list=docs)
    except Exception:
        return response_code(msg='error during get latest msgs')

@app.route("/display")
def request_html_display():
    try:
        sym = request.args.get('ric')
        count = int(request.args.get('count')) if request.args.get('count') else 20
        global es_web_client
        docs = es_web_client.get_doc_list(sym, count)
        content = '<style>body{ font-size:12px; background-color:#FFF; color:green; } posttime{background-color:#FFF; color:green;}' \
                  'span:hover{background-color:#DDD; cursor:pointer} ' \
                  '</style>' \
                  '<body>'
        for doc in docs:
            content += '<posttime>%s</posttime> <span>%s</span><br/>' % ( doc['fields']['enrich.post_time_local_str'][0], doc['fields']['enrich.plain_text'][0])
        content += '</body>'
        return content
    except Exception:
        return response_code(msg='error during get latest msgs')

@app.route("/jobs")
def request_job_status():
    content = ''
    for job in Manager.get_status()['jobs']:
        content += 'ID:%s Name:%s NextTime:%s <a href="/run_job?id=%s">RUN</a><br/>' \
                   % (job['id'], job['name'], job['next_time'], job['id'])
    return content
    # return jsonify(Manager.get_status())
    # return response_code()


@app.route("/run_job")
def request_job_run():
    job_id = request.args.get('id')
    logger.debug('run_job:%s' % job_id)
    next_run = Manager.run_job(job_id)
    return response_code()


@app.route("/stats")
def request_stats():
    ric = request.args.get('ric') if request.args.get('ric') else 'SH000001'
    global es_web_client
    count = es_web_client.get_stats(ric)
    return response_code(result={'count': count})


@app.route("/rank")
def request_rank():
    global es_web_client
    rank_list = es_web_client.get_rank()
    return response_code(result={'rank': rank_list})


@app.route("/hot")
def request_hot():
    type = request.args.get('type') if request.args.get('type') else 'summary'
    global es_web_client
    result = es_web_client.get_all_ranks()
    if type == 'user':
        return response_code(result={'user': result['user_rank']})
    elif type == 'code':
        return response_code(result={'name': result['name_rank'], 'code': result['code_rank']})
    else:
        return response_code(result={'summary': result['summary']})

@app.route('/hotstock')
def request_hot_job():
    global es_web_client
    result = es_web_client.get_all_ranks()
    content = '<a href=#>RUN TOP</a><br/><ul>'
    if result['name_rank']:
        for item in result['name_rank']:
            content += '<li><a href="https://www.baidu.com/s?wd=%s">%s</a>-%d</li>' % (item[0], item[0], item[1])
    content += '</ul>'
    return content

@app.route("/dump")
def request_dump():
    global es_web_client
    filename, total_count = es_web_client.dump()
    return response_code(result={'file': filename, 'count': total_count})


@app.route("/symbols")
def request_symbol():
    global es_web_client
    return response_code(result={'size': len(config.STOCK_LIST), 'symbol':config.STOCK_LIST})