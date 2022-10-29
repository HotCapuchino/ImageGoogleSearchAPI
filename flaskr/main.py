from time import time
from flask import Flask, jsonify, request as flask_request
from controllers import ImageSearchController
from flask_cors import CORS, cross_origin

from models.request import PaginationArgs
from multiprocessing.pool import Pool
import os
import time


app = Flask(__name__)
CORS(app, support_credentials=True)


def get_pagination_args():
    page = flask_request.args.get('page')
    per_page = flask_request.args.get('per_page')

    if page and per_page:
        return PaginationArgs(page, per_page)
    return None


class ResultAccumulator:
    def __init__(self) -> None:
        self.val = {}

    def update_results(self, obj):
        key = obj['search']
        images_list = obj['result']

        self.val[key] = images_list


@app.route('/search/images')
@cross_origin(supports_credentials=True)
def search():
    search_args = flask_request.args.getlist('search')
    pagintaion_args = get_pagination_args()

    result_accumulator = ResultAccumulator()

    pool = Pool(processes=os.cpu_count())
    start_time = time.time()

    for search_arg in search_args:
        pool.apply_async(ImageSearchController.get_searched_images,
                         (search_arg, pagintaion_args), callback=result_accumulator.update_results)

    pool.close()
    pool.join()

    print('results', result_accumulator.val)
    print('Execution took: ', time.time() - start_time, 'sec')

    return jsonify({'data': result_accumulator.val})


# driver function
if __name__ == '__main__':
    app.run(debug=True)
