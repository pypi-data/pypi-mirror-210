import os
import re
import time
from common import log
from common import basefunc
from tradeTools import helpers
import traceback

def load_codes():
    reQuery = True
    stock_info = []
    today_date = int(time.strftime('%Y%m%d', time.localtime(time.time())))
    baseRoot = basefunc.get_path_dirname()
    codeFile =f'{baseRoot}/rec/codes.txt'
    if not os.path.exists(codeFile):
        log.WriteLog("sys", f"codeFile not exists {codeFile}")
    else:
        log.WriteLog("sys", f"codeFile exists {codeFile}")
    try:
        with open(codeFile,'rt', encoding='utf8') as f:
            c = f.read()
            if len(c) >0:
                ls = c.split('\n')
                if int(ls[0]) >= today_date: reQuery = False
                for l in ls[1:]:
                    try:
                        e = re.split(r'\s+', l)
                        stock_info.append({'code': e[0], 'name': e[1]})
                    except:
                        pass
    except Exception as e:
        log.WriteLog("sys", str(traceback.format_exc()))

    log.WriteLog("sys", "load codes %s" % len(stock_info))

    if reQuery:
        codes = helpers.get_codes_from_web()
        if len(codes):
            stock_info = codes
            with open(codeFile, 'w', encoding='utf-8') as f:
                f.write(f'{today_date}\n')
                for info in stock_info:
                    f.write(f'{info["code"]}\t{info["name"]}\n')
                    
    return reQuery, stock_info
                    

if __name__ == '__main__':
    reQuery, stock_info = load_codes()
    print('Query new:', 'yes' if reQuery else 'no')
    
    print('print 10 codes')
    for si in stock_info[:10]:
        print(si)
    
    