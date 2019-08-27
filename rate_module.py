from datetime import datetime
import json
from urllib.parse import urlparse


def rate(url, status):
    write_data = []
    url = extract_domain(url)
    try:
        with open('rating.json') as json_file:
            data = json.load(json_file)
            for d in data:
                write_data.append({'url': d['url'], 'rating': d['rating'], 'date': d['date']})
        with open('rating.json', 'w') as tf:
            updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            write_data.append({'url': url, 'rating': status, 'date': updated})
            json.dump(write_data, tf, indent=2)
        tf.close()
        return True
    except Exception as e:
        print(e)
        return True


def extract_domain(url):
    parsed_uri = urlparse(url)
    result = '{uri.netloc}'.format(uri=parsed_uri)
    return result
